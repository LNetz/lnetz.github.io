// Fetch abstracts for OWN papers only, using existing verified IDs/DOIs. Never walks citations.
// node _build/tools/update_abstracts.mjs [--fresh] [paper-key ...]
import fs from 'node:fs';
import vm from 'node:vm';
const root = new URL('../../', import.meta.url);
const path = name => new URL(name, root);
const read = name => JSON.parse(fs.readFileSync(path(name), 'utf8'));
const ctx = { window: {} };
vm.runInNewContext(fs.readFileSync(path('assets/pubs.js'), 'utf8'), ctx);
const papers = ctx.window.PUBS;
const own = new Map(read('_build/citations/work/own.json').map(p => [p.key, p.work]));
const destination = '_build/paper-abstracts.json';
const cache = fs.existsSync(path(destination)) ? read(destination) : { papers: {} };
const args = process.argv.slice(2), fresh = args.includes('--fresh'), keys = args.filter(a => !a.startsWith('--'));
const norm = value => (value || '').toLowerCase().replace(/[^a-z0-9]/g, '');
const doi = value => (value || '').replace(/^https?:\/\/(?:dx\.)?doi.org\//i, '').toLowerCase();
function reconstruct(inverted) {
  if (!inverted) return '';
  const words = [];
  for (const [word, positions] of Object.entries(inverted)) for (const position of positions) words[position] = word;
  return words.join(' ').replace(/\s+/g, ' ').trim();
}
async function fetchAbstract(paper) {
  const old = cache.papers[paper.key];
  if (old?.reviewed && old.title === paper.title) return; // Preserve reviewed PDF excerpts, including on --fresh.
  if (!fresh && old?.abstract && old.title === paper.title) return;
  const mapped = own.get(paper.key);
  const id = mapped?.id?.split('/').at(-1) || (paper.doi ? `doi:${paper.doi}` : '');
  if (!id) {
    cache.papers[paper.key] = { title: paper.title, status: 'no-metadata-id' };
    console.log(paper.key, 'no metadata ID; PDF/manual source needed');
    return;
  }
  const url = `https://api.openalex.org/works/${id}?select=id,doi,display_name,abstract_inverted_index`;
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(20000) });
    if (response.status === 404) { cache.papers[paper.key] = { title: paper.title, status: 'not-found' }; return; }
    if (!response.ok) throw Error(`HTTP ${response.status}`);
    const work = await response.json();
    const sameDOI = paper.doi && doi(paper.doi) === doi(work.doi);
    if (!sameDOI && norm(work.display_name) !== norm(paper.title)) throw Error('title/DOI identity mismatch');
    const abstract = reconstruct(work.abstract_inverted_index);
    cache.papers[paper.key] = { title: paper.title, status: abstract ? 'available' : 'no-abstract',
      ...(abstract ? { abstract, language: 'en', source: work.id, sourceType: 'OpenAlex', retrieved: new Date().toISOString().slice(0, 10) } : {}) };
    console.log(paper.key, abstract ? `${abstract.split(/\s+/).length} words` : 'no abstract in metadata');
  } catch (error) {
    console.log(paper.key, 'FAILED:', error.message);
    if (!old) cache.papers[paper.key] = { title: paper.title, status: 'fetch-failed' };
  }
}
const queue = papers.filter(p => !keys.length || keys.includes(p.key));
// Small, bounded concurrency. These are free single-work lookups, not paid list/search queries.
for (let i = 0; i < queue.length; i += 3) await Promise.all(queue.slice(i, i + 3).map(fetchAbstract));
const ownKeys = new Set(papers.map(p => p.key));
cache.papers = Object.fromEntries(Object.entries(cache.papers).filter(([key]) => ownKeys.has(key)));
fs.writeFileSync(path(destination), JSON.stringify(cache, null, 2) + '\n');
console.log('Coverage:', Object.values(cache.papers).filter(p => p.abstract).length, '/', papers.length);
