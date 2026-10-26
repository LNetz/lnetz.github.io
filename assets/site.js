// Shared behaviour for all pages. Each block only runs if its markup exists.

// ---- UI strings for the page language (<html lang="…">) ----
const I18N = {
  en: { theme: { light: "light", dark: "dark", auto: "auto" }, themeLabel: "Theme: ", themeHint: " — click to change",
        pubs: "publications", open: "Open photo: ",
        slideshow: "slideshow", pause: "pause", fs: "full screen", exitFs: "exit full screen",
        flags: { Article: "Article", Dissertation: "Dissertation", MastersThesis: "Master’s thesis", BachelorsThesis: "Bachelor’s thesis" },
        miniTitle: (i, o) => `cited by ${i} works (OpenAlex) · cites ${o} works · blue: my own papers · click: show in the citation map` },
  de: { theme: { light: "hell", dark: "dunkel", auto: "auto" }, themeLabel: "Darstellung: ", themeHint: " — klicken zum Wechseln",
        pubs: "Publikationen", open: "Foto öffnen: ",
        slideshow: "Diashow", pause: "Pause", fs: "Vollbild", exitFs: "Vollbild beenden",
        flags: { Article: "Artikel", Dissertation: "Dissertation", MastersThesis: "Masterarbeit", BachelorsThesis: "Bachelorarbeit" },
        miniTitle: (i, o) => `zitiert von ${i} Arbeiten (OpenAlex) · zitiert ${o} Arbeiten · blau: eigene Paper · Klick: in der Zitationskarte zeigen` },
};
const UI = I18N[document.documentElement.lang] || I18N.en;

// ---- chapters of this page in the index column, under the active page ----
// Taken from the page's own chapter markers (nav.chapters; an article lists its numbered chapters, "In short" and
// "Literature"). On an article, the sub chapters (h3[id]) of the chapter being read open below it; a long h3 can
// give a short label in data-nav. The current chapter and sub chapter are in the accent; on phones the bar shows
// where you are ("EA · 02 How …"). Runs before the menu block, so these links close the sheet too.
(() => {
  const here = document.querySelector(".index nav a.active");
  const marks = [...document.querySelectorAll("nav.chapters a[href^='#']")];
  if (!here || !marks.length) return;
  const label = a => { const c = a.cloneNode(true); c.querySelector(".n")?.remove(); return c.textContent.trim(); };
  const chapters = marks.map(a => ({ el: document.getElementById(a.hash.slice(1)), num: a.querySelector(".n")?.textContent || "",
                                     text: a.dataset.nav || label(a), subs: [] }))
    .filter(c => c.el);
  // each h3 of an article belongs to the last chapter before it
  document.querySelectorAll(".article h3[id]").forEach(h => {
    const owner = chapters.filter(c => c.el.compareDocumentPosition(h) & Node.DOCUMENT_POSITION_FOLLOWING).pop();
    if (owner) owner.subs.push({ el: h, text: h.dataset.nav || h.textContent.trim() });
  });
  const ol = document.createElement("ol");
  ol.className = "sub";
  const link = (el, text, num) => {
    const a = document.createElement("a");
    a.href = `#${el.id}`;
    if (num) { const n = document.createElement("span"); n.className = "n"; n.textContent = num; a.append(n); }
    a.append(text);
    return a;
  };
  chapters.forEach(c => {
    const li = document.createElement("li");
    c.a = link(c.el, c.text, c.num);
    li.append(c.a);
    if (c.subs.length) {
      const sub = document.createElement("ol");
      c.subs.forEach(s => { const sli = document.createElement("li"); s.a = link(s.el, s.text); sli.append(s.a); sub.append(sli); });
      li.append(sub);
    }
    c.li = li;
    ol.append(li);
  });
  here.parentElement.append(ol);
  // the bar on phones: the article's short name and the chapter being read
  const bar = document.querySelector(".index .here"), abbr = document.querySelector(".art-head")?.dataset.abbr;
  const title = bar && bar.textContent;
  const index = document.getElementById("index");
  // scroll spy: the last heading above the upper third of the window is the current one
  const all = chapters.flatMap(c => [c, ...c.subs]);
  let current = null;
  const spy = () => {
    const line = innerHeight * .33;
    const now = all.filter(x => x.el.getBoundingClientRect().top < line).pop() || null;
    if (now === current) return;
    current = now;
    all.forEach(x => x.a.classList.toggle("on", x === now));
    let chap = null;
    chapters.forEach(c => {
      const open = c === now || c.subs.includes(now);
      c.li.classList.toggle("open", open);
      if (open) { c.a.classList.add("on"); chap = c; }
    });
    if (bar && abbr) bar.textContent = chap ? `${abbr} · ${chap.num ? chap.num + " " : ""}${chap.text}` : title;
    // a long list scrolls inside the (desktop) index column: keep the current entry in it
    if (now && index && index.scrollHeight > index.clientHeight + 1) {
      const r = now.a.getBoundingClientRect(), box = index.getBoundingClientRect();
      if (r.top < box.top + 24 || r.bottom > box.bottom - 24) index.scrollTop += r.top - box.top - box.height / 2;
    }
  };
  let queued = false;
  addEventListener("scroll", () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; spy(); }); } }, { passive: true });
  addEventListener("resize", spy);
  spy();
})();

// ---- mobile / tablet menu: the index column becomes a top bar with a full-screen sheet ----
(() => {
  const index = document.getElementById("index");
  const btn = document.getElementById("menu-toggle");
  if (!index || !btn) return;
  const label = { en: ["menu", "close"], de: ["Menü", "Schließen"] }[document.documentElement.lang] || ["menu", "close"];

  const set = open => {
    index.classList.toggle("open", open);
    document.body.classList.toggle("menu-open", open);    // locks page scroll behind the sheet
    btn.setAttribute("aria-expanded", open);
    btn.textContent = open ? label[1] : label[0];
  };
  btn.addEventListener("click", () => set(!index.classList.contains("open")));
  index.querySelectorAll(".menu a").forEach(a => a.addEventListener("click", () => set(false)));
  addEventListener("keydown", e => { if (e.key === "Escape" && index.classList.contains("open")) { set(false); btn.focus(); } });
  matchMedia("(min-width: 901px)").addEventListener("change", e => { if (e.matches) set(false); });
})();

