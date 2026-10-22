// Shared helpers for the interactive figures of the article series (research-mde/-ai4se/-dt/-ea.html).
// Loaded before each article's own script (article_common.scripts()); everything is on window.SiteDemo.
// The rules behind them (autoplay, height lock, controls) are in _build/STYLE.md.
//
//   SiteDemo.reduce                       true when the OS asks for reduced motion
//   SiteDemo.words                        { play, pause, replay, step, of } in the page language
//   SiteDemo.whenSeen(el, fn, t = .35)    run fn once, when a share t of el is visible
//   SiteDemo.lock(el, states, render, current)
//                                         height lock: renders every state, sets min-height to the tallest,
//                                         restores current() and repeats when el's width changes
//   SiteDemo.autoplay(fig, { start, stop, narrated = true })
//                                         the series' autoplay rule: a narrated sequence starts once when it
//                                         comes into view (never under reduced motion); any run stops when the
//                                         figure leaves the view. Parameter demos pass narrated: false.
//   SiteDemo.stepper(fig, count, render, { delay, narrated, lock, label, onStop })
//                                         the one stepper: .play (▶ / ❚❚ / ↺ "replay"), input.step, .where
//                                         "step n of N"; locks the elements in `lock` over all steps
//   SiteDemo.press(buttons, on)           segmented chips: aria-pressed on the pressed one only
window.SiteDemo = (() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const de = document.documentElement.lang === "de";
  const words = de ? { play: "abspielen", pause: "anhalten", replay: "noch einmal abspielen", step: "Schritt", of: "von" }
                   : { play: "play", pause: "pause", replay: "replay", step: "step", of: "of" };

  const whenSeen = (el, fn, t = .35) => {
    if (!("IntersectionObserver" in window)) return fn();
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { io.disconnect(); fn(); } }, { threshold: t });
    io.observe(el);
  };

  // states: a number n (render(0) … render(n - 1)) or an array of values passed to render
  function lock(el, states, render, current) {
    const list = typeof states === "number" ? [...Array(states).keys()] : states;
    const back = current || (() => list[0]);
    let width = -1;
    const measure = force => {
      const w = el.clientWidth;
      if (!w || (w === width && !force)) return;
      width = w;
      const now = back();
      el.style.minHeight = "";
      let max = 0;
      for (const s of list) { render(s); max = Math.max(max, el.offsetHeight); }
      el.style.minHeight = `${max}px`;
      render(now);
    };
    measure();
    if ("ResizeObserver" in window) new ResizeObserver(() => measure()).observe(el);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => measure(true));
    return { measure: () => measure(true) };
  }

  function autoplay(fig, { start, stop, narrated = true }) {
    if (narrated && !reduce) whenSeen(fig, start);
    if ("IntersectionObserver" in window && stop)
      new IntersectionObserver(([e]) => { if (!e.isIntersecting) stop(); }, { threshold: 0 }).observe(fig);
  }

  function stepper(fig, count, render, { delay = 1200, narrated = true, lock: locked = [], label = true, onStop } = {}) {
    const play = fig.querySelector(".play"), range = fig.querySelector("input.step"), where = fig.querySelector(".where");
    const wait = typeof delay === "function" ? delay : () => delay;
    let k = 0, timer = null;
    range.max = count - 1;
    const show = i => {
      k = i; range.value = i; render(i);
      if (label && where) where.textContent = `${words.step} ${i + 1} ${words.of} ${count}`;
    };
    const idle = () => {
      const end = k >= count - 1;
      play.textContent = end ? "↺" : "▶";
      play.setAttribute("aria-label", end ? words.replay : words.play);
    };
    const stop = () => { if (timer) { clearTimeout(timer); timer = null; if (onStop) onStop(k); } idle(); };
    const tick = () => { if (k >= count - 1) { timer = null; return idle(); } show(k + 1); timer = setTimeout(tick, wait(k)); };
    const start = () => {
      if (timer) return;
      if (k >= count - 1) show(0);
      play.textContent = "❚❚"; play.setAttribute("aria-label", words.pause);
      timer = setTimeout(tick, wait(k));
    };
    play.addEventListener("click", () => (timer ? stop() : start()));
    range.addEventListener("input", () => { stop(); show(+range.value); idle(); });
    [].concat(locked).forEach(el => el && lock(el, count, render, () => k));
    show(0); idle();
    autoplay(fig, { start, stop, narrated });
    const setCount = n => { count = n; range.max = n - 1; show(Math.min(k, n - 1)); if (!timer) idle(); };
    return { show, start, stop, setCount, get k() { return k; }, get running() { return !!timer; } };
  }

  const press = (buttons, on) => buttons.forEach(b => b.setAttribute("aria-pressed", String(b === on)));

  // thin sliders (style.css): the filled part of the track follows --p, also when a script sets .value
  const proto = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
  const fill = r => {
    const min = r.min === "" ? 0 : +r.min, max = r.max === "" ? 100 : +r.max, v = +proto.get.call(r);
    r.style.setProperty("--p", `${max > min ? ((v - min) / (max - min)) * 100 : 0}%`);
  };
  const thin = r => {
    if (r.dataset.thin) return;
    r.dataset.thin = "1";
    Object.defineProperty(r, "value", { configurable: true, get() { return proto.get.call(this); }, set(v) { proto.set.call(this, v); fill(this); } });
    r.addEventListener("input", () => fill(r));
    new MutationObserver(() => fill(r)).observe(r, { attributes: true, attributeFilter: ["min", "max", "value"] });
    fill(r);
  };
  document.querySelectorAll(".art-sec input[type=range]").forEach(thin);

  return { reduce, words, whenSeen, lock, autoplay, stepper, press, thin };
})();
