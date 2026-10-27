// Ranking checks against the real generated index. Run: node _build/tools/check_search.mjs
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const root = new URL('../../', import.meta.url);
const read = file => fs.readFileSync(new URL(file, root), 'utf8');
const api = vm.runInNewContext(read('assets/search-core.js') + '\nSiteSearch');
for (const lang of ['en', 'de']) {
  const items = JSON.parse(read(`assets/search-${lang}.json`)), records = api.prepare(items);
  for (const query of ['ai-1', '[ai-1]', 'AI-F12']) {
    assert.equal(api.rank(records, query)[0].item.anchor, query.toLowerCase().replace(/[\[\]]/g, ''));
  }
  assert.equal(api.rank(records, 'harness')[0].item.anchor, 'ai-2.4');
  assert.equal(api.rank(records, 'ESACA')[0].item.url, 'projects-esaca.html#esaca-1');
  assert.ok(api.rank(records, 'grammar masking').some(hit => hit.item.anchor === 'pub-NRR24'));
  assert.equal(api.rank(records, 'qzxv-nonexistent-937451').length, 0);
  assert.equal(api.rank(records, '<>').length, 0);
  assert.equal(api.normalize('Größe'), 'grosse');
  assert.equal(api.normalize('GRÖẞE'), 'grosse');
  assert.equal(JSON.stringify(api.ranges('Größe Straße', 'GROSSE strasse')), '[[0,5],[6,12]]');
  assert.equal(JSON.stringify(api.ranges('AI-1 & ai-1.2', '[ai-1]')), '[[0,4],[7,11]]');
  assert.equal(JSON.stringify(api.ranges('no match', '<>')), '[]');
  const typo = api.rank(records, 'harnses');
  assert.equal(typo[0].item.anchor, 'ai-2.4');
  assert.ok(typo[0].fuzzy.includes('harness'));
  const grouped = api.group(api.rank(records, 'harness'), records);
  assert.equal(grouped[0].item.anchor, 'ai-2.4');
  assert.ok(grouped[0].children.some(child => child.item.anchor === 'ai-f12'));
  assert.ok(grouped[0].related.length > 0);
  const primarySnippet = api.bestExcerpt(grouped[0], 'harness');
  assert.ok(primarySnippet.text.length > 80 && primarySnippet.text.length <= 284);
  assert.ok(primarySnippet.text.toLowerCase().includes('software'));
  const pageGroups = grouped.filter(hit => hit.item.kind !== 'publication' && !hit.exact).map(hit => hit.item.url.split('#')[0]);
  assert.equal(new Set(pageGroups).size, pageGroups.length);
  const exposed = grouped.flatMap(hit => [hit, ...(hit.children || []), ...hit.related.flatMap(unit => [unit, ...(unit.children || [])])]).map(hit => hit.item.url);
  assert.ok(api.rank(records, 'harness').every(hit => exposed.includes(hit.item.url)));
  assert.equal(api.group(api.rank(records, 'ai-f12'), records)[0].item.anchor, 'ai-f12');
  assert.ok(api.rank(records, 'barrierefreiheit').some(hit => hit.item.anchor === 'pub-BKM+25' && hit.abstractMatch));
  assert.ok(api.rank(records, 'wrapping effect').some(hit => hit.item.anchor === 'pub-Net15' && hit.abstractMatch));
  assert.equal(items.filter(item => item.abstract).length, 29);
  assert.ok(items.filter(item => item.abstract).every(item => item.kind === 'publication' && item.url.startsWith('research.html#pub-')));
  for (const item of items) assert.ok(api.excerpt(item.text, 'harness').length <= 224);
  console.log(`${lang}: references, field ranking, grouped figures, typos, synonyms, 29 own abstracts and excerpts passed`);
}

const fixture = api.prepare([
  {url:'word',title:'RAG',text:'Retrieval augmented generation',anchor:'one'},
  {url:'substring',title:'Frage',text:'Eine Frage beantworten',anchor:'two'},
]);
assert.equal(api.rank(fixture,'rag')[0].item.url,'word');
assert.ok(!api.rank(fixture,'rag').some(hit=>hit.item.url==='substring'));
const proximity = api.prepare([
  {url:'far',title:'Article',text:'alpha '+ 'unrelated '.repeat(60)+'beta',anchor:'far'},
  {url:'near',title:'Article',text:'alpha beta '+ 'unrelated '.repeat(60),anchor:'near'},
]);
assert.equal(api.rank(proximity,'alpha beta')[0].item.url,'near');
const passage='Alpha occurs here. '+ 'Unrelated background. '.repeat(18)+'A useful sentence brings alpha and beta together. More background.';
const snippet=api.excerpt(passage,'alpha beta');
assert.ok(snippet.includes('alpha') && snippet.includes('beta'));
assert.equal(snippet,'A useful sentence brings alpha and beta together.');
const primary={item:{url:'page#one',title:'Alpha beta',text:'Alpha is mentioned here.'},matchGroups:[['alpha'],['beta']],matchedTerms:['alpha'],related:[{item:{url:'page#two',text:'A precise sentence explains alpha and beta together.'},matchGroups:[['alpha'],['beta']],matchedTerms:['alpha','beta']}]};
const best=api.bestExcerpt(primary,'alpha beta');
assert.equal(best.item.url,'page#two');
assert.equal(best.text,'A precise sentence explains alpha and beta together.');
assert.ok(api.excerpt('The opening explanation is useful. Tiny.','absent').startsWith('The opening explanation is useful.'));
const definition='Model, harness, agent. A harness manages model calls, tool execution, context and permissions throughout an agent run.';
assert.ok(api.excerpt(definition,'harness').includes('manages model calls'));
console.log('Whole-word precision, proximity, page grouping, complete sentences and group-wide snippet checks passed');