// ---- theme toggle: cycles light → dark → auto (auto follows the OS); light is the default ----
(() => {
  const html = document.documentElement;
  const btn = document.getElementById("theme");
  if (!btn) return;
  const label = btn.querySelector("span");
  const ORDER = ["light", "dark", "auto"];
  // the button shows the current preference
  const sync = () => {
    const p = html.dataset.themePref || "light";
    label.textContent = UI.theme[p];
    btn.setAttribute("aria-label", UI.themeLabel + UI.theme[p] + UI.themeHint);
  };
  sync();
  addEventListener("pageshow", sync);
  btn.addEventListener("click", () => {
    const next = ORDER[(ORDER.indexOf(html.dataset.themePref || "light") + 1) % ORDER.length];
    try { localStorage.setItem("theme", next); } catch (_) {}
    window.applyTheme();                                  // defined in the <head> script
    sync();
  });
})();

// ---- publications: grouped by year, filter by tag ----
(() => {
  const root = document.getElementById("pubs");
  if (!root || !window.PUBS) return;
  const limit = Number(root.dataset.limit) || Infinity;   // About page shows only the latest few
  const pubs = PUBS.slice(0, limit);
  const years = [...new Set(pubs.map(p => p.year))].sort((a, b) => b - a);
  const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const me = s => esc(s).replace("L. Netz", "<b>L. Netz</b>");
  const links = p => {
    const out = [];
    if (p.pdf) out.push(`<a href="${esc(p.pdf)}" target="_blank" rel="noopener">pdf ↗</a>`);
    if (p.doi) out.push(`<a href="https://doi.org/${esc(p.doi)}" target="_blank" rel="noopener">doi ↗</a>`);
    if (p.url) out.push(`<a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.urlLabel || "link")} ↗</a>`);
    out.push(`<a href="https://scholar.google.com/scholar?q=${encodeURIComponent('"' + p.title + '"')}" target="_blank" rel="noopener">scholar ↗</a>`);
    return out.join("");
  };

  // mini graph per paper (assets/pubs-mini.js): what cites it fans in from the left, what it cites fans
  // out to the right; dots coloured by topic like the citation map, my own papers in the accent colour
  const MINI = window.PUBS_MINI || {};
  const mini = key => {
    const m = MINI[key];
    if (!m) return "";
    const W = 168, H = 34, cx = W / 2, cy = H / 2;
    const side = (topics, own, dir) => {              // dir -1: left (cited by), +1: right (cites)
      const dots = [...own.map(() => "own"), ...topics];
      if (!dots.length) return `<text x="${cx + dir * 30}" y="${cy + 3}" text-anchor="middle" class="none">—</text>`;
      const rows = dots.length > 90 ? 8 : 5, cols = Math.ceil(dots.length / rows), dx = Math.min(6.5, 56 / cols);
      let lines = "", pts = "";
      dots.forEach((t, k) => {
        const c = Math.floor(k / rows), r = k % rows;
        const x = cx + dir * (24 + c * dx), y = 3.5 + r * ((H - 7) / (rows - 1));
        lines += `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" class="${t === "own" ? "lo" : "l"}"/>`;
        pts += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${t === "own" ? 2.1 : 1.5}" class="${t === "own" ? "own" : "t" + t}"/>`;
      });
      return lines + pts;
    };
    const nIn = m.c.length + m.co.length, nOut = m.r.length + m.ro.length;
    if (!nIn && !nOut) return "";
    return `<div class="mini mono" role="button" tabindex="0" data-key="${key}" title="${UI.miniTitle(nIn, nOut)}">
            <svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" aria-hidden="true">${side(m.c, m.co, -1)}${side(m.r, m.ro, 1)}<circle cx="${cx}" cy="${cy}" r="3.4" class="me"/><circle cx="${cx}" cy="${cy}" r="5.6" class="ring"/></svg>
            <span>← ${nIn}</span><span>${nOut} →</span>
          </div>`;
  };

  root.innerHTML = years.map(y => `
    <div class="year">
      <div class="y mono">${y}</div>
      <ol class="pubs">${pubs.filter(p => p.year === y).map(p => `
        <li id="pub-${p.key}" data-tags="${p.tags.join(" ")}">
          <span class="key mono">${p.key}</span>
          <div>
            <div class="t">${esc(p.title)}${p.flag ? `<span class="flag mono">${UI.flags[p.flag] || p.flag}</span>` : ""}</div>
            <div class="a">${me(p.authors)}</div>
            <div class="v mono">${esc(p.venue)}</div>
            <div class="plinks mono">${links(p)}</div>
          </div>${mini(p.key)}
        </li>`).join("")}
      </ol>
    </div>`).join("");

  // the list is built here, after the browser looked for #pub-<key>: jump to it now
  const target = location.hash.startsWith("#pub-") && document.getElementById(decodeURIComponent(location.hash.slice(1)));
  if (target) {                                   // instantly, and once more when images etc. have settled
    const go = () => target.scrollIntoView({ block: "center", behavior: "instant" });
    requestAnimationFrame(go);
    addEventListener("load", () => setTimeout(go, 50), { once: true });
  }

  // a click on the mini graph opens the citation map on that paper: the left half in "cited by",
  // the right half in "cites"
  const jump = (el, inn) => {
    document.getElementById("citation-map")?.scrollIntoView({ behavior: "smooth", block: "start" });
    document.dispatchEvent(new CustomEvent("map:focus", { detail: { key: el.dataset.key, inn } }));
  };
  root.querySelectorAll(".mini").forEach(el => {
    el.addEventListener("click", e => { const r = el.getBoundingClientRect(); jump(el, e.clientX < r.left + r.width / 2); });
    el.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); jump(el, false); } });
  });

  const count = document.getElementById("pub-count");
  if (count) count.textContent = `${PUBS.length} ${UI.pubs}`;

  document.querySelectorAll(".filters button[data-f]").forEach(btn => {
    const f = btn.dataset.f;
    const n = f === "all" ? PUBS.length : PUBS.filter(p => p.tags.includes(f)).length;
    btn.insertAdjacentHTML("beforeend", `<span class="n">${n}</span>`);
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filters button[data-f]").forEach(b => b.setAttribute("aria-pressed", b === btn));
      root.querySelectorAll("li").forEach(li => li.hidden = f !== "all" && !li.dataset.tags.split(" ").includes(f));
      root.querySelectorAll(".year").forEach(y => y.classList.toggle("empty", !y.querySelector("li:not([hidden])")));
    });
  });
})();

