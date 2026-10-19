// Resolve PDF reference strings to OpenAlex works. A hit counts only if its title appears in the reference text.
// usage: node resolve_openalex.mjs <workDir>   (reads pdfrefs/*.json, writes pdf_resolved.json; resumable)
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
const dir = process.argv[2];
const outF = join(dir, "pdf_resolved.json");
const res = existsSync(outF) ? JSON.parse(readFileSync(outF, "utf8")) : {};
const withKey = url => process.env.OPENALEX_KEY ? url + (url.includes("?") ? "&" : "?") + "api_key=" + process.env.OPENALEX_KEY : url;   // optional own budget
const sleep = ms => new Promise(r => setTimeout(r, ms));
const SEL = "id,doi,title,publication_year,primary_location,authorships,cited_by_count,primary_topic,referenced_works,type";
async function get(url) {
  for (let k = 0; k < 6; k++) {
    try { const r = await fetch(withKey(url)); if (r.status === 429 && /budget/i.test(await r.clone().text())) { console.error("OpenAlex daily budget used up - stopping"); process.exit(3); } if (r.status === 429 || r.status >= 500) { await sleep(2000 * (k + 1)); continue; } await sleep(120); return r.ok ? r.json() : null; }
    catch { await sleep(2000); }
  }
  return null;
}
const norm = s => (s || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/-\s+/g, "").replace(/[^a-z0-9]+/g, " ").trim();
const squash = s => norm(s).replace(/ /g, "");
const contains = (entry, title) => { const t = squash(title); return t.length >= 18 && squash(entry).includes(t); };
function guessTitle(e) {
  e = e.replace(/^\[[^\]]{1,30}\]\s*|^\d{1,3}\.\s/, "");
  let m = e.match(/[“"](.{12,}?)[,.]?[”"]/); if (m) return m[1];
  m = e.match(/\(\d{4}[a-z]?\)\.?\s*(.{12,}?)[.?!](\s|$)/); if (m) return m[1];
  m = e.match(/\.\s\d{4}[a-z]?\.\s(.{12,}?)[.?!](\s|$)/); if (m) return m[1];
  m = e.match(/:\s(.{12,}?)[.?!]\s(In\b|In:|Proc|Springer|IEEE|ACM|Journal|arXiv|\d|[A-Z])/); if (m) return m[1];
  m = e.match(/^(?:[^,]+,){1,12}?\s*([A-Z][^,]{20,}?),\s/); if (m) return m[1];
  return null;
}
const files = readdirSync(join(dir, "pdfrefs")).filter(f => f.endsWith(".json"));
for (const f of files) {
  const key = f.replace(/\.json$/, "");
  if (res[key]) continue;
  const { entries } = JSON.parse(readFileSync(join(dir, "pdfrefs", f), "utf8"));
  const out = [];
  for (const e of entries) {
    let work = null, how = null;
    const doi = e.replace(/\s+/g, "").match(/10\.\d{4,9}\/[^\s,;]+?(?=\.?$|\.?(https?:|www\.|\(|Accessed))/i)?.[0] || e.match(/doi(?:\.org\/|:\s?)(10\.\d{4,9}\/[^\s,;]+)/i)?.[1];
    if (doi) { work = await get(`https://api.openalex.org/works/doi:${doi.replace(/\.$/, "")}?select=${SEL}`); if (work) how = "doi"; }
    const title = guessTitle(e);
    if (!work && title) {
      const j = await get(`https://api.openalex.org/works?filter=title.search:${encodeURIComponent(title.replace(/[,:|!?()]/g, " "))}&per-page=5&select=${SEL}`);
      work = j?.results?.find(w => contains(e, w.title)) || null; if (work) how = "title";
    }
    if (!work) {
      const q = e.replace(/^\[[^\]]{1,30}\]\s*/, "").replace(/https?:\S+|doi:\S+/g, "").replace(/[,:|!?()“”"]/g, " ").slice(0, 250);
      const j = await get(`https://api.openalex.org/works?search=${encodeURIComponent(q)}&per-page=5&select=${SEL}`);
      work = j?.results?.find(w => contains(e, w.title)) || null; if (work) how = "search";
    }
    out.push({ text: e, title, how, work });
  }
  res[key] = out;
  writeFileSync(outF, JSON.stringify(res));
  console.log(key.padEnd(8), "resolved", out.filter(o => o.work).length, "/", out.length, " (doi", out.filter(o => o.how === "doi").length, ", title", out.filter(o => o.how === "title").length, ", search", out.filter(o => o.how === "search").length, ")");
}
