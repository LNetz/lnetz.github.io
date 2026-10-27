// Global search UI. Ranking and snippets live in search-core.js.
(() => {
  const form = document.getElementById("global-search");
  if (!form) return;
  const input = form.querySelector("input"), panel = document.getElementById("global-results");
  const title = panel.querySelector("h1"), status = panel.querySelector("[role=status]");
  const list = panel.querySelector("ol"), more = panel.querySelector(".global-search-more"), retry = panel.querySelector(".global-search-retry");
  const de = document.documentElement.lang === "de";
  const barLabel = document.querySelector(".index .here");
  if (barLabel) barLabel.dataset.searchLabel = de ? "Suche" : "Search";
  const W = de ? {
    title: q => `Suche: „${q}“`, loading: "Suche wird geladen…", empty: "Keine Treffer. Versuchen Sie einen anderen Begriff oder einen Anker wie ai-1.",
    count: (n, raw) => `${n} ${raw > n ? 'Treffergruppen' : 'Treffer'}${raw > n ? ` · ${raw} Fundstellen` : ''}`, error: "Die Suche konnte nicht geladen werden. Bitte versuchen Sie es erneut.",
    abstract: "Abstract", source: "Quelle", approximate: "Auch ähnliche Schreibweisen berücksichtigt.", spelling: "Ähnliche Schreibweise:", partial: "Teiltreffer",
    related: n => `${n} weitere ${n === 1 ? 'Fundstelle' : 'Fundstellen'} auf dieser Seite`, passage: "Ausschnitt aus",
    kind: { page: "Seite", section: "Abschnitt", figure: "Abbildung", publication: "Publikation" }, more: n => `${n} weitere anzeigen`
  } : {
    title: q => `Search: “${q}”`, loading: "Loading search…", empty: "No matches. Try another term or an anchor such as ai-1.",
    count: (n, raw) => `${n} ${raw > n ? 'result groups' : n === 1 ? "result" : "results"}${raw > n ? ` · ${raw} passages` : ''}`, error: "Search could not be loaded. Please try again.",
    abstract: "Abstract", source: "Source", approximate: "Similar spellings included.", spelling: "Similar spelling:", partial: "Partial match",
    related: n => `${n} more matching ${n === 1 ? 'passage' : 'passages'} on this page`, passage: "Passage from",
    kind: { page: "Page", section: "Section", figure: "Figure", publication: "Publication" }, more: n => `Show ${n} more`
  };
  const originalURL = new URL(location.href);
  originalURL.searchParams.delete("q");
  let indexPromise, timer, request = 0, matches = [], shown = 0, active = false, originalScroll = scrollY;
  const load = () => indexPromise ||= fetch(new URL(form.dataset.index, document.baseURI), { cache: "no-cache" })
    .then(response => { if (!response.ok) throw Error(response.status); return response.json(); })
    .then(items => SiteSearch.prepare(items))
    .catch(error => { indexPromise = null; throw error; });
  document.getElementById("search-toggle")?.addEventListener("click", () => {
    const menu = document.getElementById("index");
    if (!menu.classList.contains("open")) document.getElementById("menu-toggle").click();
    input.focus({ preventScroll: true });
    input.scrollIntoView({ block: "nearest", behavior: "instant" });
  });
  const closeMenu = () => {
    const menu = document.getElementById("index"), toggle = document.getElementById("menu-toggle");
    if (menu.classList.contains("open")) toggle.click();
  };
  function close() {
    clearTimeout(timer); request++;
    input.value = ""; panel.hidden = true;
    panel.removeAttribute("aria-busy");
    document.body.classList.remove("site-searching");
    if (active) {
      history.replaceState(history.state, "", originalURL);
      scrollTo({ top: originalScroll, behavior: "instant" });
    }
    active = false;
  }
  function highlight(el, value, query) {
    let at = 0;
    for (const [start, end] of SiteSearch.ranges(value, query)) {
      el.append(document.createTextNode(value.slice(at, start)));
      const mark = document.createElement("mark"); mark.textContent = value.slice(start, end); el.append(mark);
      at = end;
    }
    el.append(document.createTextNode(value.slice(at)));
  }
  function append() {
    const stop = Math.min(matches.length, shown + 30), first = shown;
    for (; shown < stop; shown++) {
      const hit = matches[shown], item = hit.item, marked = hit.matchedTerms;
      const li = document.createElement("li"), a = document.createElement("a"), meta = document.createElement("span");
      a.href = item.url;
      meta.className = "global-result-meta mono";
      highlight(meta, `${item.anchor ? `[${item.anchor}] · ` : ""}${item.page} · ${W.kind[item.kind]}`, marked);
      const heading = document.createElement("h2"); highlight(heading, item.title, marked);
      a.append(meta, heading); li.append(a);
      if (hit.fuzzy?.length || hit.quality === 0) {
        const reason = document.createElement('span'); reason.className = 'global-result-reason mono';
        reason.textContent = hit.fuzzy?.length ? `${W.spelling} ${[...new Set(hit.fuzzy)].join(', ')}` : W.partial;
        li.append(reason);
      }
      const preview = SiteSearch.bestExcerpt(hit, input.value), excerptItem = preview.item;
      const abstract = preview.abstract;
      const passage = document.createElement("p");
      highlight(passage, preview.text, preview.matchedTerms); li.append(passage);
      if (excerptItem.url !== item.url) {
        const origin = document.createElement('a'); origin.className = 'global-result-origin mono'; origin.href = excerptItem.url;
        origin.textContent = `${W.passage} [${excerptItem.anchor}]`; origin.title = excerptItem.title; li.append(origin);
      }
      if (abstract) {
        const provenance = document.createElement('div'); provenance.className = 'global-result-source mono';
        const source = document.createElement('a'); source.href = excerptItem.abstractSource; source.target = '_blank'; source.rel = 'noopener';
        source.textContent = `${W.source} ↗`; source.setAttribute('aria-label', `${W.abstract}: ${item.title} · ${W.source}`);
        provenance.append(`${W.abstract} · ${(excerptItem.abstractLanguage || 'en').toUpperCase()} · `, source); li.append(provenance);
      }
      if (hit.children?.length) {
        const children = document.createElement('ul'); children.className = 'global-result-children';
        for (const child of hit.children) {
          const row = document.createElement('li'), link = document.createElement('a'); link.href = child.item.url;
          const label = document.createElement('span'); label.className = 'mono'; label.textContent = `[${child.item.anchor}] ${W.kind.figure} · `;
          const text = document.createElement('span'); highlight(text, child.item.title, child.matchedTerms);
          link.append(label, text); row.append(link); children.append(row);
        }
        li.append(children);
      }
      if (hit.related?.length) {
        const details = document.createElement('details'); details.className = 'global-result-related';
        const summary = document.createElement('summary'); summary.className = 'mono';
        const related = hit.related.flatMap(unit => [unit, ...(unit.children || [])]);
        summary.textContent = W.related(related.length);
        const links = document.createElement('ul'); links.className = 'global-result-children';
        for (const child of related) {
          const row = document.createElement('li'), link = document.createElement('a'); link.href = child.item.url;
          const label = document.createElement('span'); label.className = 'mono'; label.textContent = `[${child.item.anchor}] ${W.kind[child.item.kind]} · `;
          const text = document.createElement('span'); highlight(text, child.item.title, child.matchedTerms);
          link.append(label, text); row.append(link); links.append(row);
        }
        details.append(summary, links); li.append(details);
      }
      list.append(li);
    }
    more.hidden = shown >= matches.length;
    more.textContent = W.more(Math.min(30, matches.length - shown));
    return list.children[first]?.querySelector("a");
  }
  async function search() {
    const query = input.value.trim().slice(0, 160);
    if (!query) { close(); return; }
    const ticket = ++request;
    if (!active) originalScroll = scrollY;
    active = true;
    document.body.classList.add("site-searching"); panel.hidden = false;
    title.textContent = W.title(query); status.textContent = W.loading;
    list.replaceChildren(); more.hidden = retry.hidden = true;
    panel.setAttribute("aria-busy", "true");
    const url = new URL(originalURL); url.searchParams.set("q", query); url.hash = "";
    history.replaceState(history.state, "", url);
    if (!document.getElementById("index").classList.contains("open")) {
      panel.scrollIntoView({ block: "start", behavior: "instant" });
    }
    try {
      const records = await load();
      if (ticket !== request) return;
      const hits = SiteSearch.rank(records, query);
      matches = SiteSearch.group(hits, records); shown = 0;
      status.textContent = matches.length ? W.count(matches.length, hits.length) : W.empty;
      if (matches.some(hit => hit.fuzzy?.length)) status.textContent += ` ${W.approximate}`;
      append();
    } catch (_) {
      if (ticket !== request) return;
      status.textContent = W.error; retry.hidden = false;
    } finally {
      if (ticket === request) panel.removeAttribute("aria-busy");
    }
  }
  input.addEventListener("input", e => {
    if (e.isComposing) return;
    request++; // An older fetch must not render against a newer input while it is debouncing.
    clearTimeout(timer);
    if (!input.value.trim()) close(); else timer = setTimeout(search, 150);
  });
  input.addEventListener("keydown", e => {
    if (e.key === "Escape" && active) { e.preventDefault(); e.stopPropagation(); close(); }
  });
  form.addEventListener("submit", e => {
    e.preventDefault(); clearTimeout(timer); closeMenu(); search();
    if (input.value.trim()) { title.focus({ preventScroll: true }); panel.scrollIntoView({ block: "start", behavior: "instant" }); }
  });
  panel.querySelector(".global-search-close").addEventListener("click", () => {
    close();
    (matchMedia("(min-width: 901px)").matches ? input : document.getElementById("main")).focus({ preventScroll: true });
  });
  more.addEventListener("click", () => append()?.focus());
  retry.addEventListener("click", search);
  const restore = () => {
    const query = new URL(location.href).searchParams.get("q");
    if (query) { input.value = query.slice(0, 160); search(); }
    else if (active) close();
  };
  addEventListener("popstate", restore);
  restore();
})();
