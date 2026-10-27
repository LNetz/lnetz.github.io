// Local lexical search. No network calls or dependencies; shared by the UI and regression tests.
const SiteSearch = (() => {
  const normalize = value => String(value).normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase().replace(/ß/g, 'ss');
  const terms = query => [...new Set(normalize(query).match(/[\p{L}\p{N}]+(?:[.-][\p{L}\p{N}]+)*/gu) || [])].slice(0, 12);
  const stop = new Set('the a an of on for to with and or is are how what this that die der das ein eine einer eines mit und oder im in am an zu fur von als wie was ist sind'.split(' '));
  const concepts = [
    ['llm', 'llms', 'sprachmodell', 'sprachmodelle', 'large language model', 'large language models'],
    ['mde', 'model-driven engineering', 'model driven engineering', 'modellgetriebene softwareentwicklung', 'modellgetrieben', 'modellgetriebene'],
    ['rag', 'retrieval-augmented generation', 'retrieval augmented generation'],
    ['digital twin', 'digital twins', 'digitaler zwilling', 'digitale zwillinge'],
    ['accessibility', 'accessible', 'barrierefreiheit', 'barrierefrei', 'barrierefreie'],
    ['grammar', 'grammatik'], ['masking', 'maskierung'],
    ['modeling', 'modelling', 'modellierung'], ['code generation', 'codegenerierung', 'codeerzeugung'],
    ['dsl', 'dsls', 'domain-specific language', 'domain-specific languages', 'domanenspezifische sprache'],
  ];
  const synonyms = new Map(concepts.flatMap(group => group.map(word => [word, group])));
  function queryGroups(query) {
    const words = terms(query), groups = [];
    for (let i = 0; i < words.length;) {
      let phrase = '', size = 0;
      for (let n = Math.min(4, words.length - i); n > 0; n--) {
        const candidate = words.slice(i, i + n).join(' ');
        if (synonyms.has(candidate)) { phrase = candidate; size = n; break; }
      }
      const raw = phrase || words[i];
      groups.push({ raw, variants: synonyms.get(raw) || [raw] }); i += size || 1;
    }
    const meaningful = groups.filter(group => !stop.has(group.raw));
    return meaningful.length ? meaningful : groups;
  }
  const wordChar = char => !!char && /[\p{L}\p{N}]/u.test(char);
  function bounded(text, phrase) {
    for (let at = text.indexOf(phrase); at >= 0; at = text.indexOf(phrase, at + phrase.length)) {
      if (!wordChar(text[at - 1]) && !wordChar(text[at + phrase.length])) return at;
    }
    return -1;
  }
  function field(value) {
    const normal = normalize(value || ''), counts = new Map();
    const words = normal.match(/[\p{L}\p{N}]+(?:[.-][\p{L}\p{N}]+)*/gu) || [];
    for (const word of words) {
      for (const token of new Set([word, ...word.split(/[.-]/u)])) counts.set(token, (counts.get(token) || 0) + 1);
    }
    return { normal, counts, length: words.length };
  }
  const weights = { anchor: 18, title: 12, section: 4, page: .7, text: 2, abstract: 3 };
  function prepare(items) {
    const records = items.map(item => ({ item, fields: Object.fromEntries(Object.keys(weights).map(key => [key, field(item[key])])) }));
    records.df = new Map(); records.byURL = new Map(records.map(record => [record.item.url, record]));
    records.average = Object.fromEntries(Object.keys(weights).map(key => [key,
      Math.max(1, records.reduce((sum, r) => sum + r.fields[key].length, 0) / Math.max(1, records.length))]));
    for (const record of records) for (const word of new Set(Object.values(record.fields).flatMap(f => [...f.counts.keys()]))) {
      records.df.set(word, (records.df.get(word) || 0) + 1);
    }
    records.vocabulary = [...records.df.keys()].filter(word => /^[\p{L}]{4,}$/u.test(word));
    return records;
  }
  function distance(a, b, limit) {
    if (Math.abs(a.length - b.length) > limit) return limit + 1;
    let previous = Array.from({ length: b.length + 1 }, (_, i) => i), older;
    for (let i = 1; i <= a.length; i++) {
      const row = [i];
      for (let j = 1; j <= b.length; j++) {
        row[j] = Math.min(row[j - 1] + 1, previous[j] + 1, previous[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        if (older && i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) row[j] = Math.min(row[j], older[j - 2] + 1);
      }
      if (Math.min(...row) > limit) return limit + 1;
      older = previous; previous = row;
    }
    return previous[b.length];
  }
  function matchField(f, group, prefix, fallback) {
    let best = null;
    for (const variant of group.variants) {
      const phrase = variant.includes(' '), at = bounded(f.normal, variant);
      if (at >= 0 || (!phrase && f.counts.has(variant))) {
        const quality = group.typos?.includes(variant) ? 1 : 3;
        if (!best || quality > best.quality) best = { quality, term: variant, fuzzy: quality === 1, tf: f.counts.get(variant) || 1, at: Math.max(0, at) };
      } else if (prefix && variant.length >= 3 && !phrase) {
        const word = [...f.counts.keys()].find(word => word.startsWith(variant));
        const typo = group.typos?.includes(variant), quality = typo ? 1 : 2;
        if (word && (!best || best.quality < quality)) best = { quality, fuzzy: !!typo, term: word, tf: f.counts.get(word), at: f.normal.indexOf(word) };
      }
      if (!best && fallback && variant.length >= 4 && !phrase) {
        const word = [...f.counts.keys()].find(word => word.includes(variant));
        if (word) best = { quality: 0, term: word, tf: f.counts.get(word), at: f.normal.indexOf(word) };
      }
    }
    return best;
  }
  function score(records, groups, query, fallback = false) {
    const phrase = normalize(query).replace(/^\[|\]$/g, '').trim();
    return records.flatMap(record => {
      let value = 0, quality = 3, abstractMatch = false;
      const matched = [], fuzzy = [], matchesByField = new Map(), matchGroups = [];
      for (const [index, group] of groups.entries()) {
        const actual = new Set(group.variants);
        let best = 0, bestQuality = -1;
        for (const [name, f] of Object.entries(record.fields)) {
          const hit = matchField(f, group, index === groups.length - 1, fallback);
          if (!hit) continue;
          if (name === 'abstract') abstractMatch = true;
          matched.push(hit.term);
          actual.add(hit.term);
          if (hit.fuzzy) fuzzy.push(hit.term);
          if (!matchesByField.has(name)) matchesByField.set(name, []);
          matchesByField.get(name).push(hit.at);
          const df = records.df.get(hit.term) || Math.min(...terms(hit.term).map(word => records.df.get(word) || 1));
          const idf = Math.log(1 + (records.length - df + .5) / (df + .5));
          const bm25 = hit.tf * 2.2 / (hit.tf + 1.2 * (.25 + .75 * f.length / records.average[name]));
          best = Math.max(best, weights[name] * (1 + idf) * bm25 * [ .12, .35, .65, 1 ][hit.quality]);
          bestQuality = Math.max(bestQuality, hit.quality);
        }
        if (bestQuality < 0) return [];
        matchGroups.push([...actual]);
        quality = Math.min(quality, bestQuality); value += best;
      }
      for (const [name, offsets] of matchesByField) {
        if (offsets.length === groups.length && groups.length > 1) value += 30 / (1 + (Math.max(...offsets) - Math.min(...offsets)) / 30);
        if (bounded(record.fields[name].normal, phrase) >= 0) value += name === 'title' ? 60 : name === 'abstract' ? 20 : 8;
      }
      const exact = record.item.anchor?.toLowerCase() === phrase || record.item.aliases?.some(alias => normalize(alias) === phrase);
      if (exact) { value += 10000; quality = 4; }
      if (record.item.kind === 'figure') value *= .85;
      return [{ item: record.item, score: value, quality, exact, abstractMatch,
        matchedTerms: [...new Set(matched)], matchGroups,
        fuzzy: [...new Set(fuzzy)] }];
    });
  }
  function rank(records, query) {
    const groups = queryGroups(query);
    if (!groups.length) return [];
    let hits = score(records, groups, query);
    if (hits.length < 3) {
      const expanded = groups.map(group => {
        if (group.raw.length < 4 || group.raw.includes(' ') || records.df.has(group.raw)) return group;
        const limit = group.raw.length >= 8 ? 2 : 1;
        const typos = records.vocabulary.map(word => [word, distance(group.raw, word, limit)])
          .filter(([, d]) => d > 0 && d <= limit).sort((a, b) => a[1] - b[1] || records.df.get(b[0]) - records.df.get(a[0])).slice(0, 3).map(([word]) => word);
        return { ...group, variants: [...group.variants, ...typos], typos };
      });
      if (expanded.some(g => g.typos?.length)) {
        const present = new Set(hits.map(hit => hit.item.url));
        hits.push(...score(records, expanded, query).filter(hit => !present.has(hit.item.url)));
      }
    }
    if (!hits.length) hits = score(records, groups, query, true);
    return hits.sort((a, b) => b.quality - a.quality || b.score - a.score || a.item.url.localeCompare(b.item.url));
  }
  function group(hits, records) {
    const groups = new Map();
    for (const hit of hits) {
      const parent = !hit.exact && hit.item.kind === 'figure' && records.byURL.get(hit.item.parent)?.item;
      const key = parent ? parent.url : hit.item.url;
      if (!groups.has(key)) groups.set(key, { ...hit, item: parent || hit.item, excerptItem: hit.item, children: [] });
      const result = groups.get(key);
      if (hit.item.kind === 'figure' && parent) result.children.push(hit);
      if (hit.item.url === key) { result.item = hit.item; result.matchedTerms = [...new Set([...result.matchedTerms, ...hit.matchedTerms])]; }
      if (hit.score > result.score || hit.quality > result.quality) {
        result.score = hit.score; result.quality = hit.quality; result.excerptItem = hit.item;
        result.matchedTerms = hit.matchedTerms; result.matchGroups = hit.matchGroups;
      }
    }
    const sections = [...groups.values()].sort((a, b) => b.quality - a.quality || b.score - a.score || a.item.url.localeCompare(b.item.url));
    const pages = new Map();
    for (const section of sections) {
      // Keep publications and exact anchor queries individually addressable.
      const key = section.item.kind === 'publication' || section.exact ? section.item.url : section.item.url.split('#')[0];
      if (!pages.has(key)) pages.set(key, { ...section, related: [] });
      else pages.get(key).related.push(section);
    }
    return [...pages.values()];
  }
  function ranges(value, query) {
    let normalized = '', offset = 0;
    const starts = [], ends = [];
    for (const char of value) {
      const part = normalize(char), end = offset + char.length;
      for (let i = 0; i < part.length; i++) { starts.push(offset); ends.push(end); }
      if (!part && ends.length) ends[ends.length - 1] = end;
      normalized += part; offset = end;
    }
    const found = [];
    for (const word of Array.isArray(query) ? query : terms(query)) {
      if (!word) continue;
      for (let at = normalized.indexOf(word); at >= 0; at = normalized.indexOf(word, at + word.length)) {
        if (wordChar(normalized[at - 1]) || wordChar(normalized[at + word.length])) continue;
        found.push([starts[at], ends[at + word.length - 1]]);
      }
    }
    const merged = [];
    for (const range of found.sort((a, b) => a[0] - b[0])) {
      const last = merged.at(-1);
      if (last && range[0] <= last[1]) last[1] = Math.max(last[1], range[1]); else merged.push([...range]);
    }
    return merged;
  }
  function snippet(value, query, length = 220, groups) {
    if (!value) return { text: '', coverage: 0, score: 0 };
    const variants = groups || queryGroups(query).map(g => g.variants);
    const matches = variants.flatMap((group, id) => ranges(value, group).map(([start, end]) => ({ start, end, id })));
    const sentences = typeof Intl.Segmenter === 'function'
      ? [...new Intl.Segmenter(undefined, { granularity: 'sentence' }).segment(value)].map(part => ({ start: part.index, end: part.index + part.segment.trimEnd().length }))
      : [...value.matchAll(/[^.!?]+(?:[.!?](?:\s+|$)|$)/g)].map(part => ({ start: part.index, end: part.index + part[0].trimEnd().length }));
    const candidates = [];
    for (let i = 0; i < sentences.length; i++) {
      if (!matches.length && i > 0) break;
      const first = sentences[i];
      if (matches.length && !matches.some(hit => hit.start >= first.start && hit.start <= first.end)) continue;
      for (let from = Math.max(0, i - 1); from <= i; from++) {
        for (let to = i; to < sentences.length && sentences[to].end - sentences[from].start <= length; to++) {
          candidates.push({ start: sentences[from].start, end: sentences[to].end, complete: true });
        }
      }
    }
    for (const hit of matches.length ? matches : [{ start: 0 }]) {
      let start = Math.max(0, hit.start - 45);
      if (start && !/\s/.test(value[start - 1])) { const space = value.indexOf(' ', start); if (space >= 0 && space < hit.start) start = space + 1; }
      let end = Math.min(value.length, start + length);
      if (end < value.length && !/\s/.test(value[end])) { const space = value.lastIndexOf(' ', end); if (space > start) end = space; }
      candidates.push({ start, end, complete: start === 0 && end === value.length });
    }
    let best = { start: 0, end: Math.min(length, value.length), score: -1, coverage: 0 };
    for (const candidate of candidates) {
      const inside = matches.filter(hit => hit.start >= candidate.start && hit.end <= candidate.end);
      const coverage = new Set(inside.map(hit => hit.id)).size;
      const span = inside.length ? Math.max(...inside.map(hit => hit.end)) - Math.min(...inside.map(hit => hit.start)) : length;
      const size = candidate.end - candidate.start;
      // A tiny heading-like sentence is not a useful explanation on its own.
      const relevantSize = matches.length ? sentences.filter(sentence => inside.some(hit => hit.start >= sentence.start && hit.end <= sentence.end)).reduce((sum, sentence) => sum + sentence.end - sentence.start, 0) : size;
      const tooShort = coverage === 1 && relevantSize < 80 ? (80 - relevantSize) * 1.5 : 0;
      const padding = Math.max(0, size - relevantSize) * .1;
      const score = coverage * 1000 + Math.min(inside.length, 3) * 6 + (candidate.complete ? 45 : 0) + 20 * (1 - span / length) - tooShort - padding - size * .01 - candidate.start / Math.max(1, value.length) * 8;
      if (score > best.score) best = { ...candidate, score, coverage };
    }
    return { text: (best.start && !best.complete ? '…' : '') + value.slice(best.start, best.end).trim() + (best.end < value.length && !best.complete ? '…' : ''), coverage: best.coverage, score: best.score };
  }
  const excerpt = (value, query, length = 220, groups) => snippet(value, query, length, groups).text;
  function bestExcerpt(hit, query, length = 280) {
    const units = [hit, ...(hit.children || []), ...(hit.related || []).flatMap(unit => [unit, ...(unit.children || [])])];
    let best = null;
    for (const unit of units) {
      const item = unit.excerptItem || unit.item;
      const abstract = !!(item.kind === 'publication' && item.abstract && unit.abstractMatch);
      const passage = snippet(abstract ? item.abstract : item.text, query, length, unit.matchGroups);
      if (unit === hit) passage.score += 12; // Prefer the primary section when coverage is otherwise equivalent.
      if (!best || (passage.coverage > 0 && passage.score > best.score)) best = { ...passage, item, abstract, matchedTerms: unit.matchedTerms };
    }
    return best || { text: '', item: hit.item, matchedTerms: hit.matchedTerms };
  }
  return { normalize, terms, prepare, rank, group, excerpt, bestExcerpt, ranges, queryGroups, distance };
})();
