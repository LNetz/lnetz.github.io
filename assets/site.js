// Shared behaviour for all pages. Each block only runs if its markup exists.

// ---- UI strings for the page language (<html lang="…">) ----
const I18N = {
  en: { theme: { light: "light", dark: "dark", auto: "auto" }, themeLabel: "Theme: ", themeHint: " — click to change",
        pubs: "publications", open: "Open photo: ",
        slideshow: "slideshow", pause: "pause", fs: "full screen", exitFs: "exit full screen",
        flags: { Article: "Article", Dissertation: "Dissertation" } },
  de: { theme: { light: "hell", dark: "dunkel", auto: "auto" }, themeLabel: "Darstellung: ", themeHint: " — klicken zum Wechseln",
        pubs: "Publikationen", open: "Foto öffnen: ",
        slideshow: "Diashow", pause: "Pause", fs: "Vollbild", exitFs: "Vollbild beenden",
        flags: { Article: "Artikel", Dissertation: "Dissertation" } },
};
const UI = I18N[document.documentElement.lang] || I18N.en;

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

  root.innerHTML = years.map(y => `
    <div class="year">
      <div class="y mono">${y}</div>
      <ol class="pubs">${pubs.filter(p => p.year === y).map(p => `
        <li data-tags="${p.tags.join(" ")}">
          <span class="key mono">${p.key}</span>
          <div>
            <div class="t">${esc(p.title)}${p.flag ? `<span class="flag mono">${UI.flags[p.flag] || p.flag}</span>` : ""}</div>
            <div class="a">${me(p.authors)}</div>
            <div class="v mono">${esc(p.venue)}</div>
            <div class="plinks mono">${links(p)}</div>
          </div>
        </li>`).join("")}
      </ol>
    </div>`).join("");

  const count = document.getElementById("pub-count");
  if (count) count.textContent = `${PUBS.length} ${UI.pubs}`;

  document.querySelectorAll(".filters button").forEach(btn => {
    const f = btn.dataset.f;
    const n = f === "all" ? PUBS.length : PUBS.filter(p => p.tags.includes(f)).length;
    btn.insertAdjacentHTML("beforeend", `<span class="n">${n}</span>`);
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filters button").forEach(b => b.setAttribute("aria-pressed", b === btn));
      root.querySelectorAll("li").forEach(li => li.hidden = f !== "all" && !li.dataset.tags.split(" ").includes(f));
      root.querySelectorAll(".year").forEach(y => y.classList.toggle("empty", !y.querySelector("li:not([hidden])")));
    });
  });
})();

// ---- photo lightbox with a noise-dissolve between photos ----
// Moving to the next/previous photo sweeps a dissolve front across the frame (WebGL):
// from the right when moving forward, from the left when moving back. Bright areas of the
// incoming photo burn through first, so the front follows its shapes; an fbm noise
// field frays the front into tatters and both frames drift slightly sideways against
// each other. Adapted from the "Morph Gallery" shader, but photos are shown whole
// (contain, letterboxed in the page colour) instead of cropped.
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
    uniform float u_progress, u_fromAspect, u_toAspect, u_scale, u_dir, u_edge, u_drift;
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
    // "contain": the whole photo, letterboxed in the page colour
    vec4 photo(sampler2D tex, vec2 q, float imgAspect) {
      float ca = u_res.x / u_res.y;
      vec2 s = ca > imgAspect ? vec2(ca / imgAspect, 1.0) : vec2(1.0, imgAspect / ca);
      vec2 t = (q - 0.5) * s + 0.5;
      if (t.x < 0.0 || t.y < 0.0 || t.x > 1.0 || t.y > 1.0) return vec4(u_bg, 0.0);   // alpha 0 = letterbox
      return vec4(texture2D(tex, t).rgb, 1.0);
    }
    void main() {
      float adjusted = u_progress * (1.0 + 2.0 * u_edge) - u_edge;
      vec2 nuv = (uv - 0.5) * u_res / min(u_res.x, u_res.y);   // round noise in any canvas shape
      float n = fbm(nuv * u_scale + vec2(u_progress * u_dir, 0.0)) * 0.5 + 0.5;
      // side to side: the dissolve front sweeps across the frame — from the right when moving
      // forward, from the left when moving back. Within the front the incoming photo's bright
      // areas burn through first (so it follows shapes and silhouettes), and the noise frays it.
      // Letterbox areas get a neutral grey so the noise, not the page colour, decides there.
      float sweep = u_dir > 0.0 ? 1.0 - uv.x : uv.x;
      vec4 incoming = photo(u_to, uv, u_toAspect);
      float lum = incoming.a > 0.5 ? length(incoming.rgb) : 0.866;
      float shape = smoothstep(0.0, 2.0, lum + n);
      float t = sweep * 0.6 + shape * 0.4;
      float mixF = 1.0 - smoothstep(adjusted - u_edge, adjusted + u_edge, t);
      // horizontal drift: the outgoing photo slides away, the incoming one settles in
      vec4 a = photo(u_from, uv + vec2(n * u_progress * u_drift * u_dir, 0.0), u_fromAspect);
      vec4 b = photo(u_to, uv + vec2(n * (1.0 - u_progress) * -0.5 * u_drift * u_dir, 0.0), u_toAspect);
      gl_FragColor = vec4(mix(a.rgb, b.rgb, mixF), 1.0);
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
      for (const k of ["from", "to", "progress", "fromAspect", "toAspect", "scale", "dir", "edge", "drift", "res", "bg"])
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

  // Uploads both photos and sets up the shader; returns draw(progress 0..1) and dispose().
  // Used by timed transitions (morph) and by the finger-driven swipe alike. Throws on
  // tainted images (file:// previews) — callers fall back to a cross-fade.
  const prepare = (fromIm, toIm, dir) => {
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
    gl.uniform1f(U.scale, 3.5);
    gl.uniform1f(U.dir, dir);
    gl.uniform1f(U.edge, 0.15);
    gl.uniform1f(U.drift, 0.15);
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

  const morph = async (fromIm, toIm, dir) => {
    const h = prepare(fromIm, toIm, dir);
    await run(h, 0, 1, DURATION);
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
