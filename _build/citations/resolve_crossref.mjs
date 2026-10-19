// Resolve PDF reference strings with Crossref's bibliographic search (no daily budget).
// A hit counts only if its title appears in the reference text. Resumable per paper.
// usage: node resolve_crossref.mjs <workDir>   (reads pdfrefs/*.json, writes pdf_cr.json)
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
const dir = process.argv[2];
const outF = join(dir, "pdf_cr.json");
const res = existsSync(outF) ? JSON.parse(readFileSync(outF, "utf8")) : {};
const sleep = ms => new Promise(r => setTimeout(r, ms));
const norm = s => (s || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/-\s+/g, "").replace(/[^a-z0-9]+/g, " ").trim();
const squash = s => norm(s).replace(/ /g, "");
const contains = (entry, title) => { const t = squash(title); return t.length >= 18 && squash(entry).includes(t); };
async function get(url) {
  for (let k = 0; k < 5; k++) {
    try { const r = await fetch(url, { headers: { "user-agent": "research-map-builder/1.0" } }); if (r.status === 429 || r.status >= 500) { await sleep(3000 * (k + 1)); continue; } await sleep(80); return r.ok ? r.json() : null; }
    catch { await sleep(2000); }
  }
  return null;
}
for (const f of readdirSync(join(dir, "pdfrefs")).filter(f => f.endsWith(".json"))) {
  const key = f.replace(/\.json$/, "");
  if (res[key]) continue;
  const { entries } = JSON.parse(readFileSync(join(dir, "pdfrefs", f), "utf8"));
  const out = [];
  for (const e of entries) {
    const q = e.replace(/^\[[^\]]{1,30}\]\s*/, "").replace(/https?:\S+/g, "").slice(0, 300);
    const j = await get(`https://api.crossref.org/works?query.bibliographic=${encodeURIComponent(q)}&rows=3&select=DOI,title,author,issued,container-title,is-referenced-by-count,type`);
    const hit = j?.message?.items?.find(it => it.title?.[0] && contains(e, it.title[0])) || null;
    out.push({ text: e, hit: hit && {
      doi: hit.DOI.toLowerCase(), t: hit.title[0], y: hit.issued?.["date-parts"]?.[0]?.[0] || null,
      v: hit["container-title"]?.[0] || "", c: hit["is-referenced-by-count"] || 0,
      a: (hit.author || []).map(a => [a.given, a.family].filter(Boolean).join(" ")),
    } });
  }
  res[key] = out;
  writeFileSync(outF, JSON.stringify(res));
  console.log(key.padEnd(8), "crossref", out.filter(o => o.hit).length, "/", out.length);
}