// ---- photo lightbox with a noise-dissolve between photos ----
// Two moods share one shader (WebGL). Keys, buttons and the slideshow use "ink": a few drops
// land and bloom outward like ink in water — much changes at once, then it slowly fills in, with
// a soft, slightly darker wet edge (watercolour). A swipe instead sweeps a front across the frame,
// from the right going forward, from the left going back. Contours of the incoming photo
// switch first, then its areas of similar brightness switch as a whole; a little static
// noise frays the front. The order is fixed per pixel, so nothing ripples or wobbles.
// Adapted from the "Morph Gallery" shader. Photos whose orientation matches the screen (and
// that aren't panoramas) fill it, cropped like "cover"; the rest are shown whole ("contain",
// letterboxed in the page colour inside the margins).
// Falls back to a short cross-fade without WebGL (or for file:// previews, where
// images can't be uploaded as textures), and to an instant swap when the OS asks
// for reduced motion.
(() => {
  const lb = document.getElementById("lightbox");
  if (!lb) return;
  const img = lb.querySelector("img");
  const canvas = lb.querySelector("canvas");
  const count = lb.querySelector(".count");
  const title = lb.querySelector(".title");
  const figs = [...document.querySelectorAll(".grid figure")];
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  const DURATION = 1400;          // ms of dissolve
  // dissolve order weights: side-to-side sweep, brightness areas, contours, static noise
  const INK_DURATION = 1700;      // ms of the ink-drop transition (fast start, slow fill)
  // lines: contours of the incoming photo fade in faintly (lineAlpha) well ahead of the front (lead)
  const TUNE = { scale: 5.0, edge: 0.08, inkEdge: 0.11, wSweep: 0.75, wShape: 0.55, wEdge: 0.06, wNoise: 0.12, bands: 4.0, kEdge: 2.4, lead: 0.42, lineAlpha: 0.42 };
  let i = -1, opener = null, busy = false, queued = null;

  const srcOf = n => { const im = figs[n].querySelector("img"); return im.dataset.full ? new URL(im.dataset.full, location.href).href : im.src; };   // full size, not the grid thumbnail
  const wrap = n => (n + figs.length) % figs.length;
  // resolves once the image is downloaded *and* decoded, so a transition never waits for decoding
  const load = src => new Promise((ok, fail) => {
    const im = new Image();
    im.decoding = "async";
    im.onload = () => (im.decode ? im.decode().catch(() => {}) : Promise.resolve()).then(() => ok(im));
    im.onerror = fail;
    im.src = src;
  });

  // ---------- WebGL (created lazily on the first transition) ----------
  const VERT = `attribute vec2 p; varying vec2 uv;
    void main() { uv = p * 0.5 + 0.5; gl_Position = vec4(p, 0.0, 1.0); }`;
  const FRAG = `
    #ifdef GL_FRAGMENT_PRECISION_HIGH
    precision highp float;
    #else
    precision mediump float;
    #endif
    uniform sampler2D u_from, u_to;
    uniform float u_progress, u_fromAspect, u_toAspect, u_scale, u_dir, u_edge;
    uniform float u_wSweep, u_wShape, u_wEdge, u_wNoise, u_bands, u_kEdge, u_ink, u_lead, u_lineAlpha;
    uniform vec4 u_fromBox, u_toBox;       // where each photo sits on the canvas (uv: x0, y0, x1, y1)
    uniform float u_fromCover, u_toCover;  // 1 = fill its box (crop), 0 = whole photo (letterbox)
    uniform vec2 u_seed;
    uniform vec2 u_res;
    uniform vec3 u_bg;
    varying vec2 uv;

    vec3 permute(vec3 x) { return mod(((x * 34.0) + 1.0) * x, 289.0); }
    float snoise(vec2 v) {
      const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
      vec2 i = floor(v + dot(v, C.yy));
      vec2 x0 = v - i + dot(i, C.xx);
      vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
      vec4 x12 = x0.xyxy + C.xxzz;
      x12.xy -= i1;
      i = mod(i, 289.0);
      vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
      vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);
      m = m * m; m = m * m;
      vec3 x = 2.0 * fract(p * C.www) - 1.0;
      vec3 h = abs(x) - 0.5;
      vec3 a0 = x - floor(x + 0.5);
      m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
      vec3 g;
      g.x = a0.x * x0.x + h.x * x0.y;
      g.yz = a0.yz * x12.xz + h.yz * x12.yw;
      return 130.0 * dot(m, g);
    }
    float fbm(vec2 v) {
      float s = 0.0, a = 0.5;
      for (int k = 0; k < 5; k++) { s += a * snoise(v); v *= 2.0; a *= 0.5; }
      return s;
    }
    // canvas position -> texture position, "contain" or "cover" inside the photo's box
    vec2 place(vec2 q, float imgAspect, vec4 box, float cover) {
      vec2 size = box.zw - box.xy;
      float ba = (u_res.x * size.x) / (u_res.y * size.y);
      vec2 s = (ba > imgAspect) == (cover < 0.5) ? vec2(ba / imgAspect, 1.0) : vec2(1.0, imgAspect / ba);
      return ((q - box.xy) / size - 0.5) * s + 0.5;
    }
    vec4 photo(sampler2D tex, vec2 q, float imgAspect, vec4 box, float cover) {
      vec2 t = place(q, imgAspect, box, cover);
      if (t.x < 0.0 || t.y < 0.0 || t.x > 1.0 || t.y > 1.0) return vec4(u_bg, 0.0);   // alpha 0 = letterbox
      return vec4(texture2D(tex, t).rgb, 1.0);
    }
    // luminance of the incoming photo at q; letterbox areas read as black, so they switch last
    float lumTo(vec2 q) {
      vec4 c = photo(u_to, q, u_toAspect, u_toBox, u_toCover);
      return c.a > 0.5 ? dot(c.rgb, vec3(0.299, 0.587, 0.114)) : 0.0;
    }
    void main() {
      // The order in which each pixel switches is fixed for the whole transition (nothing moves,
      // so there is no wobble); progress just sweeps a threshold through it:
      //   sweep — side to side, from the right going forward, from the left going back
      //   edge  — contours of the incoming photo switch first (Sobel on a 3x3 neighbourhood)
      //   shape — then whole areas of similar brightness switch together, brightest first
      //   noise — a little static fbm so the front frays instead of cutting
      // contours: Sobel at ~1 px spacing, only clear edges pass, so they come in as fine lines
      vec2 d = 1.0 / u_res;
      float l00 = lumTo(uv + vec2(-d.x, -d.y)), l10 = lumTo(uv + vec2(0.0, -d.y)), l20 = lumTo(uv + vec2(d.x, -d.y));
      float l01 = lumTo(uv + vec2(-d.x, 0.0)),  l11 = lumTo(uv),                   l21 = lumTo(uv + vec2(d.x, 0.0));
      float l02 = lumTo(uv + vec2(-d.x, d.y)),  l12 = lumTo(uv + vec2(0.0, d.y)),  l22 = lumTo(uv + vec2(d.x, d.y));
      float gx = (l20 + 2.0 * l21 + l22) - (l00 + 2.0 * l01 + l02);
      float gy = (l02 + 2.0 * l12 + l22) - (l00 + 2.0 * l10 + l20);
      float edge = smoothstep(0.35, 0.85, length(vec2(gx, gy)) * u_kEdge);
      // the border between photo and letterbox is not a contour of the photo
      vec2 tq = place(uv, u_toAspect, u_toBox, u_toCover);
      vec2 m = min(tq, 1.0 - tq) / (4.0 * abs(place(uv + d, u_toAspect, u_toBox, u_toCover) - tq));
      edge *= step(1.5, min(m.x, m.y));
      // areas: brightness over a wider neighbourhood, in bands, so flat areas switch as one
      vec2 D = 5.0 / u_res;
      float mean = (lumTo(uv) * 2.0 + lumTo(uv + vec2(D.x, 0.0)) + lumTo(uv - vec2(D.x, 0.0))
                  + lumTo(uv + vec2(0.0, D.y)) + lumTo(uv - vec2(0.0, D.y))) / 6.0;
      float region = floor(mean * u_bands + 0.5) / u_bands;

      vec2 nuv = (uv - 0.5) * u_res / min(u_res.x, u_res.y);         // round noise in any canvas shape
      float n = fbm(nuv * u_scale) * 0.5 + 0.5;                       // static: no ripple
      float shapeT = u_wShape * (1.0 - region) - u_wEdge * edge + u_wNoise * (n - 0.5);

      // swipe: a front from the side the finger comes from
      float sweep = u_dir > 0.0 ? 1.0 - uv.x : uv.x;
      float tSwipe = u_wSweep * sweep + shapeT;
      float lo = -u_wEdge - 0.5 * u_wNoise, hi = u_wSweep + u_wShape + 0.5 * u_wNoise;
      tSwipe = (tSwipe - lo) / (hi - lo);

      // ink: a few drops land and bloom outward through water — distance to the nearest drop,
      // warped by low-frequency noise into tendrils; later drops start a little later
      float ink = 10.0;
      vec2 asp = vec2(u_res.x / min(u_res.x, u_res.y), u_res.y / min(u_res.x, u_res.y));
      float warp = fbm(nuv * 1.6 + u_seed * 7.0) * 0.32 + fbm(nuv * 4.5 - u_seed * 3.0) * 0.08;
      for (int k = 0; k < 3; k++) {
        float fk = float(k);
        vec2 c = vec2(fract(sin(fk * 12.9898 + u_seed.x * 78.233) * 43758.5453),
                      fract(sin(fk * 39.3468 + u_seed.y * 11.135) * 24634.6345));
        c = 0.15 + 0.7 * c;
        ink = min(ink, length((uv - c) * asp) + warp + fk * 0.18);
      }
      float tInk = clamp((ink * 1.05 + shapeT * 0.45) / 1.15, 0.0, 1.0);

      float t = mix(tSwipe, tInk, u_ink);
      float adjusted = u_progress * (1.0 + 2.0 * u_edge) - u_edge;
      float mixF = 1.0 - smoothstep(adjusted - u_edge, adjusted + u_edge, t);
      // lines: faint contours of the incoming photo show up long before the front reaches them
      float ahead = 1.0 - smoothstep(adjusted - u_edge, adjusted + u_edge + u_lead, t);
      mixF = max(mixF, edge * u_lineAlpha * ahead);
      vec4 a = photo(u_from, uv, u_fromAspect, u_fromBox, u_fromCover);
      vec4 b = photo(u_to, uv, u_toAspect, u_toBox, u_toCover);
      vec3 col = mix(a.rgb, b.rgb, mixF);
      // watercolour: pigment pools at the wet edge — a soft, slightly darker rim on the front
      float rim = smoothstep(0.0, 1.0, 1.0 - abs(mixF * 2.0 - 1.0));
      col *= 1.0 - 0.16 * rim * u_ink * (0.6 + 0.4 * n);
      gl_FragColor = vec4(col, 1.0);
    }`;

  let gl = null, glFailed = false, U = {};
  const initGL = () => {
    if (gl || glFailed) return !!gl;
    try {
      gl = canvas.getContext("webgl", { alpha: false, antialias: false });
      if (!gl) throw new Error("no webgl");
      const sh = (type, src) => {
        const s = gl.createShader(type);
        gl.shaderSource(s, src);
        gl.compileShader(s);
        if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
        return s;
      };
      const prog = gl.createProgram();
      gl.attachShader(prog, sh(gl.VERTEX_SHADER, VERT));
      gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FRAG));
      gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
      gl.useProgram(prog);
      gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
      const loc = gl.getAttribLocation(prog, "p");
      gl.enableVertexAttribArray(loc);
      gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
      for (const k of ["from", "to", "progress", "fromAspect", "toAspect", "scale", "dir", "edge", "res", "bg", "wSweep", "wShape", "wEdge", "wNoise", "bands", "kEdge", "ink", "seed", "lead", "lineAlpha", "fromBox", "toBox", "fromCover", "toCover"])
        U[k] = gl.getUniformLocation(prog, "u_" + k);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
      return true;
    } catch (_) {
      gl = null; glFailed = true;
      return false;
    }
  };

  const texture = im => {        // throws on tainted images (file:// previews)
    const t = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, im);
    // photos aren't powers of two: clamp + linear is the only legal pair in WebGL1
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    return t;
  };

  const ease = t => t < 0.5 ? 4 * t ** 3 : 1 - (-2 * t + 2) ** 3 / 2;    // cubic in-out: calm start/end, visible middle
  const easeOut = t => 1 - (1 - t) ** 3;                                   // for finishing a swipe already in motion
  const pageColour = () => (getComputedStyle(lb).backgroundColor.match(/[\d.]+/g) || [247, 247, 245]).slice(0, 3).map(v => v / 255);

  // A photo fills the screen when its orientation matches the screen's and it isn't a panorama
  // (or a tall strip); squares and the rest are shown whole within the margins.
  const fills = im => {
    const a = im.naturalWidth / im.naturalHeight, v = innerWidth / innerHeight;
    if (!a || a > 2.1 || a < 1 / 2.1) return false;
    return v >= 1 ? a > 1.15 : a < 0.87;
  };
  // the photo's box on the (full-window) canvas in GL uv, y up: all of it, or inside the margins
  const box = im => {
    if (fills(im)) return [0, 0, 1, 1];
    const cs = getComputedStyle(lb), px = k => parseFloat(cs.getPropertyValue(k)) || 0;
    const W = canvas.clientWidth, H = canvas.clientHeight;
    return [px("--lb-side") / W, px("--lb-bottom") / H, 1 - px("--lb-side") / W, 1 - px("--lb-top") / H];
  };
  // the resting <img> follows the photo it shows
  const fit = () => lb.classList.toggle("fill", !!img.naturalWidth && fills(img));
  img.addEventListener("load", fit);
  addEventListener("resize", fit);

  // Uploads both photos and sets up the shader; returns draw(progress 0..1) and dispose().
  // Used by timed transitions (morph) and by the finger-driven swipe alike. Throws on
  // tainted images (file:// previews) — callers fall back to a cross-fade.
  const prepare = (fromIm, toIm, dir, ink = false) => {
    const tFrom = texture(fromIm);
    const tTo = texture(toIm);
    lb.classList.add("morphing");                       // canvas visible, resting <img> hidden
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(canvas.clientWidth * dpr);
    canvas.height = Math.round(canvas.clientHeight * dpr);
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tFrom); gl.uniform1i(U.from, 0);
    gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, tTo); gl.uniform1i(U.to, 1);
    gl.uniform2f(U.res, canvas.width, canvas.height);
    gl.uniform3f(U.bg, ...pageColour());
    gl.uniform1f(U.fromAspect, fromIm.naturalWidth / fromIm.naturalHeight);
    gl.uniform1f(U.toAspect, toIm.naturalWidth / toIm.naturalHeight);
    // TUNE can be overridden from the console (window.LB_TUNE) to try variants
    const tune = Object.assign({}, TUNE, window.LB_TUNE || {});
    gl.uniform1f(U.dir, dir);
    for (const k of ["scale", "wSweep", "wShape", "wEdge", "wNoise", "bands", "kEdge", "lead", "lineAlpha"]) gl.uniform1f(U[k], tune[k]);
    gl.uniform4f(U.fromBox, ...box(fromIm)); gl.uniform1f(U.fromCover, fills(fromIm) ? 1 : 0);
    gl.uniform4f(U.toBox, ...box(toIm)); gl.uniform1f(U.toCover, fills(toIm) ? 1 : 0);
    // ink mode (keys, buttons, slideshow): drops bloom out with a wider, softer wet edge
    gl.uniform1f(U.ink, ink ? 1 : 0);
    gl.uniform1f(U.edge, ink ? tune.inkEdge : tune.edge);
    gl.uniform2f(U.seed, Math.random(), Math.random());       // new drop positions every time
    const draw = p => { gl.uniform1f(U.progress, p); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); };
    draw(0);
    return { draw, dispose: () => { gl.deleteTexture(tFrom); gl.deleteTexture(tTo); } };
  };

  // animate a prepared transition from progress p0 to p1 (eased), resolves when done
  const run = (h, p0, p1, ms, fn = ease) => new Promise(resolve => {
    let start = null;                                   // first frame's timestamp, same clock as `now`
    const frame = now => {
      if (start === null) start = now;
      const k = Math.min((now - start) / Math.max(ms, 1), 1);
      h.draw(p0 + (p1 - p0) * fn(k));
      if (k < 1) requestAnimationFrame(frame); else resolve();
    };
    requestAnimationFrame(frame);
  });

  // ink in water: much changes at once, then it slowly fills in (exponential ease-out)
  const easeInk = t => 1 - Math.pow(1 - t, 2.4);
  const morph = async (fromIm, toIm, dir) => {
    const h = prepare(fromIm, toIm, dir, true);
    lb.classList.toggle("fill", fills(toIm));           // caption shade follows the incoming photo
    await run(h, 0, 1, INK_DURATION, easeInk);
    h.dispose();
  };

  const fade = async src => {                          // fallback transition
    img.style.opacity = "0";
    await new Promise(r => setTimeout(r, 180));
    img.src = src;
    await img.decode().catch(() => {});
    img.style.opacity = "1";
  };

  // ---------- loading: thumbnail first, full size as soon as it is there ----------
  const thumbOf = n => figs[n].querySelector("img").currentSrc || figs[n].querySelector("img").src;
  const cache = new Map();                              // src -> Promise<HTMLImageElement>
  const ready = new Map();                              // src -> decoded image, for instant (sync) use
  const get = src => {
    if (!cache.has(src)) cache.set(src, load(src).then(im => { ready.set(src, im); return im; })
                                                 .catch(e => { cache.delete(src); throw e; }));
    return cache.get(src);
  };
  const thumbReady = n => {                             // the grid tile, if it has finished loading
    const t = figs[n].querySelector("img");
    return t.complete && t.naturalWidth ? t : null;
  };
  const within = (p, ms) => Promise.race([p.catch(() => null), new Promise(r => setTimeout(() => r(null), ms))]);
  const sharpen = n => get(srcOf(n)).then(() => {   // swap the thumbnail for the full photo once loaded
    if (i === n && !lb.classList.contains("morphing")) img.src = srcOf(n);
  }).catch(() => {});
  // background preloading around the current photo: nearest first (+1, -1, +2, +3, -2, +4),
  // at most two downloads at a time so the photo on screen is never starved; re-prioritised on
  // every move, so skipping ahead stays smooth
  const AHEAD = [1, -1, 2, 3, -2, 4];
  let queue = [], active = 0;
  const pump = () => {
    while (active < 2 && queue.length) {
      const src = queue.shift();
      if (cache.has(src)) continue;                     // already loaded or loading
      active++;
      get(src).catch(() => {}).finally(() => { active--; pump(); });
    }
  };
  const preload = n => {
    queue = AHEAD.map(d => srcOf(wrap(n + d))).filter((s, k, all) => all.indexOf(s) === k && s !== srcOf(n));
    pump();
  };

  // ---------- navigation ----------
  const caption = n => {
    const fig = figs[n];
    count.textContent = `${n + 1} / ${figs.length}`;
    title.textContent = [...fig.querySelectorAll("figcaption span")].map(s => s.textContent).filter(Boolean).join("  ·  ");
    img.alt = fig.querySelector("img").alt;
  };

  const go = async (n, dir) => {
    n = wrap(n);
    if (n === i) return;
    if (busy) { queued = [n, dir]; return; }          // finish the running dissolve, then continue
    busy = true;
    clearTimeout(timer);
    const from = i;
    i = n;
    caption(n);
    // use the full photo if it arrives quickly, otherwise dissolve to the (cached) thumbnail
    let to = await within(get(srcOf(n)), 350);
    const src = to ? srcOf(n) : thumbOf(n);
    try {
      if (!to) to = await get(src);
      if (reduced.matches) {
        img.src = src;
      } else if (from >= 0 && initGL()) {
        await morph(img, to, dir);
        img.src = src;
        await img.decode().catch(() => {});
        fit();
        lb.classList.remove("morphing");
      } else {
        await fade(src);
      }
    } catch (_) {
      lb.classList.remove("morphing");
      glFailed = true;                                  // e.g. file:// — cross-fade from now on
      await fade(src);
    }
    if (src !== srcOf(n)) sharpen(n);
    preload(n);
    busy = false;
    if (queued) { const [q, d] = queued; queued = null; go(q, d); return; }
    schedule();
  };

  const open = n => {
    opener = document.activeElement;
    i = wrap(n);
    caption(i);
    img.src = thumbOf(i);                               // instant: the thumbnail is already loaded
    img.style.opacity = "1";
    sharpen(i);
    lb.classList.add("open");
    document.body.style.overflow = "hidden";
    lb.focus();
    preload(i);
  };
  const close = () => {
    setPlaying(false);
    if (document.fullscreenElement) exitFs();
    lb.classList.remove("open", "morphing", "idle");
    document.body.style.overflow = "";
    queued = null;
    if (opener) opener.focus();
  };
  // count from the photo already queued, so quick repeated presses skip ahead
  const target = () => (queued ? queued[0] : i);
  const next = () => go(target() + 1, 1);
  const prev = () => go(target() - 1, -1);

  // ---------- slideshow ----------
  const INTERVAL = 5000;                                // ms each photo stays (plus the dissolve)
  const playBtn = lb.querySelector(".play");
  const fsBtn = lb.querySelector(".fs");
  const bar = lb.querySelector(".progress circle");   // small ring that fills while a photo stays
  let playing = false, timer = null;

  function schedule() {
    clearTimeout(timer);
    bar.style.animation = "none";
    if (!playing || document.hidden) return;
    void bar.offsetWidth;                               // restart the progress line
    bar.style.animation = `lb-progress ${INTERVAL}ms linear forwards`;
    timer = setTimeout(() => { if (playing) go(i + 1, 1); }, INTERVAL);
  }
  function setPlaying(on) {
    playing = on;
    lb.classList.toggle("playing", on);
    playBtn.setAttribute("aria-pressed", on);
    playBtn.querySelector("i").textContent = on ? "❚❚" : "▶";
    playBtn.querySelector("span").textContent = on ? UI.pause : UI.slideshow;
    if (on) { preload(i); if (!busy) schedule(); } else { clearTimeout(timer); bar.style.animation = "none"; }
    poke();
  }
  document.addEventListener("visibilitychange", () => { if (lb.classList.contains("open")) schedule(); });

  // ---------- full screen ----------
  // Esc in full screen is swallowed by the browser (it only leaves full screen), so a full-screen
  // exit we did not ask for closes the lightbox too; the full-screen button only leaves full screen.
  let leavingOnPurpose = false;
  const exitFs = () => { leavingOnPurpose = true; return document.exitFullscreen().catch(() => {}); };
  const toggleFs = () => {
    if (!document.fullscreenEnabled) return;
    if (document.fullscreenElement) exitFs();
    else lb.requestFullscreen().catch(() => {});
  };
  if (!document.fullscreenEnabled) fsBtn.hidden = true;   // e.g. iPhone Safari
  document.addEventListener("fullscreenchange", () => {
    const fs = document.fullscreenElement === lb;
    lb.classList.toggle("fs", fs);
    fsBtn.querySelector("span").textContent = fs ? UI.exitFs : UI.fs;
    if (!fs && !leavingOnPurpose && lb.classList.contains("open")) close();
    leavingOnPurpose = false;
    poke();
  });

  // controls and cursor fade out while a slideshow or full screen runs undisturbed
  let idleTimer = null;
  function poke() {
    lb.classList.remove("idle");
    clearTimeout(idleTimer);
    if (playing || lb.classList.contains("fs")) idleTimer = setTimeout(() => lb.classList.add("idle"), 2500);
  }
  lb.addEventListener("pointermove", poke);

  // ---------- wiring ----------
  lb.tabIndex = -1;
  figs.forEach((fig, n) => {
    fig.tabIndex = 0;                                   // photos are reachable by keyboard
    fig.setAttribute("role", "button");
    fig.setAttribute("aria-label", UI.open + fig.querySelector("img").alt);
    fig.addEventListener("click", () => open(n));
    fig.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(n); } });
    // start fetching the full photo as soon as someone shows interest in the tile
    const warm = () => get(srcOf(n)).catch(() => {});
    fig.addEventListener("pointerenter", warm, { once: true });
    fig.addEventListener("touchstart", warm, { once: true, passive: true });
    fig.addEventListener("focus", warm, { once: true });
  });

  const stop = fn => e => { e.stopPropagation(); fn(); };
  lb.querySelector(".next").addEventListener("click", stop(next));
  lb.querySelector(".prev").addEventListener("click", stop(prev));
  lb.querySelector(".close").addEventListener("click", stop(close));
  playBtn.addEventListener("click", stop(() => setPlaying(!playing)));
  fsBtn.addEventListener("click", stop(toggleFs));

  // "slideshow" on the gallery page: start at the first photo, full screen where available
  document.querySelectorAll("[data-slideshow]").forEach(b => b.addEventListener("click", () => {
    open(0);
    setPlaying(true);
    toggleFs();
  }));

  // Swipe. With WebGL the transition follows the finger (or a dragged mouse): the dissolve front
  // moves as far as you pull. Releasing past a third of the way, or with a quick flick, completes
  // it; otherwise it springs back. Without WebGL (or with reduced motion) a swipe simply moves on.
  // A plain tap/click on the backdrop or photo closes (see the click handler below).
  let sx = null, swiped = false, drag = null, trail = [];   // trail: recent [time, x] for the flick speed
  // the browser's own image drag-and-drop would take over the gesture (pointercancel)
  img.draggable = false;
  lb.addEventListener("dragstart", e => e.preventDefault());
  lb.addEventListener("pointerdown", e => {
    if (e.target.closest(".cap") || busy) return;
    sx = e.clientX; swiped = false; drag = null; trail = [[e.timeStamp, e.clientX]];
  });
  lb.addEventListener("pointermove", e => {
    if (sx === null) return;
    const dx = e.clientX - sx, now = e.timeStamp;            // input time, not processing time
    trail.push([now, e.clientX]);
    while (trail.length > 2 && now - trail[0][0] > 100) trail.shift();   // keep ~the last 100 ms
    if (!drag) {
      if (Math.abs(dx) < 10 || busy || reduced.matches || !initGL()) return;
      const dir = dx < 0 ? 1 : -1, n = wrap(i + dir);
      const toIm = ready.get(srcOf(n)) || thumbReady(n);
      if (!toIm) return;                                // nothing decoded yet: plain swipe on release
      try {
        drag = { dir, n, src: ready.has(srcOf(n)) ? srcOf(n) : thumbOf(n), h: prepare(img, toIm, dir), p: 0 };
      } catch (_) { glFailed = true; return; }           // e.g. file:// — plain swipes from now on
      busy = true;
      clearTimeout(timer);
      try { lb.setPointerCapture(e.pointerId); } catch (_) {}
    }
    drag.p = Math.max(0, Math.min(1, (-dx * drag.dir) / (canvas.clientWidth * 0.75)));
    drag.h.draw(drag.p);
  });
  const release = async e => {
    if (sx === null) return;
    const dx = e.clientX - sx;
    const [t0, x0] = trail[0], dt = e.timeStamp - t0;
    sx = null;
    if (!drag) {
      if (e.type === "pointerup" && Math.abs(dx) > 48) { swiped = true; dx < 0 ? next() : prev(); }
      return;
    }
    swiped = true;
    const d = drag;
    drag = null;
    const speed = (-(e.clientX - x0) * d.dir) / Math.max(dt, 1);   // px/ms over the last ~100 ms
    if (e.type === "pointerup" && (d.p > 0.33 || (speed > 0.5 && d.p > 0.05))) {
      await run(d.h, d.p, 1, 120 + DURATION * 0.55 * (1 - d.p), easeOut);
      i = d.n;
      caption(i);
      img.src = d.src;
      await img.decode().catch(() => {});
      fit();
      lb.classList.remove("morphing");
      d.h.dispose();
      if (d.src !== srcOf(i)) sharpen(i);
      preload(i);
    } else {                                            // not far enough: spring back
      await run(d.h, d.p, 0, 220 + 320 * d.p, easeOut);
      lb.classList.remove("morphing");
      d.h.dispose();
    }
    busy = false;
    if (queued) { const [q, qd] = queued; queued = null; go(q, qd); } else schedule();
  };
  lb.addEventListener("pointerup", release);
  lb.addEventListener("pointercancel", release);
  lb.addEventListener("click", e => {
    if (swiped) { swiped = false; return; }
    if (e.target.closest(".cap")) return;
    if (lb.classList.contains("idle")) { poke(); return; }   // first tap just brings the controls back
    close();
  });

  addEventListener("keydown", e => {
    if (!lb.classList.contains("open")) return;
    poke();
    if (e.key === "Escape") close();
    else if (e.key === "ArrowRight") { e.preventDefault(); next(); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
    else if (e.key === " ") { e.preventDefault(); setPlaying(!playing); }
    else if (e.key === "f" || e.key === "F") { e.preventDefault(); toggleFs(); }
  });
})();

