// Research map: my papers, the papers they cite, and (fainter) what those cite in turn.
// Static data (assets/citations.js, window.GRAPH) with a precomputed 3D layout, projected onto a
// canvas and turning slowly. Colour = topic, ring = RWTH Software Engineering, size = citations (log).
// Hover highlights a paper's neighbourhood and shows its metadata; click pins it.
// Two views of the same graph: 3D (turns slowly, drag turns it) and 2D (drag moves it).
// Ctrl + wheel / pinch / the +− buttons zoom; a plain wheel scrolls the page. Full screen on request.
// The data (~0.8 MB) is only fetched once the map comes near the screen, so the page itself stays light.
(() => {
  const wrap = document.getElementById("map"), box = document.getElementById("map-wrap");
  if (!wrap || !box) return;
  document.addEventListener("map:focus", e => {
    if (window.researchMapFocus) window.researchMapFocus(e.detail.key, e.detail.inn);
    else window.researchMapPending = e.detail;          // picked up once the map has started
  });
  const start = () => { if (window.GRAPH) initResearchMap(window.GRAPH, false); };
  if (window.GRAPH) { start(); return; }
  const io = new IntersectionObserver(([e]) => {
    if (!e.isIntersecting) return;
    io.disconnect();
    const sc = document.createElement("script");
    sc.src = box.dataset.src; sc.onload = start;
    document.head.appendChild(sc);
  }, { rootMargin: "800px 0px" });
  io.observe(box);

  // full screen: the native API where there is one, otherwise (iPhone) the box simply covers the window
  const fsBtn = box.querySelector("[data-fs]");
  const isFs = () => document.fullscreenElement === box || box.classList.contains("fs");
  fsBtn?.addEventListener("click", () => {
    if (isFs()) { if (document.fullscreenElement) document.exitFullscreen().catch(() => {}); box.classList.remove("fs"); }
    else if (box.requestFullscreen && document.fullscreenEnabled) box.requestFullscreen().catch(() => box.classList.add("fs"));
    else box.classList.add("fs");
    setTimeout(() => fsBtn.setAttribute("aria-pressed", isFs()), 60);
  });
  document.addEventListener("fullscreenchange", () => fsBtn?.setAttribute("aria-pressed", isFs()));
  addEventListener("keydown", e => { if (e.key === "Escape" && box.classList.contains("fs")) { box.classList.remove("fs"); fsBtn?.setAttribute("aria-pressed", false); } });
})();

