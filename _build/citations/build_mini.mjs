// Per-paper summary for the mini graphs in the publication list: the topics of what each of my papers
// cites and of what cites it, my own papers marked. usage: node build_mini.mjs <citations.js> <citedby.js> <out> [keys...]
import { readFileSync, writeFileSync } from "node:fs";
const [refF, inF, outF, ...only] = process.argv.slice(2);
const w = {};
eval(readFileSync(refF, "utf8").replace("window.GRAPH", "w.out"));
eval(readFileSync(inF, "utf8").replace("window.GRAPH_IN", "w.in"));
const CODE = { llm: "l", mde: "m", eis: "e", twin: "t", a11y: "a", ga: "g", other: "o" };
const ORDER = "mettalgo";                              // grouped by topic, in the legend's order
const sortT = s => [...s].sort((a, b) => "lmetago".indexOf(a) - "lmetago".indexOf(b)).join("");
const summary = (G, key, dir) => {
  const i = G.nodes.findIndex(n => n.k === key);
  if (i < 0) return { t: "", own: [] };
  const nb = G.links.filter(([a, b]) => dir === "out" ? a === i : b === i).map(([a, b]) => G.nodes[dir === "out" ? b : a]);
  const own = nb.filter(n => n.h === 0).map(n => n.k);
  return { t: sortT(nb.filter(n => n.h !== 0).map(n => CODE[n.g] || "o").join("")), own };
};
const out = {};
for (const n of w.out.nodes.filter(n => n.h === 0)) {
  if (only.length && !only.includes(n.k)) continue;
  const r = summary(w.out, n.k, "out"), c = summary(w.in, n.k, "in");
  out[n.k] = { r: r.t, ro: r.own, c: c.t, co: c.own };
}
writeFileSync(outF, "// Mini graphs in the publication list: per paper the topics of what it cites (r) and of what cites it (c),\n// my own papers among them by key (ro, co). Generated from citations.js / citedby.js.\nwindow.PUBS_MINI = " + JSON.stringify(out) + ";\n");
for (const [k, v] of Object.entries(out)) console.log(k.padEnd(8), "cites", v.r.length, "+ own", v.ro.length, "| cited by", v.c.length, "+ own", v.co.length);
