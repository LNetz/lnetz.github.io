# Article feedback implementation, 26 October 2026

Local review: <http://localhost:8001/research.html#articles>. No staging, commit or push performed.

Scope: AI4SE, Digital Twins and Evolutionary Algorithms, including all six EN/DE generated pages. MDE and shared article/demo modules have no content diff. Existing figure and section IDs are preserved.

## Implementation matrix

“Implemented” refers to the editorial or interaction change; it does not imply every combination of viewport, theme, animation frame and assistive technology has been tested.

| Review task IDs | Status and change | Source files | Evidence / validation |
|---|---|---|---|
| AI P1-01–02, P2-08 | Implemented: conditional grammar guarantee; prototype limitations; synthetic task provenance; per-model fractions; separate GPT-4o reference; setup-specific latency | `ai4se.py` | NRR24 §4–6 and Table 1; fractions recalculated. Gemma remains 2/658 ≈ 0.3%, correcting the paper's percentage typo. |
| AI P1-03–04 | Implemented: capability-based generative-AI taxonomy; models versus products; separate harness/model and isolated execution boundary | `ai4se.py` | SVG and surrounding prose aligned; desktop dark and phone rendering checked |
| AI P1-05, P1-08 | Implemented: artificial attention weights, causal direction and explanation caveat; static-word versus contextual-token versus retrieval embeddings | `ai4se.py` | Jain & Wallace 2019; mechanism versus interpretation distinguished |
| AI P1-06–07, P2-10, P2-13–14 | Implemented: syntax gate, explicit semantic stage in final pipeline, prototype scope and generator limitations | `ai4se.py` | NRR24 limitations; EN/DE pipeline inspected at phone width |
| AI P2-01–07, P2-09, P2-11–12, P2-15 | Implemented: tokenizer units; KV cache; toy ReLU/softmax; full-attention cost; post-training scope; RAG generation failures; practical agent definition; schematic fragments; article focus; JSON annotation outside code; trust boundaries | `ai4se.py` | Source review, generated content and browser checks. The sources-required label is a request, not an automatic citation guarantee. |
| DT P1-01–03 | Implemented: operational versus development notions; broad original-system scope; human-mediated control is conditional on the other clauses; revised recommendation checklist | `dt.py`, `dt_figs.py` | RWTH essay v2.2, rationale and kinds; German development preset and keyboard anatomy tested |
| DT P1-04 | Implemented: preserve the source's toy threshold 500; abstract illustrative T rather than claiming 500 °C is an ordinary industrial setpoint; consistent loop and cockpit examples | `dt_figs.py` | DHM+22 Fig. 17–18 calls the nozzle threshold “500 degrees” without establishing a polymer-specific Celsius setpoint; no new process measurements invented |
| DT P1-05, P2-06 | Implemented: 2022 scope and separate framework/runtime/language/platform categories; remove universal “no platforms” claim | `dt.py` | DHM+22 related-work scope; historical comparison retained |
| DT P1-06, P2-03–04 | Implemented: visible command return path; optional cockpit approval route; sensor feedback is distinguished from command acknowledgement | `dt_figs.py` | SVG references checked; new reading/evaluator stage described explicitly |
| DT P1-07 | Implemented: SQL projection analogy; purpose/provenance context; observation versus charging advice; synthetic diagnostic threshold | `dt.py`, `dt_figs.py` | All three SQL views executed in SQLite and match the displayed outputs |
| DT P1-08–09, P2-02 | Implemented: lifecycle goals rather than mandatory lifespan/instantiation; different model/shadow cadences; mapping, generated schemas and deployment/runtime boundary | `dt.py`, `dt_figs.py` | RWTH rationale; tablet generation diagram inspected |
| DT P1-10, P2-10 | Implemented: engineering-data prototype scope; excerpt labeling; example values without invented units; CRUD, handwritten derivation and tool writeback distinguished | `dt.py`, `dt_figs.py` | MNN+22 §§5–6. Release-status tracking actually was implemented, including associated-object release checks; this is retained as basic lifecycle tracking, not downgraded to an unimplemented concept or promoted to a full workflow engine. |
| DT P2-07–08, P2-11–12 | Implemented: logical views versus independent twins; safety and authorization; composition versus interoperability; digital thread and CPS distinctions | `dt.py` | Architecture responsibilities and integration preconditions made explicit |
| DT P3-02–03 | Implemented: diagram parts focusable with Enter/Space and touch activation; technical names visible beside low-code choices | `dt.js`, `dt.css`, `dt_figs.py` | Keyboard interaction checked in German; focus style added |
| EA P1-01–03, P1-06 | Implemented: parallel hybrid; 20 ms model step versus ≤1 s split hold; simulated NEDC scope; finite horizon hypothesis; 12.5 GB packed storage | `ea.py`, `ea_figs.py` | NWN+15 §4 and Tables 1–4 checked directly; memory calculation independently verified |
| EA P1-04–05, P1-07–08 | Implemented: ML paradigms and neuroevolution; scalar versus richer evaluator interfaces; Pareto approximation; novelty versus quality-diversity archives; novelty sources beyond mutation | `ea.py`, `ea_figs.py` | Prose, overview, family table and summary synchronized |
| EA P2-01–02, P2-04, P2-08–09 | Implemented: No-Free-Lunch assumptions; qualified gradient guidance; richer benchmark reporting; algorithmic versus runtime-budget claims | `ea.py`, `ea_figs.py` | Uniform finite-function/non-revisiting assumptions stated; repeatable starter results checked |
| EA P2-03, P2-05–07, P2-11–12 | Implemented or retained where already correct: SUS caption already named six equally spaced pointers; constraints and local scores remain visible; Jensen simplifications; finite sweep rather than full Pareto front; resolution heuristic qualified | `ea.py`, `ea_figs.py` | Net17 One-Step description and runtime text checked directly (PDF pp. 36 and 60–62); numerical arrays preserved |
| EA P3-01–05 | Implemented core editorial changes: design-choice preview, evidence/seed labels, scoped slogans, benchmark n=1/hardware, library parameter semantics and dated versions | `ea.py`, `ea_figs.py` | Five GitHub release records and DEAP's PyPI release source consulted; DEAP/PyGAD/pymoo operator docs checked. No claim that sigma, uniform bounds and eta are interchangeable. |
| EA interaction checklist | Implemented: mutation point supports arrow keys, Shift for larger moves; visible focus ring. Existing turbine keyboard movement retained. | `ea.js`, `ea.css`, `ea_figs.py` | Mutation keyboard placement exercised in browser; live randomness explicitly retained and labeled |
| Shared C/D and figure QA | Implemented source/caption alignment and EN/DE regeneration; static fallback notice and inactive no-JS controls hidden locally per article | Three generators and six outputs | Automated structural checks and sampled visual/interaction QA below; no shared-module change |

