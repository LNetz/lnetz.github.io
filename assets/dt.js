// Interactive figures of the Digital Twins article (research-dt.html, built by _build/dt.py + dt_figs.py).
// All states are precomputed at build time and shipped as data-json; this script only swaps and highlights.
//   dt1 — model → shadow → twin: how automatically does data flow? (presets)
//   dt2 — anatomy of a twin: clause ↔ part (hover / tap), "Is it a twin?" presets
//   dt3 — one machine's data, three shadows (purpose presets)
//   dt4 — the self-adaptive loop, automatic or with an operator approving (stepper)
//   dt5 — who builds the twin: platform engineer, twin designer, domain expert (stepper)
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const json = fig => JSON.parse(fig.dataset.json);
  const press = (buttons, on) => buttons.forEach(b => b.setAttribute("aria-pressed", String(b === on)));
  const whenSeen = (el, fn) => {
    if (!("IntersectionObserver" in window)) return fn();
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { io.disconnect(); fn(); } }, { threshold: .4 });
    io.observe(el);
  };

  // ---------------- a stepper (as in mde.js), with an optional hold: autoplay stops at a step until released ----------------
  function stepper(fig, count, render, delay, hold = () => false) {
    const play = fig.querySelector(".play"), range = fig.querySelector("input.step"), words = json(fig).words;
    let k = 0, timer = null;
    range.max = count - 1;
    const show = i => { k = i; range.value = i; render(i); };
    const stop = () => { clearTimeout(timer); timer = null; play.textContent = k >= count - 1 ? "↺" : "▶"; play.setAttribute("aria-label", words.play); };
    const tick = () => {
      if (k >= count - 1 || hold(k)) return stop();
      show(k + 1);
      timer = setTimeout(tick, delay);
    };
    const start = () => { if (k >= count - 1) show(0); play.textContent = "❚❚"; play.setAttribute("aria-label", words.pause); timer = setTimeout(tick, delay); };
    play.addEventListener("click", () => (timer ? stop() : start()));
    range.addEventListener("input", () => { stop(); show(+range.value); stop(); });
    show(0); stop();
    return { start, show, get k() { return k; }, render: () => render(k) };
  }

  // ---------------- dt1: the ladder ----------------
  function ladder(fig) {
    const { states, words } = json(fig);
    const buttons = [...fig.querySelectorAll(".d1-presets button")];
    const up = fig.querySelector('[data-a="up"]'), down = fig.querySelector('[data-a="down"]');
    const label = fig.querySelector(".dl-label"), quote = fig.querySelector(".dl-quote"), src = fig.querySelector(".dl-src");
    const set = i => {
      const s = states[i];
      press(buttons, buttons[i]);
      for (const [g, mode] of [[up, s.up], [down, s.down]]) {
        g.className.baseVal = `arr ${g.dataset.a} ${mode}`;
        g.querySelector(".alab").textContent = words[mode];
      }
      label.textContent = s.label; quote.textContent = s.quote; src.innerHTML = s.src;
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => set(i)));
    set(1);
  }

  // ---------------- dt2: anatomy ----------------
  function anatomy(fig) {
    const { presets } = json(fig);
    const parts = [...fig.querySelectorAll(".anat .part")], chips = [...fig.querySelectorAll(".anat-chips .chip")];
    const buttons = [...fig.querySelectorAll(".d1-presets button")], verdict = fig.querySelector(".anat-verdict");
    const keysOf = el => el.dataset.k.split(" ");
    const light = k => {
      parts.forEach(p => p.classList.toggle("hi", !!k && keysOf(p).includes(k)));
      chips.forEach(c => c.classList.toggle("hi", !!k && c.dataset.k === k));
    };
    chips.forEach(c => {
      c.addEventListener("pointerenter", () => light(c.dataset.k));
      c.addEventListener("focus", () => light(c.dataset.k));
      c.addEventListener("click", () => light(c.dataset.k));
      c.addEventListener("pointerleave", () => light(null));
      c.addEventListener("blur", () => light(null));
    });
    parts.forEach(p => {
      p.addEventListener("pointerenter", () => light(keysOf(p)[0]));
      p.addEventListener("pointerleave", () => light(null));
    });
    const set = i => {
      const on = new Set(presets[i].on);
      press(buttons, buttons[i]);
      parts.forEach(p => p.classList.toggle("off", !keysOf(p).some(k => on.has(k))));
      verdict.textContent = presets[i].verdict;
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => set(i)));
    set(buttons.length - 1);
  }

  // ---------------- dt3: shadows ----------------
  function shadows(fig) {
    const { states } = json(fig);
    const grid = fig.querySelector(".sh-grid"), buttons = [...fig.querySelectorAll(".d1-presets button")];
    const facts = fig.querySelector(".sh-facts"), code = fig.querySelector(".sh-card pre"), note = fig.querySelector(".sh-note"), src = fig.querySelector(".sh-card .dl-src");
    const set = i => {
      const s = states[i];
      press(buttons, buttons[i]);
      grid.className = `sh-grid s${i + 1}`;
      facts.innerHTML = s.facts; code.innerHTML = s.code; note.textContent = s.note; src.innerHTML = s.src;
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => set(i)));
    set(0);
  }

  // ---------------- dt4: the loop ----------------
  function loop(fig) {
    const { steps, hold, words } = json(fig);
    const comps = [...fig.querySelectorAll(".loop .lp")], conns = [...fig.querySelectorAll(".loop .lc")];
    const say = fig.querySelector(".lp-say"), code = fig.querySelector(".lp-code"), where = fig.querySelector(".where");
    const cockpit = fig.querySelector(".lp-cockpit"), msg = fig.querySelector(".lp-msg"), approve = fig.querySelector(".approve");
    const modes = [...fig.querySelectorAll("[data-m]")];
    let mode = "auto", approved = false;
    const render = i => {
      const s = steps[i];
      comps.forEach(c => c.classList.toggle("on", s.c.includes(c.dataset.c)));
      conns.forEach(c => c.classList.toggle("on", s.l.includes(c.dataset.c)));
      say.textContent = s.say;
      code.innerHTML = s.code;
      where.textContent = `${words.step} ${i + 1} ${words.of} ${steps.length}`;
      const waiting = mode === "human" && i === hold;
      cockpit.className = "lp-cockpit" + (i === hold ? (mode === "human" ? " ask" : " skip") : "");
      msg.textContent = i === hold ? (mode === "human" ? words.human : words.auto) : "";
      approve.disabled = !waiting;
    };
    const st = stepper(fig, steps.length, render, 1500, i => mode === "human" && i === hold && !approved);
    approve.addEventListener("click", () => { approved = true; st.show(hold + 1); approved = false; st.start(); });
    modes.forEach(b => b.addEventListener("click", () => { mode = b.dataset.m; press(modes, b); st.render(); }));
    if (!reduce) whenSeen(fig, st.start);
  }

  // ---------------- dt5: roles ----------------
  function roles(fig) {
    const { steps } = json(fig);
    const quads = [...fig.querySelectorAll(".roles .q")];
    const title = fig.querySelector(".ro-title"), text = fig.querySelector(".ro-text"), panel = fig.querySelector(".ro-html");
    const where = fig.querySelector(".where"), words = json(fig).words;
    const render = i => {
      const s = steps[i];
      quads.forEach(q => q.classList.toggle("on", s.q.includes(q.dataset.q)));
      title.textContent = s.title; text.textContent = s.text; panel.innerHTML = s.html;
      where.textContent = `${words.step} ${i + 1} ${words.of} ${steps.length}`;
    };
    stepper(fig, steps.length, render, 4000);
  }

  const kinds = { dt1: ladder, dt2: anatomy, dt3: shadows, dt4: loop, dt5: roles };
  document.querySelectorAll("figure.demo[data-demo]").forEach(fig => {
    try { kinds[fig.dataset.demo]?.(fig); } catch (e) { console.error(e); }
  });
})();
