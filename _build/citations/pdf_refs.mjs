// Extract the reference list of a PDF as separate entries. usage: node pdf_refs.mjs <pdf> -> JSON array of strings
import { readFileSync } from "node:fs";
import { getDocument } from "pdfjs-dist/legacy/build/pdf.mjs";
const doc = await getDocument({ data: new Uint8Array(readFileSync(process.argv[2])), verbosity: 0 }).promise;
const lines = [];
for (let p = 1; p <= doc.numPages; p++) {
  const page = await doc.getPage(p), tc = await page.getTextContent();
  // group items into lines by y (columns: split at page middle when the page has two columns)
  const W = page.view[2], items = tc.items.filter(i => i.str.trim());
  const twoCol = items.filter(i => i.transform[4] > W * 0.52).length > items.length * 0.3 && items.filter(i => i.transform[4] < W * 0.45).length > items.length * 0.3;
  const cols = twoCol ? [items.filter(i => i.transform[4] < W * 0.5), items.filter(i => i.transform[4] >= W * 0.5)] : [items];
  for (const col of cols) {
    const byY = new Map();
    for (const i of col) { const y = Math.round(i.transform[5]); const k = [...byY.keys()].find(v => Math.abs(v - y) < 3) ?? y; (byY.get(k) || byY.set(k, []).get(k)).push(i); }
    for (const y of [...byY.keys()].sort((a, b) => b - a)) lines.push({ p, x: Math.min(...byY.get(y).map(i => i.transform[4])), t: byY.get(y).sort((a, b) => a.transform[4] - b.transform[4]).map(i => i.str).join(" ").replace(/\s+/g, " ").trim() });
  }
}
let start = -1;
const heads = [];
lines.forEach((l, k) => { if (/^(\d+\.?|[IVX]+\.?)?(REFERENCES|BIBLIOGRAPHY|LITERATUR(VERZEICHNIS)?|LITERATURE)$/.test(l.t.replace(/\s+/g, "").toUpperCase())) heads.push(k); });
// the heading that is followed by entries (running page headers repeat the word later on)
const isEntry = t => /^(\[[^\]]{1,30}\]|\d{1,3}\.\s|\(\d{1,3}\)\s)/.test(t);
start = heads.find(k => lines.slice(k + 1, k + 16).filter(l => isEntry(l.t)).length >= 3) ?? heads.at(-1) ?? -1;
const headWord = start >= 0 ? lines[start].t : null;
const body = lines.slice(start + 1).filter(l => !/^\d{1,3}$/.test(l.t) && l.t !== headWord && !/^\d{1,3} Bibliography$|^Bibliography \d{1,3}$/.test(l.t));
// an entry starts with [..] or "n." / "n " at the line start
const entries = [];
const startRe = /^(\[[^\]]{1,30}\]|\d{1,3}\.\s|\(\d{1,3}\)\s)/;
const numbered = body.filter(l => startRe.test(l.t)).length > 3;
// author-year styles without numbers: an entry starts with "Surname X." unless the previous line ended in a hyphen
const authorRe = /^[\p{Lu}][\p{L}'’-]+(\s[\p{Lu}][\p{L}'’-]+)*,?\s(\p{Lu}\.\s?-?)+\s?[,;:(]/u;
let prev = "";
for (const l of body) {
  const isStart = numbered ? startRe.test(l.t) : authorRe.test(l.t) && !prev.endsWith("-");
  if (isStart || !entries.length) entries.push(l.t); else entries[entries.length - 1] += (entries[entries.length - 1].endsWith("-") ? "" : " ") + l.t;
  prev = l.t;
}
// the cover page of se-rwth.de PDFs cites the paper itself
for (let k = entries.length - 1; k >= 0; k--) if (/www\.se-rwth\.de\/publications\/?$/.test(entries[k])) entries.splice(k, 1);
if (process.argv[3] === "dump") { console.log(lines.slice(start - 2, start + 40).map(l => l.p + " " + Math.round(l.x) + " | " + l.t).join("\n")); process.exit(); }
console.log(JSON.stringify({ start, n: entries.length, entries }));
