// The other direction: who cites my papers (hop 1) and who cites those (hop 2); same look and layouts.
// usage: node build_citedby.mjs <pubs.js> <graphDir> <out citedby.js> <reference graph citations.js> [hop2 min]
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { forceSimulation, forceLink, forceManyBody, forceCollide, forceX, forceY, forceZ } from "d3-force-3d";

const [pubsFile, dir, outFile, refGraphFile, minArg] = process.argv.slice(2);
const HOP2_MIN = +(minArg || 1);
const window = {}; eval(readFileSync(pubsFile, "utf8"));
const PUBS = window.PUBS;
const J = f => JSON.parse(readFileSync(join(dir, f), "utf8"));
const own = J("own.json"), hop1oa = J("hop1.json");
const pdf = existsSync(join(dir, "pdf_resolved.json")) ? J("pdf_resolved.json") : {};
const SEL = "id,doi,title,publication_year,primary_location,authorships,cited_by_count,primary_topic,referenced_works,type";
const short = id => id.replace("https://openalex.org/", "");
const norm = s => (s || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
const sleep = ms => new Promise(r => setTimeout(r, ms));
let budgetGone = false;
// OpenAlex single-work lookups: free (only list/filter queries draw on the daily budget). A few in parallel,
// politely paced; into(work, value) gets each hit, misses are simply skipped.
async function oaBatch(kind, values, select, into) {
  const path = v => kind === "doi" ? `doi:${v}` : v;
  let next = 0, done = 0;
  const worker = async () => {
    while (next < values.length) {
      const v = values[next++];
      for (let a = 0; a < 4; a++) {
        try {
          const r = await fetch(`https://api.openalex.org/works/${path(v)}?select=${select}`);
          if (r.ok) { into(await r.json(), v); break; }
          if (r.status === 404) break;
        } catch (_) {}
        await sleep(1500 * (a + 1));
      }
      if (++done % 200 === 0) console.log(`  ${kind}: ${done} / ${values.length}`);
      await sleep(180);
    }
  };
  await Promise.all([worker(), worker(), worker(), worker()]);
}
const cr = existsSync(join(dir, "pdf_cr.json")) ? J("pdf_cr.json") : {};

// ---------- topics: own papers from their tags, everything else from title + OpenAlex topic ----------
const RULES = [
  ["a11y", /accessib|visual(ly)? impair|blind|disabilit|screen reader|inclusive|assistive|older adults|elderly|wcag/],
  ["llm", /language model|\bllms?\b|gpt|chatgpt|transformer|prompt|retrieval augmented|\brag\b|bert|few shot|in context learning|code generation with|neural|machine learning|deep learning|copilot|codex|natural language/],
  ["twin", /digital twin|cyber physical|internet of production|\biot\b|industry 4 0|manufactur|wind turbine|aircraft|avionic|flight|sysml|systems engineering|automotive/],
  ["ga", /genetic algorithm|evolutionary|hybrid electric|energy management|control strateg|vehicle|battery|reinforcement|optimi[sz]ation/],
  ["eis", /information system|enterprise|web application|graphical user interface|\bgui\b|user interface|low code|e government|public sector|business process|erp|financial|management system/],
  ["mde", /model driven|model based|\bmde\b|\bmdse\b|\buml\b|domain specific|\bdsls?\b|metamodel|meta model|code generat|generator|modeling|modelling|ocl|grammar|language workbench|monticore|model transformation|class diagram|software language/],
];
const topicOf = (title, oaTopic) => {
  const t = norm(title) + " " + norm(oaTopic);
  for (const [k, re] of RULES) if (re.test(t)) return k;
  return "other";
};
const OWN_ORDER = ["a11y", "llm", "twin", "ga", "eis", "mde"];
const ownTopic = tags => OWN_ORDER.find(t => tags.includes(t)) || "mde";

// ---------- SE (RWTH Software Engineering, Rumpe's chair) ----------
const SE_NAMES = /rumpe|judith michael|lukas netz|kirchhof|wortmann|gerasimov|ringert|krahn|grönniger|gronniger|haber|look,?\s|plotnikov|heithoff|buschhaus|drux|kautz|varga|adam,? k|kai adam/i;
const isSE = names => SE_NAMES.test(names);

// words split at a line break in the PDF ("In- vestigating"); real compounds keep their hyphen
const KEEP = /^(driven|based|specific|aware|oriented|level|time|world|scale|source|end|art|the|to|of|in|on|code|free|agnostic|intensive|critical|centric|enabled|grained|like|tuning|shot|step|order)/;
const dehyph = s => s.replace(/(\p{L})-\s?(\p{Ll}+)/gu, (m, a, b) => KEEP.test(b) ? a + "-" + b : a + b);

// ---------- node records ----------
const nodes = new Map();          // id -> node
const edges = new Set();          // "a>b" (a cites b)
const authorsShort = w => {
  const a = (w.authorships || []).map(x => x.author?.display_name).filter(Boolean);
  return a.length > 3 ? a.slice(0, 3).join(", ") + " et al." : a.join(", ");
};
const allAuthors = w => (w.authorships || []).map(x => x.author?.display_name).join("; ");
function fromWork(w, hop) {
  return {
    id: short(w.id), hop, t: w.title || "", yr: w.publication_year || null,
    v: w.primary_location?.source?.display_name || "", a: authorsShort(w), c: w.cited_by_count || 0,
    g: topicOf(w.title, w.primary_topic?.display_name), se: isSE(allAuthors(w)),
    d: w.doi ? w.doi.replace("https://doi.org/", "") : null, refs: (w.referenced_works || []).map(short),
  };
}
const add = n => { const o = nodes.get(n.id); if (!o || o.hop > n.hop) nodes.set(n.id, o ? { ...o, ...n, refs: o.refs.length ? o.refs : n.refs } : n); return nodes.get(n.id); };

// own papers
const ownNodes = [];
for (const p of PUBS) {
  const o = own.find(x => x.key === p.key);
  const w = o?.work;
  const n = {
    id: w ? short(w.id) : "P:" + p.key, hop: 0, key: p.key, t: p.title, yr: p.year, v: p.venue, a: p.authors,
    c: w?.cited_by_count || 0, g: ownTopic(p.tags), se: true, d: p.doi || null, u: p.url || null, pdf: p.pdf || null,
    refs: (w?.referenced_works || []).map(short),
  };
  nodes.set(n.id, n); ownNodes.push(n);
}
const ownIds = new Set(ownNodes.map(n => n.id));
if (existsSync(join(dir, "scholar.json"))) {
  const sq = s => (s || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "");
  const S = J("scholar.json");
  for (const n of ownNodes) {
    const k = sq(n.t).slice(0, 40);
    const hits = S.filter(r => r.t && (sq(r.t).startsWith(k) || k.startsWith(sq(r.t).slice(0, 40))));
    if (hits.length) {                                // duplicates on Scholar: the entry with the larger count
      const best = hits.reduce((a, b) => (b.c > a.c ? b : a));
      n.c = best.c; n.cs = true; n.gs = best.cites || null;
    }
  }
}
// ---------- who cites me: works citing my papers (hop 1) and works citing those (hop 2) ----------
const c1 = J("citing1.json"), c2 = J("citing2.json");
const ownByOa = new Map(ownNodes.filter(n => !n.id.startsWith("P:")).map(n => [n.id, n]));
for (const w of c1) { const id = short(w.id); if (!ownByOa.has(id)) add(fromWork(w, 1)); }
const set1 = new Set([...nodes.values()].filter(n => n.hop === 1).map(n => n.id));
for (const w of c1) {
  const id = short(w.id);
  if (ownByOa.has(id)) continue;
  for (const r of w.referenced_works.map(short)) if (r !== id && (ownByOa.has(r) || set1.has(r))) edges.add(id + ">" + r);
}
// my papers citing each other: taken from the reference map (read from the papers' own reference lists)
const refWin = {}; eval(readFileSync(refGraphFile, "utf8").replace("window.GRAPH", "refWin.G"));
const keyId = new Map(ownNodes.map(n => [n.key, n.id]));
for (const [a, b] of refWin.G.links) {
  const A = refWin.G.nodes[a], B = refWin.G.nodes[b];
  if (A.h === 0 && B.h === 0 && keyId.has(A.k) && keyId.has(B.k)) edges.add(keyId.get(A.k) + ">" + keyId.get(B.k));
}
// second hop: everything citing a first-hop work
let hop2n = 0;
for (const w of c2) {
  const id = short(w.id);
  if (nodes.has(id)) continue;
  const cites = [...new Set(w.referenced_works.map(short))].filter(r => set1.has(r));
  if (cites.length < HOP2_MIN) continue;
  add({ ...fromWork(w, 2), refs: [], n1: cites.length }); hop2n++;
  for (const r of cites) edges.add(id + ">" + r);
}

// ---------- layout (static, computed once) ----------
const list = [...nodes.values()];
const index = new Map(list.map((n, i) => [n.id, i]));
const links = [...edges].map(e => e.split(">")).filter(([a, b]) => index.has(a) && index.has(b)).map(([a, b]) => ({ source: index.get(a), target: index.get(b) }));
const R = n => n.hop === 0 ? 7 : n.hop === 1 ? 2 + 1.1 * Math.log10(1 + n.c) : 1.4 + 0.7 * Math.log10(1 + n.c);
list.forEach(n => { n.r = +R(n).toFixed(2); });
// two static layouts from the same forces: flat (2D) and a ball (3D), each started on a Fibonacci spiral/ball
// 2D groups by topic: every topic gets an anchor; my papers are drawn firmly to theirs, the works they
// cite gently to their own topic's — so each paper's star splits into topic sub-clusters
const TOPIC_ORDER = ["mde", "eis", "twin", "llm", "a11y", "ga", "other"];
const ANCHOR_R = 260;
const anchor = g => { const a = TOPIC_ORDER.indexOf(g) / TOPIC_ORDER.length * 2 * Math.PI - Math.PI / 2; return [Math.cos(a) * ANCHOR_R, Math.sin(a) * ANCHOR_R]; };
function layout(dims) {
  const ns = list.map((n, i) => {
    const t = Math.acos(1 - 2 * (i + 0.5) / list.length), p = i * 2.39996;
    const o = { hop: n.hop, r: n.r, g: n.g };
    if (dims === 2) { const [ax, ay] = anchor(n.g), rr = 3 * Math.sqrt(i + 1); o.x = ax + rr * Math.cos(p); o.y = ay + rr * Math.sin(p); }
    else { const rr = 14 * Math.cbrt(i + 1); o.x = rr * Math.sin(t) * Math.cos(p); o.y = rr * Math.sin(t) * Math.sin(p); o.z = rr * Math.cos(t); }
    return o;
  });
  const ls = links.map(l => ({ source: l.source, target: l.target }));
  const sim = forceSimulation(ns, dims);
  if (dims === 2) {
    sim.force("link", forceLink(ls).distance(l => l.source.hop === 0 && l.target.hop === 0 ? 90 : (l.source.hop === 0 || l.target.hop === 0) ? 34 : l.target.hop === 2 ? 22 : 30)
        .strength(l => l.source.hop === 0 && l.target.hop === 0 ? 0.02 : (l.source.hop === 0 || l.target.hop === 0) ? 0.12 : l.target.hop === 2 ? 0.06 : 0.015))
      .force("charge", forceManyBody().strength(n => n.hop === 0 ? -260 : n.hop === 1 ? -9 : -4).distanceMax(260))
      .force("collide", forceCollide(n => n.r + (n.hop === 0 ? 6 : 1.4)))
      .force("x", forceX(n => anchor(n.g)[0]).strength(n => n.hop === 0 ? 0.09 : 0.035))
      .force("y", forceY(n => anchor(n.g)[1]).strength(n => n.hop === 0 ? 0.09 : 0.035));
  } else {
    sim.force("link", forceLink(ls).distance(l => (l.source.hop === 0 || l.target.hop === 0) ? 70 : l.target.hop === 2 ? 28 : 45)
        .strength(l => (l.source.hop === 0 || l.target.hop === 0) ? 0.08 : l.target.hop === 2 ? 0.05 : 0.02))
      .force("charge", forceManyBody().strength(n => n.hop === 0 ? -900 : n.hop === 1 ? -26 : -10).distanceMax(600))
      .force("collide", forceCollide(n => n.r + 1.2))
      .force("x", forceX(0).strength(0.02)).force("y", forceY(0).strength(0.02)).force("z", forceZ(0).strength(0.02));
  }
  sim.stop();
  for (let k = 0; k < 900; k++) sim.tick();
  return ns;
}
const flat = layout(2), ball = layout(3);
// papers without any link are pushed far out by the repulsion and would only inflate the frame:
// bring them back to the rim of the connected cloud
const degree = new Array(list.length).fill(0);
for (const l of links) { degree[l.source]++; degree[l.target]++; }
for (const ns of [flat, ball]) {
  const d = ["x", "y", "z"].filter(k => ns[0][k] !== undefined);
  const mid = d.map(k => ns.reduce((s, n) => s + n[k], 0) / ns.length);
  const dist = n => Math.hypot(...d.map((k, j) => n[k] - mid[j]));
  const rim = ns.filter((n, i) => degree[i]).map(dist).sort((a, b) => a - b);
  const R = rim[Math.floor(rim.length * 0.97)];
  ns.forEach((n, i) => {
    const r = dist(n);
    if (!degree[i] && r > R) d.forEach((k, j) => { n[k] = mid[j] + (n[k] - mid[j]) * R / r; });
  });
}
const r1 = v => Math.round(v * 10) / 10;

// ---------- write ----------
const out = {
  generated: new Date().toISOString().slice(0, 10), hop2min: HOP2_MIN,
  nodes: list.map((n, i) => {
    const o = { id: n.id, h: n.hop, t: n.t, y: n.yr, v: n.v, a: n.a, c: n.c, g: n.g, r: n.r, p2: [r1(flat[i].x), r1(flat[i].y)], p3: [r1(ball[i].x), r1(ball[i].y), r1(ball[i].z)] };
    if (n.se) o.se = 1; if (n.d) o.d = n.d; if (n.u) o.u = n.u; if (n.key) o.k = n.key; if (n.raw) o.raw = 1; if (n.byOwn) o.bo = n.byOwn; if (n.n1) o.n1 = n.n1; if (n.cs) o.cs = 1; if (n.pdf) o.pdf = n.pdf; if (n.gs) o.gs = n.gs;
    return o;
  }),
  links: links.map(l => [l.source, l.target]),
};
writeFileSync(outFile, "// Citation graph, other direction: works citing my papers and works citing those (static, generated).\nwindow.GRAPH_IN = " + JSON.stringify(out) + ";\n");
const by = h => list.filter(n => n.hop === h).length;
console.log(`own ${by(0)}  citing (hop1) ${by(1)}  citing those (hop2) ${by(2)}  links ${links.length}  SE ${list.filter(n => n.se).length}`);