// ---- scroll reveal: content below the page header fades up as it enters the view ----
// Only armed with html.anim (see <head>); without JS or with reduced motion nothing is hidden.
(() => {
  const root = document.documentElement;
  if (!root.classList.contains("anim") || !("IntersectionObserver" in window)) return;
  const items = [...document.querySelectorAll(
    "main section > .group, main section > .filters, .quick, main section > .bio, " +
    ".themes > div, .spec > li, .rows > li, .year, .grid figure"
  )];
  const loadedAt = performance.now();
  const io = new IntersectionObserver(entries => {
    // what is visible right after load waits for the opening sequence (~.6s)
    const base = performance.now() - loadedAt < 400 ? 0.6 : 0;
    entries.filter(e => e.isIntersecting).forEach((e, k) => {
      e.target.style.setProperty("--d", `${base + Math.min(k * 0.05, 0.5)}s`);   // gentle stagger per batch
      e.target.classList.add("in");
      io.unobserve(e.target);
    });
  }, { rootMargin: "0px 0px -6% 0px" });
  items.forEach(el => { el.classList.add("reveal"); io.observe(el); });
})();

// ---- back to top: a small round arrow bottom right, once the page has been scrolled down ----
(() => {
  if (!document.querySelector("footer")) return;
  const a = document.createElement("a");
  a.className = "to-top mono";
  a.href = "#top";
  a.textContent = "↑";
  a.setAttribute("aria-label", document.documentElement.lang === "de" ? "nach oben" : "back to top");
  document.body.append(a);
  let on = false, over = false;
  // interactive figures in view: the button steps aside while one of them is under it (bottom 80px)
  const demos = new Set();
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(es => { es.forEach(e => (e.isIntersecting ? demos.add(e.target) : demos.delete(e.target))); sync(); });
    document.querySelectorAll("figure.demo").forEach(f => io.observe(f));
  }
  const sync = () => {
    const show = scrollY > innerHeight * 0.9;
    if (show !== on) { on = show; a.classList.toggle("on", on); }
    const o = [...demos].some(f => { const r = f.getBoundingClientRect(); return r.top < innerHeight && r.bottom > innerHeight - 80; });
    if (o !== over) { over = o; a.classList.toggle("over-demo", over); }
  };
  addEventListener("scroll", sync, { passive: true });
  sync();
})();

