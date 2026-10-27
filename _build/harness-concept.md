# Explaining the agent harness

Editorial concept for the AI4SE article, researched 27 October 2026.

## The central distinction

The model generates a proposed next step. The harness turns model calls into a
managed process. The agent is the resulting goal-directed system, with the model
choosing its next steps from observations.

Working definition: **An agent harness is the software and configuration that run
the loop around a model: assemble context, call the model, execute permitted tool
calls, and feed results into the next turn.**

The term is useful because this surrounding machinery can change behaviour,
capability and failure modes without changing learned weights. “Model” cannot
name both the learned component and the whole executing system precisely.

## What the sources actually define

| Source | Boundary | Editorial use |
| --- | --- | --- |
| [Trivedy, LangChain, 10 March 2026](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness) | Broad complement of the model: code, configuration, execution logic, including bundled infrastructure. | Explains the popular formula “agent = model + harness”; explicitly a broad convention, not a universal taxonomy. |
| [Cloudflare, Harnesses](https://developers.cloudflare.com/agents/harnesses/) | The turn-by-turn loop around a model; distinguishes harness behaviour from underlying runtime infrastructure. | Anchor for the operational definition. |
| [Anthropic, Trustworthy agents in practice, 9 April 2026](https://www.anthropic.com/research/trustworthy-agents) | Separates model, harness (instructions and guardrails), tools and environment. | Evidence that competent authors draw different boundaries. Keep connected systems visible as separate responsibilities. |
| [Anthropic, Effective harnesses for long-running agents, 26 November 2025](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) | Concrete harness support for context management and continuity across sessions. | Example of extensions beyond the minimal execution loop. |
| [Böckeler, 2 April 2026](https://martinfowler.com/articles/harness-engineering.html) | Distinguishes the coding-agent builder's harness from additions made by its users; guides and sensors. | Connects the definition to project rules, checks, and the following parser/grammar section. |

These are practitioner definitions. The article states its own boundary rather
than presenting one vendor's terminology as a settled standard.

## Teaching sequence

1. Start with the missing mechanism: a generated test call does not run a test.
2. Define model, harness and agent by responsibility.
3. Show the mechanism and the boundaries in one diagram.
4. Trace “fix a failing test” through one iteration.
5. Resolve boundary cases: project instructions configure the harness; source
   files are task data; a test becomes feedback through its invocation and result.
6. Put competing definitions and optional features in the expandable note.
7. End with the engineering implication: improve context, tools, feedback and
   enforcement as well as choosing a model.

## Visual concept

The existing figure had a large undivided harness box, loosely distributed labels,
unlabelled model connections and no visible structure for the loop.

Replace it with a ruled responsibility diagram. Three aligned rows make the
harness inspectable: context and state; turn control; tool execution. The model
is a peer component inside the agent boundary, with the article's accent reserved
for it. Label context, response, call and return paths. Show tools and environment
below the boundary, since the harness connects to them rather than owning all
their contents. Explain that these are responsibility boundaries, not deployment
or security boundaries.

Use independent 640-unit desktop and 358-unit phone drawings, capped at their
native widths rather than stretched, with separate marker IDs,
theme tokens, orthogonal connectors and readable labels. Preserve the public
`#ai-f12` figure anchor and the shared caption/source conventions.

The layout refinement narrows the desktop harness from 416 to 264 units. Context
and response use two straight, opposing horizontal connectors, entering the model
from its side and returning to the harness's turn-control row. The model spans
both connection heights. Four small line glyphs identify context, control, tool
execution and the learned model; text remains sufficient to understand every role.
Rows have consistent title/detail alignment, and both layouts retain the separate
tool-call and results-return paths.

The harness is inset 56 units on desktop and 40 on phones; the results rail is
20 units from the agent background edge and retains one bend. Internal separators
use inset 3/3 dashes, distinct from the solid ownership boundary. Native details
controls add bilingual explanations to each row, the model and tools/environment,
with mouse hover, keyboard focus, touch toggling and Escape dismissal. Each whole
labelled region is the target, with no information icon. Explanations share a
reserved area below the drawing so none can cover another target. Only one is
open at a time. Figure height stays fixed; controls still toggle natively when
JavaScript is off.

Avoid the horse metaphor: it does not resolve any technical boundary. Avoid a
product-name taxonomy: a coding application can bundle a model, a harness, tools,
an environment and a user interface. Avoid treating memory, subagents or a
sandbox as necessary conditions for every harness.
