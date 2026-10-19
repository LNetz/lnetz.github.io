// Write the generator's captured output; optional args limit it to files whose path ends with one of them.
import { readFileSync, writeFileSync } from "node:fs";
const only = process.argv.slice(2);
const files = JSON.parse(readFileSync(0, "utf8").trim());
for (const [p, c] of Object.entries(files)) {
  if (only.length && !only.some(o => p.replace(/\\/g, "/").endsWith(o))) continue;
  writeFileSync(p, c); console.log("wrote", p);
}
