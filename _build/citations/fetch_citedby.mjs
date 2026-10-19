// Who cites me: works citing my papers (hop 1) and works citing those (hop 2), from OpenAlex (cites: filter,
// up to 50 ids per query, cursor paging). Cached per step. usage: node fetch_citedby.mjs <workDir>
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
const dir = process.argv[2];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const short = id => id.replace("https://openalex.org/", "");
const SEL = "id,doi,title,publication_year,primary_location,authorships,cited_by_count,primary_topic,referenced_works,type";
let calls = 0, cost = 0;
async function citing(ids) {                          // all works citing any of ids
  const out = [];
  for (let k = 0; k < ids.length; k += 50) {
    let cursor = "*";
    while (cursor) {
      const url = `https://api.openalex.org/works?filter=cites:${ids.slice(k, k + 50).join("|")}&per-page=200&cursor=${encodeURIComponent(cursor)}&select=${SEL}` + (process.env.OPENALEX_KEY ? `&api_key=${process.env.OPENALEX_KEY}` : "");
      let j = null;
      for (let a = 0; a < 5 && !j; a++) {
        const r = await fetch(url); calls++;
        cost += +(r.headers.get("x-ratelimit-cost-usd") || 0);
        if (r.status === 429 && /budget/i.test(await r.clone().text())) { console.log("budget used up after", calls, "calls"); process.exit(3); }
        if (r.ok) j = await r.json(); else await sleep(2000 * (a + 1));
      }
      if (!j) throw new Error("failed " + url);
      out.push(...j.results);
      cursor = j.meta.next_cursor;
      await sleep(150);
    }
  }
  return out;
}
const own = JSON.parse(readFileSync(join(dir, "own.json"), "utf8")).filter(o => o.work).map(o => short(o.work.id));
const f1 = join(dir, "citing1.json");
const c1 = existsSync(f1) ? JSON.parse(readFileSync(f1, "utf8")) : await citing(own);
writeFileSync(f1, JSON.stringify(c1));
const ids1 = [...new Set(c1.map(w => short(w.id)))].filter(id => !own.includes(id));
console.log("my papers in OpenAlex:", own.length, " citing works (hop 1):", ids1.length, " calls so far", calls);
const f2 = join(dir, "citing2.json");
const c2 = existsSync(f2) ? JSON.parse(readFileSync(f2, "utf8")) : await citing(ids1);
writeFileSync(f2, JSON.stringify(c2));
const set1 = new Set([...ids1, ...own]);
const count = new Map();
for (const w of c2) { const id = short(w.id); if (set1.has(id)) continue; const n = w.referenced_works.map(short).filter(r => set1.has(r) && !own.includes(r)).length; count.set(id, Math.max(count.get(id) || 0, n)); }
const hist = {}; for (const c of count.values()) hist[Math.min(c, 8)] = (hist[Math.min(c, 8)] || 0) + 1;
console.log("hop 2 works:", count.size, " by number of hop-1 works they cite:", JSON.stringify(hist));
console.log("calls", calls, "cost $" + cost.toFixed(4));