function initResearchMap(G, startIn) {
  const wrap = document.getElementById("map");
  const de = document.documentElement.lang === "de";
  const UI = de
    ? { own: "eigenes Paper", hop1: "zitiert von meinen Papern", hop2: "2. Hop", close: "Karte schließen", paper: "Paper ↗", pdf: "PDF ↗", site: "Seite ↗", gsCited: n => `Scholar: zitiert von ${n} ↗`, gsFind: "Scholar ↗", pin: "Klick für Links", pause: "Drehung anhalten", play: "Drehung fortsetzen", se: "SE RWTH", noMeta: "nur aus dem Literaturverzeichnis gelesen",
        citesN: n => `→ zitiert ${n} Arbeiten (in der Karte)`, inMine: n => `← steht in den Referenzen von ${n} meiner Paper`,
        inHop1: n => `← steht in den Referenzen von ${n} Arbeiten des 1. Hops`, cited: n => `insgesamt ${n}× zitiert (OpenAlex)`, citedGS: n => `${n}× zitiert (Google Scholar)`,
        hop1In: "zitiert meine Paper", citedOnMap: n => `← von ${n} Arbeiten in der Karte zitiert`, citesMine: n => `→ zitiert ${n} meiner Paper`, citesHop1: n => `→ zitiert ${n} Arbeiten des 1. Hops` }
    : { own: "my paper", hop1: "cited by my papers", hop2: "2nd hop", close: "Close card", paper: "paper ↗", pdf: "PDF ↗", site: "page ↗", gsCited: n => `Scholar: cited by ${n} ↗`, gsFind: "Scholar ↗", pin: "click for links", pause: "Pause rotation", play: "Resume rotation", se: "SE RWTH", noMeta: "read from a reference list only",
        citesN: n => `→ cites ${n} works (on the map)`, inMine: n => `← in the references of ${n} of my papers`,
        inHop1: n => `← in the references of ${n} first-hop works`, cited: n => `cited ${n}× in total (OpenAlex)`, citedGS: n => `cited ${n}× (Google Scholar)`,
        hop1In: "cites my papers", citedOnMap: n => `← cited by ${n} works on the map`, citesMine: n => `→ cites ${n} of my papers`, citesHop1: n => `→ cites ${n} first-hop works` };
  const TOPIC = {
    llm: ["#3b5bff", "#8c9bff"], mde: ["#0f9488", "#3cc7b8"], eis: ["#8b5cf6", "#b49cff"],
    twin: ["#e07a1f", "#f2a25c"], a11y: ["#d6336c", "#f0729b"], ga: ["#6f9a1f", "#a6cf55"], other: ["#a3a39d", "#6d6d68"],
  };
  // overlay symbols: a paper with an arrow going out (cites) or coming in (is cited); my paper / a dot citing it
  const svg = body => `<svg viewBox="0 0 17 10" aria-hidden="true">${body}</svg>`;
  const DOC = `<rect x="1" y="1" width="6" height="8" rx="0.5"/>`, OUT = `<path d="M9 5h6.5M12.5 2l3 3-3 3"/>`;
  const ICON = {
    out: svg(DOC + OUT),
    in: svg(DOC + `<path d="M16 5H9.5M12.5 2l-3 3 3 3"/>`),
    mine: svg(`<circle cx="4" cy="5" r="1.8" class="f"/><circle cx="4" cy="5" r="3.4"/>` + OUT),
    hop: svg(`<circle cx="4" cy="5" r="2" class="f"/>` + OUT),
    // the other direction: an arrow pointing at my paper / at a first-hop work
    tomine: svg(`<path d="M1 5h6.5M4.5 2l3 3-3 3"/><circle cx="13" cy="5" r="1.8" class="f"/><circle cx="13" cy="5" r="3.4"/>`),
    tohop: svg(`<path d="M1 5h6.5M4.5 2l3 3-3 3"/><circle cx="13" cy="5" r="2" class="f"/>`),
  };
  const SPIN = 0.05;                                  // rad/s: one turn in about two minutes
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- data: both layouts, each centred on the origin; swappable between the two directions ----------
  let N, L, EXT, RAD, R, CAM, sx, sy, sr, sz, order, dirIn = !!startIn;
  // centre each layout on its bounding box; keep its half extents (2D) and radius (3D) for fitting
  const centre = key => {
    const d = N[0][key].length, ax = [0, 1, 2].slice(0, d);
    const lo = ax.map(k => Math.min(...N.map(n => n[key][k]))), hi = ax.map(k => Math.max(...N.map(n => n[key][k])));
    for (const n of N) n[key] = [0, 1, 2].map(k => k < d ? n[key][k] - (lo[k] + hi[k]) / 2 : 0);
    const rs = N.map(n => Math.hypot(...n[key])).sort((a, b) => a - b);
    return { ex: (hi[0] - lo[0]) / 2, ey: (hi[1] - lo[1]) / 2, r: rs[Math.floor(rs.length * 0.99)] };   // a few outliers may touch the edge
  };
  let dims = 3;                                       // 3D unless the visitor chose 2D before
  try { if (localStorage.getItem("mapView") === "2") dims = 2; } catch (_) {}
  function setData(D) {
    N = D.nodes.map((n, i) => ({ ...n, i, out: [], inn: [] }));
    for (const [a, b] of D.links) { N[a].out.push(b); N[b].inn.push(a); }
    L = D.links;
    EXT = { 2: centre("p2"), 3: centre("p3") };
    RAD = { 2: EXT[2].r, 3: EXT[3].r };
    R = RAD[dims]; CAM = R * 3;                       // camera distance: mild perspective
    // projected positions of the last frame (screen px), used for picking
    sx = new Float32Array(N.length); sy = new Float32Array(N.length); sr = new Float32Array(N.length); sz = new Float32Array(N.length);
    order = N.map(n => n.i);
  }
  setData(G);

  // ---------- state ----------
  const canvas = wrap.querySelector("canvas"), ctx = canvas.getContext("2d");
  const tip = wrap.querySelector(".map-tip");
  let W = 0, H = 0, dpr = 1, base = 1, shiftX = 0, dotK = 1;
  let yaw = 0.6, pitch = -0.25, zoom = 1, ox = 0, oy = 0;
  let hover = null, pinned = null, showHop2 = true, onScreen = true, holdUntil = 0;
  const off = new Set();                              // topics switched off
  let only = null;                                    // legend: "own" = only my papers, "se" = only SE RWTH work
  const visible = n => (showHop2 || n.h < 2) && !off.has(n.g) && (only === "own" ? n.h === 0 : only === "se" ? !!n.se : true);
  const focus = () => pinned ?? hover;
  const near = n => new Set([n.i, ...n.out, ...n.inn]);

  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const dark = () => document.documentElement.dataset.theme === "dark";
  let C = {};
  const readColours = () => { C = { ink: css("--ink"), ink2: css("--ink-2"), ink3: css("--ink-3"), line: dark() ? "255,255,255" : "20,20,20", accent: css("--accent") }; };

  const resize = () => {
    dpr = Math.min(devicePixelRatio || 1, 2);
    const r = wrap.getBoundingClientRect();
    W = r.width; H = r.height;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    // dot size follows the map size only, not the layout's extent: the same paper looks the same in
    // 2D and 3D and in both directions
    dotK = Math.max(0.5, Math.min(1, Math.min(W, H) / 900));
    // as tight as possible: the content column already has its margins
    const pad = 6, lab = W >= 600 ? 44 : 0;          // a little room on the right for the labels
    if (dims === 2) {
      base = Math.min((W - 2 * pad - lab) / (2 * EXT[2].ex), (H - 2 * pad) / (2 * EXT[2].ey));
      shiftX = -lab / 2;
    } else {                                          // turning: the cloud must fit at every angle
      base = (Math.min(W - lab, H) - 2 * pad) / (2 * R);
      shiftX = -lab / 2;
    }
    draw();
  };
  const fit = () => { zoom = 1; ox = oy = 0; draw(); };
  function setView(d) {
    dims = d; R = RAD[d]; CAM = R * 3;
    try { localStorage.setItem("mapView", String(d)); } catch (_) {}
    document.querySelectorAll("[data-view]").forEach(b => b.setAttribute("aria-pressed", b.dataset.view === String(d)));
    canvas.style.cursor = d === 3 ? "grab" : "move";
    resize(); fit(); showPause(); wake();
  }

  // ---------- projection + drawing ----------
  const rad = n => n.h === 0 ? n.r * 0.7 : n.r;          // my papers a little smaller than their layout size
  function project() {
    const cy = Math.cos(yaw), syw = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    const k = base * zoom, kr = dotK * Math.pow(zoom, 0.35), cx0 = W / 2 + shiftX + ox, cy0 = H / 2 + oy;   // dots grow slower than the gaps
    for (const n of N) {
      if (dims === 2) {                               // flat: no turning, no perspective
        const [x, y] = n.p2;
        sx[n.i] = cx0 + x * k; sy[n.i] = cy0 + y * k; sr[n.i] = Math.max(0.7, rad(n) * kr); sz[n.i] = 0;
        continue;
      }
      const [x, y, z] = n.p3;
      const x1 = x * cy + z * syw, z1 = -x * syw + z * cy;
      const y2 = y * cp - z1 * sp, z2 = y * sp + z1 * cp;
      const s = CAM / (CAM + z2);
      sx[n.i] = cx0 + x1 * s * k; sy[n.i] = cy0 + y2 * s * k; sr[n.i] = Math.max(0.7, rad(n) * s * kr); sz[n.i] = z2;
    }
  }
  const depth = i => dims === 2 ? 1 : 1 - 0.55 * (sz[i] + R) / (2 * R);   // 1 in front … 0.45 at the back

  function draw() {
    if (!W) return;
    if (!C.ink) readColours();
    project();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const f = focus(), nb = f ? near(f) : null;
    // links, batched into one path per kind (fast enough to redraw every frame)
    ctx.lineWidth = 0.6;
    for (const [kind, alpha] of [[2, 0.05], [1, 0.07], [0, 0.15]]) {
      ctx.beginPath();
      for (const [a, b] of L) {
        const A = N[a], B = N[b];
        if (!visible(A) || !visible(B)) continue;
        // by the hops it joins, whatever its direction: touching my paper = 0, reaching the second hop = 2
        if ((A.h === 2 || B.h === 2 ? 2 : A.h === 0 || B.h === 0 ? 0 : 1) !== kind) continue;
        ctx.moveTo(sx[a], sy[a]); ctx.lineTo(sx[b], sy[b]);
      }
      ctx.strokeStyle = `rgba(${C.line},${f ? alpha * 0.35 : alpha})`;
      ctx.stroke();
    }
    ctx.beginPath();                                  // links between my own papers stand out
    for (const [a, b] of L) if (N[a].h === 0 && N[b].h === 0 && visible(N[a]) && visible(N[b])) { ctx.moveTo(sx[a], sy[a]); ctx.lineTo(sx[b], sy[b]); }
    ctx.strokeStyle = C.accent; ctx.globalAlpha = f ? 0.15 : 0.45; ctx.lineWidth = 1.1; ctx.stroke(); ctx.globalAlpha = 1;
    if (f) {                                          // the focused paper's own links on top
      ctx.beginPath();
      for (const j of [...f.out, ...f.inn]) if (visible(N[j])) { ctx.moveTo(sx[f.i], sy[f.i]); ctx.lineTo(sx[j], sy[j]); }
      ctx.strokeStyle = C.accent; ctx.globalAlpha = 0.6; ctx.lineWidth = 0.9; ctx.stroke(); ctx.globalAlpha = 1;
    }
    // nodes back to front
    if (dims === 3) order.sort((a, b) => sz[b] - sz[a]); else order.sort((a, b) => N[b].h - N[a].h);
    for (const i of order) {
      const n = N[i];
      if (!visible(n)) continue;
      const dim = nb && !nb.has(i);
      // brightness tells mine from the rest: my papers in full colour, what they cite washed out
      // towards the page colour, the second hop more so (the hovered neighbourhood comes forward)
      const hot = nb && nb.has(i) && n.h > 0;
      const tone = n.h === 0 ? 1 : n.h === 2 ? 0.32 : n.raw ? 0.45 : 0.62;
      ctx.globalAlpha = Math.min(1, tone * (hot ? 1.5 : 1)) * (n.h === 0 ? 0.65 + 0.35 * depth(i) : depth(i)) * (dim ? 0.18 : 1);
      ctx.fillStyle = TOPIC[n.g][dark() ? 1 : 0];
      ctx.beginPath(); ctx.arc(sx[i], sy[i], sr[i], 0, 6.2832); ctx.fill();
      if (n.h === 0) {                                // my papers: a firm ring in the ink colour
        ctx.lineWidth = Math.max(1, sr[i] * 0.12);
        ctx.strokeStyle = C.ink2;
        ctx.beginPath(); ctx.arc(sx[i], sy[i], sr[i] + Math.max(2, sr[i] * 0.32), 0, 6.2832); ctx.stroke();
      } else if (n.se) {                              // ring: RWTH Software Engineering — fine, grey, a little apart
        ctx.lineWidth = 0.8;
        ctx.strokeStyle = C.ink3;
        ctx.beginPath(); ctx.arc(sx[i], sy[i], sr[i] + Math.max(1.6, sr[i] * 0.3), 0, 6.2832); ctx.stroke();
      }
    }
    ctx.globalAlpha = 1;
    // labels for my papers (and the focused node); on small screens only once zoomed in
    const labels = W >= 600 || zoom > 1.6;
    ctx.font = `11px "IBM Plex Mono", monospace`;
    ctx.textBaseline = "middle";
    for (const n of N) {
      if (!visible(n) || !(n === f || (n.h === 0 && labels))) continue;
      if (nb && !nb.has(n.i)) continue;
      ctx.globalAlpha = n === f ? 1 : 0.5 + 0.5 * depth(n.i);
      ctx.fillStyle = n === f ? C.ink : C.ink2;
      ctx.fillText(n.k || "", sx[n.i] + sr[n.i] * 1.4 + 5, sy[n.i]);
    }
    ctx.globalAlpha = 1;
  }

  // ---------- slow turn ----------
  let last = 0, raf = 0;
  let paused = reduced;
  try { if (localStorage.getItem("mapSpin") === "off") paused = true; } catch (_) {}
  const pauseBtn = wrap.querySelector(".map-pause");
  const showPause = () => {
    if (!pauseBtn) return;
    pauseBtn.hidden = dims !== 3;
    pauseBtn.textContent = paused ? "▶" : "❚❚";
    pauseBtn.setAttribute("aria-label", paused ? UI.play : UI.pause);
    pauseBtn.title = paused ? UI.play : UI.pause;
  };
  pauseBtn?.addEventListener("click", () => {
    paused = !paused;
    try { localStorage.setItem("mapSpin", paused ? "off" : "on"); } catch (_) {}
    showPause(); wake();
  });
  const turning = () => dims === 3 && !paused && onScreen && !document.hidden && !focus() && !drag && performance.now() > holdUntil;
  function frame(t) {
    raf = 0;
    if (last) yaw += SPIN * Math.min(t - last, 100) / 1000;
    last = t;
    draw();
    if (turning()) raf = requestAnimationFrame(frame); else last = 0;
  }
  const wake = () => { if (!raf && turning()) raf = requestAnimationFrame(frame); };
  const holdFor = ms => { holdUntil = performance.now() + ms; setTimeout(wake, ms + 20); };

  // ---------- picking ----------
  const pick = (px, py) => {
    let best = null, bz = Infinity;
    for (const n of N) {
      if (!visible(n)) continue;
      const i = n.i, d = Math.hypot(sx[i] - px, sy[i] - py);
      if (d <= sr[i] + 4 && sz[i] < bz) { best = n; bz = sz[i]; }   // the one in front wins
    }
    return best;
  };

  // ---------- overlay ----------
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const ownCount = n => n.inn.filter(i => N[i].h === 0).length;
  const hop1Count = n => n.inn.filter(i => N[i].h === 1).length;
  function showTip(n, px, py) {
    if (!n) { tip.hidden = true; return; }
    // my own work: a thesis says what kind it is (flag in pubs.js) instead of "my paper"
    const flag = n.h === 0 && (window.PUBS || []).find(p => p.key === n.k)?.flag;
    const own = (de ? { Dissertation: "Dissertation", MastersThesis: "Masterarbeit", BachelorsThesis: "Bachelorarbeit" }
                    : { Dissertation: "dissertation", MastersThesis: "master’s thesis", BachelorsThesis: "bachelor’s thesis" })[flag] || UI.own;
    const kind = n.h === 0 ? own : n.h === 1 ? (dirIn ? UI.hop1In : UI.hop1) : UI.hop2;
    const links = [];
    if (n.d) links.push([UI.paper, `https://doi.org/${n.d}`]);
    if (n.u && !n.d) links.push([UI.site, n.u]);
    if (n.pdf) links.push([UI.pdf, n.pdf]);
    if (n.gs) links.push([UI.gsCited(n.c), `https://scholar.google.com/scholar?cites=${n.gs}`]);
    else if (n.t && !n.raw) links.push([UI.gsFind, `https://scholar.google.com/scholar?q=${encodeURIComponent('"' + n.t + '"')}`]);
    // direction as small symbols (the sentence is the tooltip): ▯→ what it cites (drawn on the map),
    // ▯← how often it is cited (a count only), ◉→ / •→ how many of my / first-hop papers cite it
    const stat = (icon, n, title, src = "") => `<span title="${esc(title)}">${ICON[icon]}${n}${src ? `<small>${src}</small>` : ""}</span>`;
    const cited = n.raw ? "" : stat("in", n.c, n.cs ? UI.citedGS(n.c) : UI.cited(n.c), n.cs ? "GS" : "OA");
    const outTo = h => n.out.filter(i => N[i].h === h).length;
    const by = dirIn
      ? (n.h === 0 ? stat("in", n.inn.length, UI.citedOnMap(n.inn.length))
        : n.h === 1 ? stat("tomine", outTo(0), UI.citesMine(outTo(0))) : stat("tohop", outTo(1), UI.citesHop1(outTo(1))))
      : (n.h === 0 ? stat("out", n.out.length, UI.citesN(n.out.length))
        : n.h === 1 ? stat("mine", ownCount(n), UI.inMine(ownCount(n))) : stat("hop", hop1Count(n), UI.inHop1(hop1Count(n))));
    tip.innerHTML = (pinned === n ? `<button type="button" class="tip-x" aria-label="${UI.close}" title="${UI.close}">×</button>` : "") +
      `<div class="mono kind"><i style="background:${TOPIC[n.g][dark() ? 1 : 0]}"></i>${esc(document.querySelector(`[data-topic="${n.g}"] span`)?.textContent || n.g)} · ${kind}${n.se ? " · " + UI.se : ""}</div>` +
      `<div class="t">${esc(n.t)}</div>` +
      (n.a ? `<div class="a">${esc(n.a)}</div>` : "") +
      `<div class="mono m">${[n.y, esc(n.v)].filter(Boolean).join(" · ")}</div>` +
      `<div class="mono stats">${by}${cited}</div>` +
      (n.raw ? `<div class="mono m">${UI.noMeta}</div>` : "") +
      (!links.length ? "" : pinned === n
        ? `<div class="mono links">${links.map(([l, u]) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(l)}</a>`).join("")}</div>`
        : `<div class="mono hint">${UI.pin}</div>`);
    tip.hidden = false;
    tip.classList.toggle("pinned", pinned === n);
    // keep the card inside the map
    const r = tip.getBoundingClientRect(), pad = 14;
    let x = px + pad, y = py + pad;
    if (x + r.width > W - 8) x = px - r.width - pad;
    if (y + r.height > H - 8) y = py - r.height - pad;
    placeTip(x, y);
  }
  let tx = 0, ty = 0;
  const placeTip = (x, y) => {
    const r = tip.getBoundingClientRect();
    tx = Math.max(8, Math.min(x, W - r.width - 8)); ty = Math.max(8, Math.min(y, H - r.height - 8));
    tip.style.transform = `translate(${tx}px, ${ty}px)`;
  };
  const unpin = () => { pinned = hover = null; tip.hidden = true; tip.classList.remove("pinned"); draw(); wake(); };
  // a pinned card can be closed (×) and dragged out of the way
  tip.addEventListener("click", e => { if (e.target.closest(".tip-x")) unpin(); });
  let tipDrag = null;
  tip.addEventListener("pointerdown", e => {
    if (!tip.classList.contains("pinned") || e.target.closest("a, button")) return;
    tipDrag = { x: e.clientX - tx, y: e.clientY - ty };
    tip.setPointerCapture(e.pointerId); tip.classList.add("dragging");
  });
  tip.addEventListener("pointermove", e => { if (tipDrag) placeTip(e.clientX - tipDrag.x, e.clientY - tipDrag.y); });
  const dropTip = () => { tipDrag = null; tip.classList.remove("dragging"); };
  tip.addEventListener("pointerup", dropTip);
  tip.addEventListener("pointercancel", dropTip);

  // ---------- interaction: drag turns, pinch / Ctrl+wheel / buttons zoom ----------
  const pts = new Map();
  let drag = null, pinch = null, moved = false;
  function zoomAt(px, py, f) {
    const z = Math.min(Math.max(zoom * f, 0.4), 30);
    f = z / zoom;
    ox = (px - W / 2) - ((px - W / 2) - ox) * f; oy = (py - H / 2) - ((py - H / 2) - oy) * f; zoom = z;
    draw();
  }
  canvas.addEventListener("pointerdown", e => {
    pts.set(e.pointerId, [e.offsetX, e.offsetY]);
    moved = false;
    if (pts.size === 2) {
      const [a, b] = [...pts.values()];
      pinch = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), z: zoom }; drag = null;
    } else {
      drag = { x: e.offsetX, y: e.offsetY };
      try { canvas.setPointerCapture(e.pointerId); } catch (_) {}
    }
  });
  canvas.addEventListener("pointermove", e => {
    if (pts.has(e.pointerId)) {
      pts.set(e.pointerId, [e.offsetX, e.offsetY]);
      if (pts.size === 2 && pinch) {
        const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]);
        zoomAt((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, pinch.z * d / pinch.d / zoom);
        moved = true; return;
      }
      if (drag) {
        const dx = e.offsetX - drag.x, dy = e.offsetY - drag.y;
        if (Math.abs(dx) + Math.abs(dy) > 3) moved = true;
        if (moved) {
          if (dims === 3) { yaw += dx * 0.006; pitch = Math.max(-1.4, Math.min(1.4, pitch + dy * 0.006)); }
          else { ox += dx; oy += dy; }
          drag = { x: e.offsetX, y: e.offsetY }; tip.hidden = true; draw();
        }
      }
      return;
    }
    if (pinned || e.pointerType === "touch") return;
    const n = pick(e.offsetX, e.offsetY);
    canvas.style.cursor = n ? "pointer" : dims === 3 ? "grab" : "move";
    if (n !== hover) { hover = n; if (!n) holdFor(1500); draw(); }
    showTip(n, e.offsetX, e.offsetY);
  });
  const up = e => {
    pts.delete(e.pointerId);
    if (pts.size < 2) pinch = null;
    if (e.type === "pointerup" && !moved && drag) {
      const n = pick(e.offsetX, e.offsetY);
      pinned = n && n !== pinned ? n : null;
      hover = pinned;
      draw();
      showTip(pinned, e.offsetX, e.offsetY);
    }
    if (!pts.size) { drag = null; holdFor(2500); }
  };
  canvas.addEventListener("pointerup", up);
  canvas.addEventListener("pointercancel", up);
  canvas.addEventListener("pointerleave", () => { if (!pinned) { hover = null; tip.hidden = true; draw(); wake(); } });
  // only Ctrl/⌘ + wheel zooms (trackpad pinch arrives as that too); a plain wheel scrolls the page
  canvas.addEventListener("wheel", e => {
    if (!e.ctrlKey && !e.metaKey) return;
    e.preventDefault(); tip.hidden = true;
    zoomAt(e.offsetX, e.offsetY, Math.exp(-Math.max(-100, Math.min(100, e.deltaY)) * 0.002));
  }, { passive: false });
  canvas.addEventListener("dblclick", fit);
  addEventListener("keydown", e => { if (e.key === "Escape" && pinned) { pinned = hover = null; tip.hidden = true; draw(); wake(); } });

  // legend: topics toggle, second hop toggle, zoom, fit
  document.querySelectorAll("[data-topic]").forEach(b => b.addEventListener("click", () => {
    const t = b.dataset.topic, on = off.has(t);
    on ? off.delete(t) : off.add(t);
    b.setAttribute("aria-pressed", on);
    draw();
  }));
  const hopBtn = document.querySelector("[data-hop2]");
  hopBtn?.addEventListener("click", () => { showHop2 = !showHop2; hopBtn.setAttribute("aria-pressed", showHop2); draw(); });
  document.querySelectorAll("[data-zoom]").forEach(b => b.addEventListener("click", () => zoomAt(W / 2, H / 2, b.dataset.zoom === "in" ? 1.4 : 1 / 1.4)));
  document.querySelector("[data-fit]")?.addEventListener("click", fit);
  document.querySelectorAll("[data-only]").forEach(b => b.addEventListener("click", () => {
    only = only === b.dataset.only ? null : b.dataset.only;        // one at a time; again = show all
    document.querySelectorAll("[data-only]").forEach(x => x.setAttribute("aria-pressed", x.dataset.only === only));
    if (focus() && !visible(focus())) { pinned = hover = null; tip.hidden = true; }
    draw();
  }));
  document.querySelectorAll("[data-view]").forEach(b => b.addEventListener("click", () => setView(+b.dataset.view)));
  const box = document.getElementById("map-wrap");
  const setDir = inn => {
    dirIn = inn;
    setData(inn ? window.GRAPH_IN : window.GRAPH);
    pinned = hover = null; tip.hidden = true;
    document.querySelectorAll("[data-dir]").forEach(b => b.setAttribute("aria-pressed", (b.dataset.dir === "in") === inn));
    box.querySelectorAll("[data-lead]").forEach(p => p.hidden = (p.dataset.lead === "in") !== inn);
    resize(); fit(); wake();
  };
  const switchDir = (inn, then) => {
    if (inn === dirIn) return then?.();
    if (inn ? window.GRAPH_IN : window.GRAPH) { setDir(inn); return then?.(); }
    const sc = document.createElement("script");
    sc.src = inn ? box.dataset.srcIn : box.dataset.src; sc.onload = () => { setDir(inn); then?.(); };
    document.head.appendChild(sc);
  };
  document.querySelectorAll("[data-dir]").forEach(b => b.addEventListener("click", () => switchDir(b.dataset.dir === "in")));
  // from the publication list: show one of my papers — in the middle, pinned, its card open
  window.researchMapFocus = (key, inn) => !W ? setTimeout(() => window.researchMapFocus(key, inn), 60) : switchDir(!!inn, () => {
    only = null; off.clear(); showHop2 = true;
    document.querySelectorAll("[data-only]").forEach(x => x.setAttribute("aria-pressed", false));
    document.querySelectorAll("[data-topic]").forEach(x => x.setAttribute("aria-pressed", true));
    hopBtn?.setAttribute("aria-pressed", true);
    const n = N.find(x => x.h === 0 && x.k === key);
    if (!n) return;
    zoom = 1.6; ox = oy = 0; draw();
    ox = W / 2 - sx[n.i]; oy = H / 2 - sy[n.i];
    pinned = hover = n; draw();
    showTip(n, sx[n.i], sy[n.i]);
  });
  if (window.researchMapPending) { const p = window.researchMapPending; window.researchMapPending = null; window.researchMapFocus(p.key, p.inn); }
  document.querySelectorAll("[data-view]").forEach(b => b.setAttribute("aria-pressed", b.dataset.view === String(dims)));
  showPause();

  // theme switches redraw with the new colours; turning only while the map is on screen
  new MutationObserver(() => { readColours(); draw(); }).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  new ResizeObserver(() => { resize(); wake(); }).observe(wrap);
  new IntersectionObserver(([e]) => { onScreen = e.isIntersecting; wake(); }).observe(wrap);
  document.addEventListener("visibilitychange", wake);
  document.fonts?.ready.then(draw);
}
