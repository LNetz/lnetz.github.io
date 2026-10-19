// Fetch Lukas' papers, their references (hop 1) and the references of those (hop 2) from OpenAlex.
// usage: node fetch_openalex.mjs <pubs.js> <outDir>
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
const [pubsFile, out] = process.argv.slice(2);
const window = {}; eval(readFileSync(pubsFile, "utf8"));
const PUBS = window.PUBS;
const API = "https://api.openalex.org";
const withKey = url => process.env.OPENALEX_KEY ? url + (url.includes("?") ? "&" : "?") + "api_key=" + process.env.OPENALEX_KEY : url;   // optional own budget
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function get(url) {
  for (let k = 0; k < 6; k++) {
    const r = await fetch(withKey(url));
    if (r.status === 429 || r.status >= 500) { await sleep(2000 * (k + 1)); continue; }
    await sleep(150);
    if (r.status === 404) return null;
    if (!r.ok) throw new Error(r.status + " " + url);
    return r.json();
  }
  throw new Error("gave up " + url);
}
const cache = async (name, fn) => { const f = join(out, name); if (existsSync(f)) return JSON.parse(readFileSync(f, "utf8")); const v = await fn(); writeFileSync(f, JSON.stringify(v)); return v; };
const SEL = "id,doi,title,publication_year,primary_location,authorships,cited_by_count,primary_topic,referenced_works,type";
const short = id => id.replace("https://openalex.org/", "");
// works by OpenAlex id, 50 per request
async function works(ids, select) {
  const res = [];
  for (let k = 0; k < ids.length; k += 50) {
    const j = await get(`${API}/works?filter=openalex_id:${ids.slice(k, k + 50).join("|")}&per-page=50&select=${select}`);
    res.push(...j.results);
    if (k % 1000 === 0) console.log("  works", k, "/", ids.length);
  }
  return res;
}
const norm = s => s.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
const own = await cache("own.json", async () => {
  const res = [];
  for (const p of PUBS) {
    let w = p.doi ? await get(`${API}/works/doi:${p.doi}?select=${SEL}`) : null;
    let how = "doi";
    if (!w) {
      const j = await get(`${API}/works?search=${encodeURIComponent(p.title.replace(/[:,?]/g, " "))}&per-page=5&select=${SEL}`);
      w = j?.results?.find(r => r.title && norm(r.title).startsWith(norm(p.title).slice(0, 40))) || null; how = "title";
    }
    console.log(p.key.padEnd(8), w ? `${how.padEnd(5)} refs ${String(w.referenced_works.length).padStart(3)}  ${w.title.slice(0, 60)}` : "MISSING " + p.title.slice(0, 60));
    res.push({ key: p.key, work: w });
  }
  return res;
});
const ownIds = new Set(own.filter(o => o.work).map(o => short(o.work.id)));
const ids1 = [...new Set(own.flatMap(o => o.work?.referenced_works || []).map(short))].filter(id => !ownIds.has(id));
console.log("own resolved", ownIds.size, "/", PUBS.length, "  hop-1 refs", ids1.length);
const hop1 = await cache("hop1.json", () => works(ids1, SEL));
const ids1set = new Set(ids1);
const count = new Map();
for (const w of hop1) for (const r of w.referenced_works.map(short)) if (!ids1set.has(r) && !ownIds.has(r)) count.set(r, (count.get(r) || 0) + 1);
const hist = {}; for (const c of count.values()) hist[Math.min(c, 10)] = (hist[Math.min(c, 10)] || 0) + 1;
console.log("hop-2 unique", count.size, "  by number of hop-1 papers citing them:", JSON.stringify(hist));
writeFileSync(join(out, "hop2_count.json"), JSON.stringify([...count]));
