// Interactive figures of the Digital Twins article (research-dt.html, built by _build/dt.py + dt_figs.py).
// All states are precomputed at build time and shipped as data-json; this script only swaps and highlights.
// Shared helpers (stepper, height lock, autoplay rule, chips) come from assets/demo-common.js (window.SiteDemo).
//   dt1 — model → shadow → twin on a car: how automatically does data flow? (presets)
//   dt2 — anatomy of a twin: clause ↔ part (hover / tap), "Is it a twin?" presets
//   dt3 — one car's raw telemetry, three shadows as database views (purpose presets)
//   dt4 — the injection-moulding twin's loop, automatic or with an operator approving in the cockpit (stepper)
//   dt5 — who builds the twin: platform engineer, twin designer, domain expert (stepper)
(() => {
  const D = window.SiteDemo;
  const json = fig => JSON.parse(fig.dataset.json);

  // ---------------- dt1: the ladder ----------------
  function ladder(fig) {
    const { states, words } = json(fig);
    const buttons = [...fig.querySelectorAll(".d1-presets button")];
    const up = fig.querySelector('[data-a="up"]'), down = fig.querySelector('[data-a="down"]');
    const out = fig.querySelector(".dl-out"), label = fig.querySelector(".dl-label"), quote = fig.querySelector(".dl-quote"), src = fig.querySelector(".dl-src");
    let cur = 1;
    const text = i => { const s = states[i]; label.textContent = s.label; quote.textContent = s.quote; src.innerHTML = s.src; };
    const set = i => {
      cur = i;
      const s = states[i];
      D.press(buttons, buttons[i]);
      for (const [g, mode] of [[up, s.up], [down, s.down]]) {
        g.setAttribute("class", `arr ${g.dataset.a} ${mode}`);
        g.querySelector(".alab").textContent = words[mode];
      }
      text(i);
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => set(i)));
    set(cur);
    D.lock(out, states.length, text, () => cur);
  }

  // ---------------- dt2: anatomy ----------------
  function anatomy(fig) {
    const { presets } = json(fig);
    const parts = [...fig.querySelectorAll(".anat .part")], clauses = [...fig.querySelectorAll(".anat-def .cl")];
    const buttons = [...fig.querySelectorAll(".d1-presets button")], verdict = fig.querySelector(".anat-verdict");
    const keysOf = el => el.dataset.k.split(" ");
    let cur = presets.length - 1, pinned = null;
    const light = k => {
      parts.forEach(p => p.classList.toggle("hi", !!k && keysOf(p).includes(k)));
      clauses.forEach(c => c.classList.toggle("hi", !!k && c.dataset.k === k));
    };
    clauses.forEach(c => {
      c.addEventListener("pointerenter", () => light(c.dataset.k));
      c.addEventListener("focus", () => light(c.dataset.k));
      c.addEventListener("click", () => { pinned = pinned === c.dataset.k ? null : c.dataset.k; light(pinned); });
      c.addEventListener("pointerleave", () => light(pinned));
      c.addEventListener("blur", () => light(pinned));
    });
    parts.forEach(p => {
      const key = keysOf(p)[0];
      const clause = clauses.find(c => c.dataset.k === key);
      p.setAttribute("tabindex", "0");
      p.setAttribute("role", "button");
      p.setAttribute("aria-label", clause?.textContent || key);
      p.addEventListener("pointerenter", () => light(keysOf(p)[0]));
      p.addEventListener("pointerleave", () => light(pinned));
      p.addEventListener("focus", () => light(key));
      p.addEventListener("blur", () => light(pinned));
      const pin = () => { pinned = pinned === key ? null : key; light(pinned); };
      p.addEventListener("click", pin);
      p.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pin(); }
      });
    });
    const say = i => { verdict.textContent = presets[i].verdict; };
    const set = i => {
      cur = i;
      const on = new Set(presets[i].on);
      D.press(buttons, buttons[i]);
      parts.forEach(p => p.classList.toggle("off", !keysOf(p).some(k => on.has(k))));
      say(i);
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => set(i)));
    set(cur);
    D.lock(verdict, presets.length, say, () => cur);
  }

  // ---------------- dt3: shadows as views on one table ----------------
  function shadows(fig) {
    const { states } = json(fig);
    const buttons = [...fig.querySelectorAll(".d1-presets button")], tbl = fig.querySelector(".sh-tbl");
    const rows = [...tbl.querySelectorAll("tbody tr")], cells = [...tbl.querySelectorAll("[data-c]")];
    const card = fig.querySelector(".sh-card"), code = card.querySelector("pre"), ans = card.querySelector(".sh-ans"), note = card.querySelector(".sh-note");
    let cur = 0;
    const text = i => { const s = states[i]; code.innerHTML = s.sql; ans.textContent = s.a; note.textContent = s.note; };
    const set = i => {
      cur = i;
      const s = states[i];
      D.press(buttons, buttons[i]);
      rows.forEach(r => r.classList.toggle("sel", s.rows.includes(+r.dataset.r)));
      cells.forEach(c => c.classList.toggle("col", +c.dataset.c === s.col));
      tbl.classList.add("on");
      text(i);
    };
    buttons.forEach((b, i) => b.addEventListener("click", () => set(i)));
    set(cur);
    D.lock(card, states.length, text, () => cur);
  }

  // ---------------- dt4: the loop ----------------
  function loop(fig) {
    const { steps, hold, words } = json(fig);
    const svg = fig.querySelector(".loop");
    const comps = [...svg.querySelectorAll(".lp")], conns = [...svg.querySelectorAll(".lc")];
    const cockpit = svg.querySelector(".ck"), temp = svg.querySelector(".lp-temp");
    const side = fig.querySelector(".lp-side"), say = fig.querySelector(".lp-say"), code = fig.querySelector(".lp-code");
    const msg = fig.querySelector(".lp-msg"), approve = fig.querySelector(".approve");
    const modes = [...fig.querySelectorAll("[data-m]")];
    let mode = "auto", approved = false, st = null;
    const setMode = m => {
      mode = m;
      fig.classList.toggle("mode-human", m === "human");
      svg.classList.toggle("mode-auto", m === "auto");
    };
    const render = i => {
      const s = steps[i];
      comps.forEach(c => c.classList.toggle("on", s.c.includes(c.dataset.c)));
      conns.forEach(c => c.classList.toggle("on", s.l.includes(c.dataset.c)));
      say.textContent = s.say;
      code.innerHTML = s.code;
      temp.textContent = s.temp;
      const waiting = mode === "human" && i === hold;
      cockpit.classList.toggle("ask", waiting);
      msg.textContent = i === hold ? words[mode] : "";
      approve.disabled = !waiting;
      // the hold: in operator mode a running sequence stops at the proposal until someone approves
      if (waiting && !approved && st && st.running) queueMicrotask(() => { if (st.running && st.k === hold) st.stop(); });
    };
    setMode("auto");
    st = D.stepper(fig, steps.length, render, { delay: 1500, narrated: true, lock: [side] });
    approve.addEventListener("click", () => { approved = true; st.show(hold + 1); approved = false; st.start(); });
    modes.forEach(b => b.addEventListener("click", () => { setMode(b.dataset.m); D.press(modes, b); render(st.k); }));
  }

  // ---------------- dt5: roles ----------------
  function roles(fig) {
    const { steps, words } = json(fig);
    const quads = [...fig.querySelectorAll(".roles .q")];
    const side = fig.querySelector(".ro-side"), title = fig.querySelector(".ro-title"), text = fig.querySelector(".ro-text"), panel = fig.querySelector(".ro-html");
    const where = fig.querySelector(".where");
    const render = i => {
      const s = steps[i];
      quads.forEach(q => q.classList.toggle("on", s.q.includes(q.dataset.q)));
      title.textContent = s.title; text.textContent = s.text; panel.innerHTML = s.html;
      where.textContent = `${words.step} ${i + 1} ${words.of} ${steps.length}`;
    };
    D.stepper(fig, steps.length, render, { delay: 4000, narrated: true, lock: [side], label: false });
  }

  const kinds = { dt1: ladder, dt2: anatomy, dt3: shadows, dt4: loop, dt5: roles };
  document.querySelectorAll("figure.demo[data-demo]").forEach(fig => {
    try { kinds[fig.dataset.demo]?.(fig); } catch (e) { console.error(e); }
  });
})();
