// Extract candidate front-matter text for OWN papers missing a metadata abstract.
// Candidates require review; this command never invents or automatically publishes an abstract.
import fs from 'node:fs';
import vm from 'node:vm';
import { getDocument } from '../citations/node_modules/pdfjs-dist/legacy/build/pdf.mjs';
const root = new URL('../../', import.meta.url), path = name => new URL(name, root);
const ctx = { window: {} }; vm.runInNewContext(fs.readFileSync(path('assets/pubs.js'), 'utf8'), ctx);
const papers = ctx.window.PUBS, cache = JSON.parse(fs.readFileSync(path('_build/paper-abstracts.json')));
const overrides = JSON.parse(fs.readFileSync(path('_build/citations/work/pdf_sources.json')));
fs.mkdirSync(path('_build/search-work/'), { recursive: true });
const selected = process.argv.slice(2).filter(arg => !arg.startsWith('--'));
const forceColumns = process.argv.includes('--two-columns');
for (const paper of papers) {
  if (cache.papers[paper.key]?.abstract || (selected.length && !selected.includes(paper.key))) continue;
  const source = overrides[paper.key] || paper.pdf;
  if (!source) { console.log(paper.key, 'no public PDF'); continue; }
  const pdfPath = path(`_build/search-work/${paper.key}.pdf`);
  const existing = path(`_build/citations/work/pdfs/${paper.key}.pdf`);
  try {
    if (!fs.existsSync(pdfPath) && !fs.existsSync(existing)) {
      const response = await fetch(source, { signal: AbortSignal.timeout(45000) });
      if (!response.ok) throw Error(`HTTP ${response.status}`);
      const bytes = Buffer.from(await response.arrayBuffer());
      if (bytes.subarray(0, 4).toString() !== '%PDF') throw Error('not a PDF');
      fs.writeFileSync(pdfPath, bytes);
    }
    const doc = await getDocument({ data: new Uint8Array(fs.readFileSync(fs.existsSync(existing) ? existing : pdfPath)), verbosity: 0 }).promise;
    const pages = [];
    for (let p = 1; p <= Math.min(12, doc.numPages); p++) {
      const page = await doc.getPage(p), content = await page.getTextContent();
      const items = content.items.filter(i => i.str?.trim()), width = page.view[2];
      const twoColumns = forceColumns || (items.filter(i => i.transform[4] > width * .52).length > items.length * .3 &&
        items.filter(i => i.transform[4] < width * .45).length > items.length * .3);
      const columns = twoColumns ? [items.filter(i => i.transform[4] < width * .5), items.filter(i => i.transform[4] >= width * .5)] : [items];
      const texts = columns.map(column => {
        const lines = new Map();
        for (const item of column) {
          const y = Math.round(item.transform[5]);
          const key = [...lines.keys()].find(k => Math.abs(y - k) < 3) ?? y;
          if (!lines.has(key)) lines.set(key, []);
          lines.get(key).push(item);
        }
        return [...lines.keys()].sort((a, b) => b - a).map(y => lines.get(y)
          .sort((a, b) => a.transform[4] - b.transform[4]).map(i => i.str).join(' ')).join('\n');
      });
      pages.push({ page: p, text: texts.join('\n') });
    }
    await doc.destroy();
    fs.writeFileSync(path(`_build/search-work/${paper.key}.json`), JSON.stringify({ title: paper.title, source, pages }, null, 2));
    const abstractPage = pages.find(p => /\babstract\b/i.test(p.text)) || pages.find(p => /\b(kurzfassung|zusammenfassung)\b/i.test(p.text));
    console.log(paper.key, pages.length, 'pages extracted;', abstractPage ? `abstract heading on page ${abstractPage.page}` : 'no abstract heading found');
  } catch (error) { console.log(paper.key, 'FAILED:', error.message); }
}
