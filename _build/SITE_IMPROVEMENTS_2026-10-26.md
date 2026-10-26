# Portfolio improvements — 26 October 2026

Review at <http://127.0.0.1:8001/>. Everything remains uncommitted, including the preceding article corrections.

## Changes

- About now starts with Lukas's positioning and selected project evidence. Three linked project previews use existing screenshots/logos and already published outcomes. The quotation moves below the biography; exploration links have visible labels.
- Projects starts with the same selected work. The complete archive remains; the timeline is an expandable section. The decorative AI illustration no longer precedes the work.
- Research offers three direct routes: introductions, publications and citations. Both generated research pages include every publication before JavaScript runs. Title/author/year search combines with topic filters, announces result counts and provides an empty state. Existing per-paper links and citation miniatures remain.
- Citation-map advanced filters are collapsible. Phone control hit areas are at least 44 × 44 px. A searchable list provides keyboard selection and source links for external graph nodes as well as Lukas's papers. A failed data request produces a localized message and retry action without removing the publication list.
- The lightbox, mobile navigation sheet and game overlay share focus containment and background isolation. The mobile sheet receives dialog semantics only while open. Closing restores the existing opener behavior. A skip-to-content link and meaningful research/project section headings improve navigation.
- Photography starts with a short introduction and the selected photographs. The longer explanation and personal banner move into “Behind the camera”; the complete gallery, captions, slideshow and transitions remain.
- Research overview and geneial now consistently describe the studied parallel hybrid rather than plug-in hybrid.
- Shared page generation adds canonical URLs, large-image sharing metadata using existing relevant imagery, and bilingual 404 pages. The local preview server returns those pages with HTTP 404 for missing paths. A generated sitemap lists the 36 regular EN/DE routes.

## Validation

- Build: repository capture/Node workflow regenerated all pages and the sitemap. Only the final citation script hash required a subsequent research-page rebuild.
- `python -X utf8 _build/tools/check_site.py`: 38 generated pages pass unique-ID, local destination/anchor, sharing-image, canonical and main-landmark checks. Both research pages contain all 32 publication entries statically; sitemap has 36 unique regular routes.
- Existing article validation passed after the shared-shell changes; its numerical examples and demo payloads remain valid.
- JavaScript syntax checks and `git diff --check` pass.
- Browser: EN/DE overview pages checked at 375, 768 and 1280 px after loading; no settled page-wide overflow. Initial measurements during navigation were transient and are not reported as fixed layout defects.
- Browser: publication title search, no-results message, combined topic/author filtering in German and year search exercised. The map list selected an external paper by keyboard; both citation directions loaded. Phone controls measured at least 44 × 44 px.
- Browser: Tab/Shift+Tab stay inside the photo lightbox; the mobile menu wraps focus and closes with Escape. The game uses the same focus helper, but a complete keyboard game was not played.
- Failure injection: a temporary localhost proxy rejected the first citation-data request. The error message and Retry appeared; Retry then loaded 2,330 graph papers and enabled search. The proxy was used for testing only.
- Custom missing-route recovery viewed locally. Production GitHub Pages behavior and external social-card caches require verification after a separately authorized deployment.

No formal screen-reader audit or full browser/device matrix was performed. The no-JavaScript publication fallback is verified in generated HTML; a dedicated browser session with scripting disabled was not run. No external publication data or citation metrics were refreshed.