## Scientific sources inspected

- [NRR24 grammar masking](https://www.se-rwth.de/publications/Using-Grammar-Masking-to-Ensure-Syntactic-Validity-in-LLM-based-Modeling-Tasks.pdf), especially task synthesis, Table 1, grammar mismatch, token limits and semantic checks.
- [Attention is not Explanation](https://aclanthology.org/N19-1357/).
- [RWTH digital-twin essay](https://www.se-rwth.de/essay/Digital-Twin-Definition/), original-system scope, update cadences and development/operational categories. The essay has broader scope than the physical-precondition sentence still present on the separate research-topic page; this article follows its declared essay definition.
- [DHM+22](https://www.se-rwth.de/publications/Generating-Customized-Low-Code-Development-Platforms-for-Digital-Twins.pdf), especially Fig. 17–18.
- [MNN+22](https://www.se-rwth.de/publications/Generating-Digital-Twin-Cockpits-for-Parameter-Management-in-the-Engineering-of-Wind-Turbines.pdf), engineering writeback, release tracking and explicitly excluded runtime functionality.
- [NWN+15](https://easychair.org/publications/paper/6CD4/open), §4 and Tables 1–4. The old `/publications/open/6CD4` route failed in the research tool; the paper-specific `/paper/6CD4/open` route worked.
- [Net17 thesis](https://ths.rwth-aachen.de/wp-content/uploads/sites/4/netz_master.pdf), downloaded temporarily for direct text extraction because the web reader rejects its size. Runtime values 88732.62, 73594.79 and 17768.83 seconds and the corresponding rounded grid durations were confirmed. No thesis experiment was rerun.
- [DEAP tools](https://deap.readthedocs.io/en/master/api/tools.html), [DEAP algorithms](https://deap.readthedocs.io/en/master/api/algo.html), [PyGAD parameters](https://pygad.readthedocs.io/en/latest/pygad.html), [pymoo mutation](https://pymoo.org/operators/mutation.html), official release records, and OpenAI's structured-output/function-calling documentation.

## Validation

- Full generator initially succeeded. A later direct Python write failed with `OSError: Invalid argument`; the repository's capture/Node workaround regenerated the six target pages successfully. Unrelated generated pages and MDE have no content diff.
- `python -X utf8 _build/tools/check_article_review.py`: pass, all six pages. Checks unique IDs, internal anchors, local resources, SVG marker/clip references and JSON demo payloads; executes the SQLite examples and independent arithmetic; runs EA simulation assertions and ten starter seeds twice for reproducibility (1,100 evaluations per run).
- `node --check assets/dt.js` and `node --check assets/ea.js`: pass.
- `git diff --check`: pass after removing an empty SVG interpolation line's whitespace.
- Browser geometry checks: six pages × widths 375, 768 and 1280 px. No page-wide horizontal overflow. Scrollable technical figures remain scrollable by design.
- Phone SVG text-boundary checks: all six pages; no rendered labels outside their visible SVG boundaries.
- Inspected key figures: taxonomy and German full validation pipeline on phone; harness in desktop light/dark; German anatomy in phone layout; generation/deployment boundary on tablet.
- Exercised shadow-purpose switching, German development-twin verdict, keyboard activation of anatomy parts and mutation arrow-key placement. No warnings/errors in the browser logs sampled during those checks.

## Limits of this pass

The exhaustive checklist in the feedback goes beyond these targeted checks. Every animation frame/preset was not screenshot-audited in every theme/language. A dedicated screen reader, actual 200% browser zoom, emulated reduced-motion run and a browser session with JavaScript disabled were not exercised. Reduced-motion handling remains in the unchanged shared demo helpers; the no-JS notice/control hiding was source-checked. All external publication links were not crawled, and no blanket “no broken external links” claim is made. No observed clipping issue was invented or claimed fixed.

No owner decision is needed to view the changes. Review the local articles before authorizing any commit.