// ---- thin sliders in articles (demo-common.js): also those a figure script created ----
if (window.SiteDemo) document.querySelectorAll(".art-sec input[type=range]").forEach(SiteDemo.thin);

// ---- wide diagrams (.dia-scroll): on phones they scroll sideways; the edges fade where there is more ----
(() => {
  document.querySelectorAll(".dia-scroll").forEach(el => {
    const sync = () => {
      const max = el.scrollWidth - el.clientWidth;
      el.style.setProperty("--fl", `${Math.min(40, el.scrollLeft)}px`);
      el.style.setProperty("--fr", `${Math.max(0, Math.min(40, max - el.scrollLeft))}px`);
      el.classList.toggle("scrolls", max > 2);          // the figure's caption then shows "↔ scroll" (style.css)
    };
    el.addEventListener("scroll", sync, { passive: true });
    addEventListener("resize", sync);
    sync();
  });
})();

// ---- project lifeline: scrolls sideways (wheel, drag, arrow keys) ----
// When it comes into view it starts at the left and glides over to today (stops as soon as
// the visitor takes over; reduced motion: straight to today). The vertical wheel moves the
// rail until it reaches an end; then the page scrolls on.
(() => {
  document.querySelectorAll(".lifeline").forEach(el => {
    // edges fade only where there is more to scroll
    const FADE = 56;
    // a title whose start has scrolled out of view stays at the left edge while its line is visible
    const runs = [...el.querySelectorAll(".ll-p")].map(a => ({ a, s: a.querySelector("span") }));
    const sync = () => {
      const max = el.scrollWidth - el.clientWidth;
      el.style.setProperty("--fl", `${Math.min(FADE, el.scrollLeft)}px`);
      el.style.setProperty("--fr", `${Math.min(FADE, max - el.scrollLeft)}px`);
      for (const { a, s } of runs) {
        const len = parseFloat(a.style.getPropertyValue("--len")) || 0;
        const shift = Math.max(0, Math.min(el.scrollLeft + FADE * 0.7 - a.offsetLeft, len - s.offsetWidth - 6));
        s.style.transform = shift ? `translateX(${shift}px)` : "";
      }
    };
    el.addEventListener("scroll", sync, { passive: true });
    addEventListener("resize", sync);
    let glide = 0, touched = false;
    const stop = () => { touched = true; cancelAnimationFrame(glide); glide = 0; };
    const toToday = () => {
      if (touched) return;
      const max = el.scrollWidth - el.clientWidth;
      if (matchMedia("(prefers-reduced-motion: reduce)").matches) { el.scrollLeft = max; return; }
      const from = el.scrollLeft, t0 = performance.now(), dur = Math.min(2600, 900 + max * 0.9);
      let frames = 0;                                                  // safety net: never more than 600 frames
      const step = now => {
        const k = ++frames > 600 ? 1 : Math.min(1, (now - t0) / dur), e = k < .5 ? 4 * k * k * k : 1 - (-2 * k + 2) ** 3 / 2;
        el.scrollLeft = from + (max - from) * e;
        glide = k < 1 ? requestAnimationFrame(step) : 0;
      };
      glide = requestAnimationFrame(step);
    };
    el.scrollLeft = 0; sync();
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(([e]) => {
        if (!e.isIntersecting) return;
        io.disconnect();
        setTimeout(toToday, 500);                                       // after the rail has drawn in
      }, { threshold: 0.6 });
      io.observe(el);
    } else el.scrollLeft = el.scrollWidth;
    ["wheel", "pointerdown", "keydown", "touchstart"].forEach(t => el.addEventListener(t, stop, { passive: true }));
    el.addEventListener("wheel", e => {
      if (Math.abs(e.deltaY) <= Math.abs(e.deltaX)) return;          // trackpads scroll sideways natively
      const max = el.scrollWidth - el.clientWidth;
      if ((e.deltaY < 0 && el.scrollLeft <= 0) || (e.deltaY > 0 && el.scrollLeft >= max - 1)) return;
      e.preventDefault();
      el.scrollLeft = Math.max(0, Math.min(max, el.scrollLeft + e.deltaY));
    }, { passive: false });
    let x0 = null, s0 = 0, moved = false;                             // drag with the mouse
    el.addEventListener("pointerdown", e => {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      x0 = e.clientX; s0 = el.scrollLeft; moved = false;
    });
    addEventListener("pointermove", e => {
      if (x0 === null) return;
      if (!moved && Math.abs(e.clientX - x0) > 4) { moved = true; el.classList.add("drag"); }
      if (moved) el.scrollLeft = s0 - (e.clientX - x0);
    });
    addEventListener("pointerup", () => { x0 = null; el.classList.remove("drag"); });
    el.addEventListener("click", e => { if (moved) { e.preventDefault(); moved = false; } }, true);
    el.addEventListener("keydown", e => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault();
      el.scrollBy({ left: e.key === "ArrowRight" ? 240 : -240, behavior: "smooth" });
    });
  });
})();

