// Refresh the citation map data, step by step. Run from anywhere:
//   node _build/citations/update.mjs              all steps, reusing what is cached in work/
//   node _build/citations/update.mjs --fresh      all steps, fetching everything anew
//   node _build/citations/update.mjs graph mini   only the named steps
// Steps: openalex pdfs crossref scholar graph citedby mini (in this order). See README.md.
// OPENALEX_KEY (environment) gives OpenAlex calls their own budget; without it the free budget is shared
// by everyone on the network and often used up. "citedby" needs it in practice.
import { execFileSync } from "node:child_process";
import { existsSync, rmSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "..", "..");
const work = join(here, "work");
const pubs = join(repo, "assets", "pubs.js");
const asset = f => join(repo, "assets", f);
const args = process.argv.slice(2);
const fresh = args.includes("--fresh");
const STEPS = ["openalex", "pdfs", "crossref", "scholar", "graph", "citedby", "mini"];
const want = args.filter(a => !a.startsWith("--"));
const steps = want.length ? STEPS.filter(s => want.includes(s)) : STEPS;

if (!existsSync(join(here, "node_modules", "pdfjs-dist"))) {
  console.error(`dependencies missing: run  cd "${here}" && npm install`);
  process.exit(1);
}
const run = (script, ...a) => {
  console.log(`\n> ${script} ${a.map(x => x.replace(repo, ".")).join(" ")}`);
  execFileSync(process.execPath, [join(here, script), ...a], { stdio: "inherit" });
};
const drop = (...files) => { for (const f of files) rmSync(join(work, f), { force: true }); };

for (const step of steps) {
  if (step === "openalex") {                          // my papers in OpenAlex + their reference lists
    if (fresh) drop("own.json", "hop1.json", "hop2_count.json");
    run("fetch_openalex.mjs", pubs, work);
  }
  if (step === "pdfs") run("fetch_pdfs.mjs", pubs, work, ...(fresh ? ["--fresh"] : []));
  if (step === "crossref") {                          // resolve PDF reference entries (resumable per paper)
    if (fresh) drop("pdf_cr.json");
    run("resolve_crossref.mjs", work);
  }
  if (step === "scholar") run("fetch_scholar.mjs", work);
  if (step === "graph") {                             // "cites" map -> assets/citations.js
    if (fresh) drop("oa_by_doi.json", "hop2_meta.json");
    run("build_graph.mjs", pubs, work, asset("citations.js"), "3");
  }
  if (step === "citedby") {                           // "cited by" map -> assets/citedby.js
    if (fresh) drop("citing1.json", "citing2.json");
    run("fetch_citedby.mjs", work);
    run("build_citedby.mjs", pubs, work, asset("citedby.js"), asset("citations.js"), "1");
  }
  if (step === "mini") run("build_mini.mjs", asset("citations.js"), asset("citedby.js"), asset("pubs-mini.js"));
}
console.log("\ndone. Next: regenerate the pages (python _build/build.py) and check the research page locally.");
