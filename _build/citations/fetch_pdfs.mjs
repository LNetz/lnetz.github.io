// Download the PDF of each of my papers and read its reference list (work/pdfrefs/<key>.json).
// Source: work/pdf_sources.json if listed there, else the pdf link in assets/pubs.js.
// Existing reference lists are kept unless --fresh. usage: node fetch_pdfs.mjs <pubs.js> <workDir> [--fresh] [keys...]
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const [pubsFile, dir, ...rest] = process.argv.slice(2);
const fresh = rest.includes("--fresh"), only = rest.filter(a => !a.startsWith("--"));
const window = {}; eval(readFileSync(pubsFile, "utf8"));
const sources = existsSync(join(dir, "pdf_sources.json")) ? JSON.parse(readFileSync(join(dir, "pdf_sources.json"), "utf8")) : {};
mkdirSync(join(dir, "pdfs"), { recursive: true });
mkdirSync(join(dir, "pdfrefs"), { recursive: true });
const here = dirname(fileURLToPath(import.meta.url));

for (const p of window.PUBS) {
  if (only.length && !only.includes(p.key)) continue;
  const url = sources[p.key] || p.pdf;
  const refs = join(dir, "pdfrefs", p.key + ".json");
  if (!url) { console.log(p.key.padEnd(8), "no PDF (references come from OpenAlex only)"); continue; }
  if (existsSync(refs) && !fresh) { console.log(p.key.padEnd(8), "kept"); continue; }
  const pdf = join(dir, "pdfs", p.key + ".pdf");
  if (!existsSync(pdf) || fresh) {
    const r = await fetch(url, { headers: { "user-agent": "Mozilla/5.0 (citation-map-pipeline)" } });
    const buf = Buffer.from(await r.arrayBuffer());
    if (!r.ok || buf.subarray(0, 4).toString() !== "%PDF") { console.log(p.key.padEnd(8), "download failed", r.status, url); continue; }
    writeFileSync(pdf, buf);
  }
  const out = execFileSync(process.execPath, [join(here, "pdf_refs.mjs"), pdf], { maxBuffer: 64 << 20 }).toString();
  writeFileSync(refs, out);
  const n = JSON.parse(out).n;
  console.log(p.key.padEnd(8), n, "references", n < 5 ? "  <- check: scanned PDF or broken fonts? add a better source to pdf_sources.json" : "");
}
