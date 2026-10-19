// Citation counts of my papers from my public Google Scholar profile: ONE request, allowed by Scholar's
// robots.txt ("Allow: /citations?user="; note "Disallow: /citations?*cstart=" — never add cstart).
// Never crawl Scholar search or "cited by" pages (disallowed). usage: node fetch_scholar.mjs <workDir>
import { writeFileSync } from "node:fs";
import { join } from "node:path";

const dir = process.argv[2];
const URL = "https://scholar.google.com/citations?user=5mVkoWsAAAAJ&hl=en&pagesize=100";
const r = await fetch(URL, { headers: { "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36" } });
const h = await r.text();
const rows = [...h.matchAll(/<tr class="gsc_a_tr">([\s\S]*?)<\/tr>/g)].map(m => {
  const row = m[1];
  const t = (row.match(/class="gsc_a_at"[^>]*>([^<]*)/) || [])[1];
  return {
    t: t && t.replace(/&amp;/g, "&").replace(/&#39;/g, "'"),
    c: +((row.match(/class="gsc_a_ac gs_ibl"[^>]*>([^<]*)/) || [])[1]) || 0,
    y: (row.match(/gsc_a_h gsc_a_hc gs_ibl">([^<]*)/) || [])[1],
    cites: (row.match(/cites=([0-9,]+)/) || [])[1],
  };
});
// the profile's totals (citations, h-index, i10-index — "All" column) for the METRICS block in _build/build.py
const stats = [...h.matchAll(/<td class="gsc_rsb_std">(\d+)<\/td>/g)].map(m => +m[1]);
if (!rows.length) { console.log("no rows — Scholar answered", r.status, "(captcha?). Keep the old work/scholar.json."); process.exit(1); }
writeFileSync(join(dir, "scholar.json"), JSON.stringify(rows));
console.log(rows.length, "papers on the profile");
if (stats.length >= 6) console.log(`totals (all time): citations ${stats[0]}, h-index ${stats[2]}, i10-index ${stats[4]}  -> update METRICS in _build/build.py`);