// Footer gamepad: Connect Four opens as an overlay over the current page (like the photo lightbox)
// instead of leaving it. Loaded on first use; closing keeps the game, so reopening continues it.
// Ctrl/⌘/middle click still opens the game as a page of its own.
(() => {
  const egg = document.querySelector(".foot-icons .egg");
  if (!egg) return;
  const de = document.documentElement.lang === "de";
  let box = null, frame = null, opener = null;
  const close = () => {
    if (!box || !box.classList.contains("open")) return;
    box.classList.remove("open");
    document.body.style.overflow = "";
    if (opener) opener.focus();
  };
  const open = () => {
    opener = document.activeElement;
    if (!box) {
      box = document.createElement("div");
      box.className = "game-overlay";
      box.setAttribute("role", "dialog");
      box.setAttribute("aria-modal", "true");
      box.setAttribute("aria-label", egg.getAttribute("aria-label") || "Game");
      box.innerHTML = `<div class="game-frame"><iframe title="${egg.getAttribute("aria-label") || "Game"}" src="${egg.href}" allow="fullscreen; autoplay"></iframe></div>
        <button type="button" class="game-x mono">${de ? "schließen" : "close"} ×</button>`;
      document.body.appendChild(box);
      frame = box.querySelector("iframe");
      box.querySelector(".game-x").addEventListener("click", close);
      box.addEventListener("click", e => { if (e.target === box) close(); });   // click beside the game
    }
    box.classList.add("open");
    document.body.style.overflow = "hidden";
    setTimeout(() => frame.focus(), 60);                // keys (1–7, R) go straight to the game
  };
  egg.addEventListener("click", e => {
    if (e.button || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    open();
  });
  addEventListener("keydown", e => { if (e.key === "Escape") close(); });
  // Esc inside the game (it has the focus) arrives as a message
  addEventListener("message", e => { if (e.origin === location.origin && e.data && e.data.type === "game:close") close(); });
})();

// Share links on articles (a.share after headings and captions, built by article_common.share_links): a click copies
// the link to that section or figure and says so for a moment. An anchor inside a closed "for the curious" box opens it.
(() => {
  const links = document.querySelectorAll(".article a.share");
  if (!links.length) return;
  const done = document.documentElement.lang === "de" ? "kopiert" : "copied";
  const copy = text => navigator.clipboard?.writeText(text).catch(() => fallback(text)) ?? fallback(text);
  const fallback = text => {
    const t = Object.assign(document.createElement("textarea"), { value: text });
    t.style.cssText = "position:fixed;opacity:0";
    document.body.append(t);
    t.select();
    try { document.execCommand("copy"); } catch (_) {}
    t.remove();
  };
  links.forEach(a => a.addEventListener("click", e => {
    if (e.button || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    const url = location.origin + location.pathname + a.hash;
    copy(url);
    history.replaceState(null, "", a.hash);
    a.dataset.done = done;
    clearTimeout(a._t);
    a._t = setTimeout(() => delete a.dataset.done, 1600);
  }));
  const reveal = () => {
    const el = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    const box = el && el.closest("details:not([open])");
    if (box) { box.open = true; el.scrollIntoView(); }
  };
  reveal();
  addEventListener("hashchange", reveal);
})();
