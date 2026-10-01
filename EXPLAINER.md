# EXPLAINER.md

Conventions every Cybertron explainer inherits: §1–7 engineering (Jazz), §8–10 design (Arcee). Breaking a rule
is wrong by default; deviate only with the deviation named and justified on the ticket. Every rule has a **Check**.

## 1. Layout and entry point

- One directory per explainer: `explainers/<slug>/`, `<slug>` lowercase kebab-case — no dates, no version suffixes.
- The entry point is always `explainers/<slug>/index.html`. Nothing else is a page.
- Permitted siblings: `assets/` (only files actually referenced) and `SOURCES.md`. Nothing else ships.

**Check:** `ls explainers/*/index.html` lists one file per explainer directory; `ls explainers/<slug>/` shows
nothing outside the permitted set.

## 2. Self-contained

- One HTML file, CSS and JS inline (`<style>`, `<script>`). No build step: the file committed is the file the reader gets.
- No `<script src>`, `<link href>` or `@import` pointing at any host. No CDN, no web fonts, no analytics.
- No `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource` or dynamic `import()` — at load or ever.
- Images: inline SVG, or a local file in `assets/` inside the §5 budget. `data:` URIs only under 10 KB.

**Check — all three pass:** (1) open `index.html` from `file://`: it renders and every interaction works.
(2) DevTools › Network, hard reload from `file://`: zero requests other than the document itself.
(3) `grep -nE '(src|href)="https?:|@import|fetch\(|XMLHttpRequest' index.html` returns nothing outside prose source links.

## 3. Data/view split

- All content lives in one top-level `const DATA = { … }` at the top of the `<script>`: plain arrays and objects of
  strings, numbers, dates and ids. No functions, no DOM, no markup.
- Render functions read `DATA` and produce DOM. They hold no content — a fact hard-coded in a render function is a bug.
- **One source of truth.** A fact is typed once. If two views need it, both read the same field. Derive, never duplicate.
  A claim shown in several views (timeline entry, lore variant, comparison column) is one record with an `id`; each view
  references it and may add framing (title, label, link), never a reworded copy. Records sharing an id across collections
  (an era and a continuity) derive shared fields such as years, never retype them. Reworded copies drift (CYB-11 F3, H1).
- Entities carry a stable string `id`. Relationships are id references, never nested copies of the entity.
- **State minimalism.** Store only what the reader chose (selected id, active filter, quiz answer). Counts, filtered
  lists, labels and "is selected" are derived at render time. If you can compute it, do not store it.

**Check:** a non-engineer can correct a date or a name by editing `DATA` alone. Change one fact, reload: every place
it appears updates — if one doesn't, the fact was typed twice. Read `DATA` top to bottom: no claim is stated in two records.

## 4. Source discipline

- Every factual claim carries a `source` on the same record in `DATA`: a title, plus a URL where one exists.
  Next to the fact — not a bibliography at the bottom.
- Unsourceable means unknown: the field is `null` and the UI says "unknown", or the fact is cut.
  **Never fill a gap with a plausible guess.** Invented confident-sounding detail is the worst defect we can ship.
- Disputed or estimated values carry `confidence: "disputed" | "approximate"`, and the UI shows that qualifier.
- **Precision is a claim.** No value — in `DATA`, the text, or markup like `datetime` — is more precise than its source:
  `"1984"` stays `1984`, never `1984-01-01`. In-world or fictional material is labelled where it could pass for fact.
- `SOURCES.md` lists the works consulted. It summarises what is already in `DATA`; it does not replace it.

**Check:** pick three claims at random off the rendered page; each traces to a `source` in `DATA`. Every `null`
renders a visible "unknown", not an empty cell. Every `time[datetime]` equals its `DATA` value character for character.

## 5. Performance budget

- Interactive in under **2 s** on a laptop, cold from `file://`: document start to the first interaction responding.
- Page weight ceiling: **500 KB** for `index.html`, **1 MB** for the explainer directory. Over budget means cut
  content or compress assets — not request an exception. Zero runtime dependencies.
- Render the initial view in one pass. No layout-thrash loops, no per-frame work while idle.

**Check:** `wc -c explainers/<slug>/index.html` ≤ 512000 and `du -sk explainers/<slug>/` ≤ 1024.
DevTools › Performance, cold `file://` load: interactive under 2 s.

## 6. Progressive enhancement and failure visibility

- With JS off or broken the reader still gets the page's frame: `<h1>`, lede, each section's `<h2>` and a one-sentence
  intro saying what it teaches, plus a per-section note (`<noscript>`, and a visible fallback for JS that loads but breaks)
  naming what is unavailable. Content lives in `DATA` (§3) and needs JS to render: copying it into static HTML types every
  fact twice (§3) and pre-rendering needs a build step (§2). Accepted trade-off (CYB-12), not a gap.
- Semantic elements first: `<main>`, `<section>`, `<h1>`–`<h3>`, `<ol>`/`<ul>`, `<button>`, `<details>`. `aria-*` only
  where semantics run out. A `<div>` with a click handler is a defect.
- **A broken interaction must look broken.** Render entry points are wrapped so a thrown error renders the §9 error
  state. Never swallow an exception and leave the UI unchanged. No `console.log` in shipped code.
- The wrapper honours `?fail=<section id>`: it throws inside that section's render, so the error state is testable without
  editing code. It is a test hook: never mentioned in reader-facing copy.
- Live regions (`<output>`, `[role=status]`, `[aria-live]`) are in the markup at first render, empty; renders change only their
  text, and one action updates one region. Screen readers often skip a region that arrives filled, or drop one of two.
- Never gate logic on `transitionend`/`animationend`: under reduced motion (§8) durations are 0 and they never fire.

**Check:** disable JS and reload — the frame is readable and each section's note says what is missing. Load `?fail=<id>` for
each section — that section shows the error state; the rest of the page still works. Capture `document.querySelectorAll('output,[role=status],[aria-live]')`
at load; after the §10 "Focus is never lost" walk (no throw) every node is still `isConnected` and the same query returns the same count (none inserted).

## 7. Review gate

Nothing merges without all four: this file followed (or the deviation justified on the ticket), Ratchet's test evidence
for the changed interactions, Soundwave's findings fixed or accepted in writing on the ticket, and Jazz's approval.
**Reuse before invention:** check this file and existing explainers before adding a pattern; approved exceptions are written here.
**Current conventions:** a page is reviewed against this file as it is at review time, not as it was when the build began.
The §8 block must match byte for byte: `P='/^:root { \/\* tokens:start/,/tokens:end \*\/$/p'; diff <(sed -n "$P" EXPLAINER.md) <(sed -n "$P" explainers/<slug>/index.html)` prints nothing.
**Accepted residual risk, studio-wide (CYB-23):** nobody verifies what a screen reader *speaks*, including whether and when live-region updates and inserted alerts are announced, and what WebKit/Safari exposes; §10 proves only what Chrome's accessibility tree exposes.

## 8. Design tokens

Paste this block verbatim, markers included, at the top of the explainer's inline `<style>`. Dark follows the OS with no JS
(`color-scheme` + `light-dark()`); an optional toggle only sets `data-theme` on `<html>`. Recorded exception: `light-dark()` sets
the browser floor at Chrome 123 / Firefox 120 / Safari 17.5 (mid-2024); older browsers drop the colour tokens and fall back to
browser-default colours in the OS scheme, still readable and focusable. Outside this block, colour and duration literals are
banned (§10 G1 proves it); spacing, type and radii come from tokens; px only for border, outline and stroke widths ≤3px and SVG geometry. New tokens are a system change — raise it.

```css
:root { /* tokens:start */
  color-scheme: light dark;
  /* Colour: light-dark(light, dark). Allowed pairs, both schemes: text --text, --text-2, --accent, --ok, --warn, --danger only on --bg, --surface or --surface-2 (≥4.5:1, lowest 5.23); --on-accent only on --accent (6.70/8.96); --focus and --border-strong on --bg, --surface or --surface-2 (≥3:1, lowest 4.34). Any other pair is a defect (--text-2 on --accent is 1.11:1). */
  --bg: light-dark(#f7f6f2, #131518);        --surface: light-dark(#ffffff, #1c1f24);
  --surface-2: light-dark(#ecebe5, #272b32); --border: light-dark(#cfccc3, #3d424b);
  --border-strong: light-dark(#6f6c64, #8a8f99);
  --text: light-dark(#1c1b19, #edece8);      --text-2: light-dark(#57554f, #b0aea7);
  --accent: light-dark(#1d4ed8, #8ab4ff);    --on-accent: light-dark(#ffffff, #0b1220);
  --focus: light-dark(#c2410c, #fdba74);
  --ok: light-dark(#166f34, #57d38c); --warn: light-dark(#855700, #f5c542); --danger: light-dark(#b42318, #ff8a80);
  /* Type: system stacks only (§2). Two weights, six sizes. */
  --font-sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --text-xs: 0.8125rem; --text-sm: 0.875rem; --text-md: 1rem; --text-lg: 1.25rem;
  --text-xl: clamp(1.5rem, 1.2rem + 1.2vw, 1.875rem); --text-2xl: clamp(1.875rem, 1.4rem + 2vw, 2.5rem);
  --leading-tight: 1.2; --leading-body: 1.55; --weight-regular: 400; --weight-bold: 650;
  /* Space (4px base), target size, radii, shadows, motion */
  --space-1: .25rem; --space-2: .5rem; --space-3: .75rem; --space-4: 1rem;
  --space-5: 1.5rem; --space-6: 2rem; --space-7: 3rem; --space-8: 4rem; --measure: 68ch; --target: 2.75rem;
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 14px; --radius-full: 999px; --dur-fast: 120ms; --dur-base: 200ms; --dur-slow: 320ms;
  --shadow-1: 0 1px 2px light-dark(rgb(0 0 0 / .08), rgb(0 0 0 / .5)); --shadow-2: 0 4px 14px light-dark(rgb(0 0 0 / .10), rgb(0 0 0 / .6));
  --ease-out: cubic-bezier(.2, .7, .2, 1); --ease-in-out: cubic-bezier(.45, 0, .2, 1);
}
:root[data-theme="light"] { color-scheme: light; } :root[data-theme="dark"] { color-scheme: dark; }
@media (prefers-reduced-motion: reduce) { :root { --dur-fast: 0ms; --dur-base: 0ms; --dur-slow: 0ms; } }
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: var(--weight-regular) var(--text-md) / var(--leading-body) var(--font-sans); }
h1, h2, h3 { line-height: var(--leading-tight); font-weight: var(--weight-bold); text-wrap: balance; }
h1 { font-size: var(--text-2xl); } h2 { font-size: var(--text-xl); } h3 { font-size: var(--text-lg); }
p, li, dd { max-width: var(--measure); overflow-wrap: break-word; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; }  /* long error lines must wrap at 390px, not overflow */
fieldset { min-inline-size: 0; } img, svg, video { max-inline-size: 100%; block-size: auto; }  @media (forced-colors: active) { svg circle, svg line { stroke: CanvasText !important; } svg circle { fill: Canvas !important; } svg text { fill: CanvasText !important; } }
button, input, select, textarea { font: inherit; }  button, summary, label:has(input) { min-block-size: var(--target); min-inline-size: var(--target); }  label:has(input) { display: flex; align-items: center; gap: var(--space-2); }  a { color: var(--accent); text-underline-offset: .15em; }
:focus-visible { outline: 3px solid; outline-color: var(--focus); outline-offset: 2px; box-shadow: 0 0 0 2px var(--bg); } /* tokens:end */
```

## 9. Component grammar

Every component: `--surface` on `--bg`, 1px `--border`, `--radius-md`, `--space-4` padding, `--text-2` for metadata. Every state
change also changes a word or glyph, never colour alone; state glyphs on controls and the error state (✓, ⚠) go in `<span aria-hidden="true">`, and the word or the
ARIA state carries the meaning. Colour that carries state (focus, error, pressed, current) goes in the `*-color` longhand, never inside
a shorthand (see `:focus-visible` above). Motion: `--dur-fast`/`--ease-out` on hover, `--dur-base` on enter; nothing moves or advances
on its own (no timers). **Focus** stays on the control used or moves to the target named below; a re-render never removes the focused element. Regions marked (§6) are in the static markup and renders set only their text (the quiz result's ✓/✗ is part of that text).

- **Timeline entry** — `<ol class="timeline">` > `<li>` with a date, `<h3>`, `<p>`, source link, longer detail in `<details>`.
  `<time datetime>` only as precise as §4 allows (`1984`, `1996-04`); approximate, in-world and unknown dates are a `<span>` with
  the visible qualifier ("c. 1985", "date unknown"). Rail 2px `--border`; marker 12px `--accent` disc. Current entry:
  `aria-current="true"`, 3px solid left border with `border-left-color: var(--accent)`, `--weight-bold` title.
- **Entity card** — `<article id="<id>" tabindex="-1">` with `<h3 id="h-<id>">` name, `<dl>` facts, and one
  `<button id="b-<id>" aria-labelledby="b-<id> h-<id>" aria-expanded>` "Details" (announced "Details <name>") that toggles an
  in-card region; focus stays on it. The card is not the target; the button is. `--shadow-1`; hover `--shadow-2`. `null` renders
  `<dd>` "unknown" in italic `--text-2` (§4); `confidence` renders a `--text-xs` chip ("approx." / "disputed") next to the value.
- **Filter bar** — `<fieldset>` + visible `<legend>`; options are `<button aria-pressed>` chips, ≤7 visible (Hick's law), the rest
  in `<details>` "More". Chip: `--radius-full`, `--space-1 --space-3`, `--text-sm`, 1px `--border-strong`, `--target` tall. Pressed:
  `--accent` bg, `--on-accent` text, leading "✓" in `<span aria-hidden="true">` (the name never changes). Toggling keeps focus on the chip. Count in `<output aria-live="polite">` (§6).
- **Relationship map** — first a `<details>` "As a list": one `<li>` per edge ("A — relation → B") from the same `DATA` array;
  then `<a class="skip" href="#<id of the element after the svg>">` "Skip map" (may be visually hidden until focused, never `display: none`); then the inline `<svg role="group" aria-labelledby="<title id>">` with `<title id>` (never `role="img"`). The SVG is hidden by a CSS `@media (width < 40rem)` rule, and the list is `open` whenever that query matches, set on load and on the `matchMedia` `change` event. Node:
  `<a href="#<id>">` (focusable, named) wrapping `<circle r="22">` `--surface` fill, 2px `--accent` stroke, `--text-sm` label;
  edges 1.5px `--border-strong` with a text label. The SVG renders 1 unit = 1px (`inline-size: <viewBox width>px`, width ≤560,
  `max-inline-size: 100%`) with `overflow: visible`, so rings never clip. Node Tab order = `DATA` order = list order. A node link
  clears any filter hiding its target, then focuses the card (instant scroll under reduced motion). Forced colours: the §8
  `forced-colors` rule (`!important`, so it beats any component selector) gives circles, lines and text `Canvas`/`CanvasText`; add no colour here (§8 bans literals outside the block).
- **Quiz question** — `<form tabindex="-1">` > `<fieldset tabindex="-1">` + `<legend>` question; `<label><input type="radio">`
  options; `<button type="submit">` "Check" (focus stays) and, once checked, `<button type="button">` "Next question" → the new
  `<fieldset>`; after the last question the form shows the summary and takes focus. Result in an `<output aria-live="polite">` (§6)
  outside the fieldset: "✓ Correct" (`--ok`) or "✗ Not quite" (`--danger`), one sentence and its source. Score in a plain `<span>`.
- **Empty state** — at 0 results the count `<output>` (the one live region, §6) itself says *why* ("No entries match 'Beast era'") in place
  of the count, so it is heard; beneath it a non-live box, never blank: 1px dashed `--border-strong`, `--space-6` padding, centred `--text-2` `<p>` "Try fewer filters", `<button>` "Clear filters" → first chip.
- **Error state** — what §6's render wrapper renders into: `<div role="alert">` with "⚠" (`aria-hidden`) and "This section failed to render", one
  sentence on what to do, and the message in `<pre>` (`--font-mono`, `--text-xs`). `border: 2px solid` + `--surface-2` bg +
  `border-color: var(--danger)`. Styled by this stylesheet, not JS, so it looks broken even when the JS is what broke.
- **Theme toggle** (optional) — `<button type="button" aria-pressed>` "Dark theme"; initial `aria-pressed` = `matchMedia('(prefers-color-scheme: dark)').matches`
  (tracked on that query's `change` event until the first press); `data-theme` is set on `<html>` only on press: `"dark"` when pressed, `"light"` when not. Pressed shows a leading "✓" (`aria-hidden`). Focus stays on it.

## 10. Accessibility bar

Every check runs on the `file://` page in Chrome DevTools (verified in Chrome 154) with nothing installed. `G*`/`S*` are the grep and console lines in the block below the table; paste the `G*` lines into the shell as printed (verified in interactive zsh and bash). Then run rows "Real heading outline" and "Works at 390px" again with DevTools › Settings › Disable JavaScript (JS-rendered components are absent, not broken: §6). Fail any one and the page does not ship (§7).

| Rule | Check |
|---|---|
| Contrast by construction: text ≥4.5:1, UI edges/icons ≥3:1, both schemes | Colour only via §8 tokens, in the §8 allowed pairs: `G1` and `G2` return nothing (a colour hit is removed, not justified; `#` plus digits inside `DATA` or prose is not a colour). Accepted gap: a named colour inside a non-state shorthand (`border: 1px solid red`) is not grepped; Lighthouse covers it for text, and §9 keeps state colour in longhands. Then **Lighthouse › Mode: Snapshot › Accessibility** (Navigation refuses `file://`; Snapshot does not), toggle at its default (a set `data-theme` overrides emulation), Rendering › Emulate `prefers-color-scheme` light then dark, once per state: load, chip pressed, quiz wrong, quiz right, empty, error, all `<details>` open. Zero contrast failures each run. |
| Never colour alone: pressed, current, correct/wrong, error, "unknown", `confidence` chips, theme toggle, map nodes and edges | Rendering › Emulate CSS media feature `forced-colors: active`, in both schemes. Every state above is still identifiable by text, glyph, weight or border, and the Accessibility pane shows `pressed`/`current`/`expanded` for each (chip, timeline entry, Details). |
| Visible focus on every stop, never clipped | Tab through the whole page: each stop shows the 3px `--focus` ring with all four sides visible (map: `overflow: visible`). `G2` returns nothing. |
| Full keyboard path, no trap, order = DOM order = visual order | Key map: Tab/Shift+Tab between controls; Enter/Space activate; arrows only inside native radio groups; Escape only closes a `<dialog>` and returns focus to its opener; no other key handlers; no positive `tabindex` (`G4`) and no CSS reordering of focusables. Run in Chrome (Safari skips links by default). Paste `S1`, walk every control: the logged order is DOM order and, in the map, `DATA` order. |
| Focus is never lost | With `S1` pasted before the walk: toggle a chip, Clear filters, Details, a map node, Check, Next question, the last question, the theme toggle. It warns nothing and `document.activeElement` is the §9 target each time. |
| Accessibility-tree exposure (what Chrome exposes to assistive tech; whether it is *spoken* is unverified, §7) | Read the tree with CDP `Accessibility.getFullAXTree` (verified in headless Chrome 154); a person reads the same nodes one at a time in DevTools › Elements › Accessibility. A node's text = the concatenated `name`s of its `StaticText` descendants (a `status`/`alert` node's own `name` is empty). At load the `heading` nodes and levels match the outline, and each count and quiz-result region is a `status` (or `live: polite`) node with no text. Toggle one chip: the count node's text changes. Filter to zero: the count node's text is the why ("No entries match …"). Answer one wrong, then one right: the result node's text is the ✗, then the ✓ sentence. Throw inside a render (§6): an `alert` node holds the "This section failed to render" sentence. Each card button is named "Details <name>" and a pressed chip's name has no "✓"; with "As a list" open, the map list exposes one `listitem` per edge. |
| Real heading outline | Console: `[...document.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading]')].map(h=>h.tagName+' '+h.textContent.trim())` shows one `H1`, only `H1`–`H3`, no `role=heading`, no skipped level, no empty heading (a bare `H2 `); `S2` returns `[]` (a styled non-heading at `--text-lg` or above). "Reads as a table of contents" is reviewer judgment. |
| `prefers-reduced-motion` honoured | Rendering › Emulate `prefers-reduced-motion: reduce`, reload: nothing moves and every interaction still works. Every `G3` hit is gated on `matchMedia('(prefers-reduced-motion: reduce)').matches`; the map layout is at rest before first paint. |
| Works at 390px | `<meta name="viewport" content="width=device-width, initial-scale=1">` present; `G4` returns nothing (`overflow-x` hidden/clip is banned on `html` and `body`, allowed on a named scroll region). Device toolbar 390×844, type **Mobile**: `document.documentElement.scrollWidth <= 390`; `S3` and `S4` return `[]`; body text computes to 16px; the map list is open and the SVG hidden, both on a fresh load and after resizing from 1280 to 390 without a reload. |
| Targets: primary ≥44×44 CSS px; inline links within a sentence are exempt (WCAG 2.5.8) | Primary = every `<button>`, `<summary>`, radio `<label>` and map node (the §8 `--target` rule). Element picker at 390 on a chip, Check, a radio label, Details and the summary, and at 641 on a map node (≥44, label ≥13px): read the box. |
| Names and language | Same Lighthouse run: "Buttons have an accessible name", "Links have a discernible name", "Image elements have alt" pass; `<svg>` has `<title>`; non-empty `<title>`; `<html lang="en">`; `lang` on non-English passages. |
| Relationship map | List, then "Skip map", then the SVG in the DOM; Enter on "Skip map" lands focus after the SVG; Accessibility pane shows the SVG as `group` named by its `<title>`; `document.querySelectorAll('.map li').length===DATA.edges.length`; node order = `DATA` order; a node link whose target is filtered out clears the filter and lands focus on the card; at 641 no ring is clipped. |
| 400% zoom and text spacing reflow | Cmd/Ctrl + to 400% at 1280 wide (320 CSS px): no horizontal scroll; no overlap: `document.elementFromPoint` at each control's centre returns that control (or a child of it); the map list is open and the SVG hidden. Then paste `S5`; `S4` still returns `[]`. |

```text
: G1; sed '/tokens:start/,/tokens:end/d' index.html | grep -noE '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(|oklch\(|light-dark\(|(color|fill|stroke|background)(-color)?: *[a-z-]+|(fill|stroke|color)="[^"]+"|\.style\.[a-zA-Z]*([cC]olor|fill|stroke)' | grep -vE '(: *|=")(var|inherit|currentColor|transparent|none|unset|initial)\b'
: G2; grep -nE 'opacity *:|color-mix\(|filter: *[a-z-]+\(|mix-blend-mode|outline(-style|-width|-color)?: *(none|0|transparent)|\.style\.(opacity|filter|outline)' index.html
: G3; grep -nE 'scroll-behavior|smooth|\.animate\(|requestAnimationFrame|setInterval' index.html
: G4; grep -nE 'maximum-scale|user-scalable|overflow-x: *(hidden|clip)|tabindex="?[1-9]' index.html
addEventListener('focusin',e=>console.log(e.target)); addEventListener('focusout',e=>setTimeout(()=>document.activeElement===document.body&&console.warn('focus lost from',e.target)))  // S1
[...document.querySelectorAll('body :not(h1,h2,h3,h1 *,h2 *,h3 *)')].filter(e=>!e.children.length&&e.textContent.trim()&&parseFloat(getComputedStyle(e).fontSize)>=20)  // S2
[...document.querySelectorAll('a,button,input,summary')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&(r.left<0||r.right>390)})  // S3: off-screen controls
[...document.querySelectorAll('body *')].filter(e=>e.clientWidth&&e.scrollWidth>e.clientWidth+1&&getComputedStyle(e).overflowX!=='visible')  // S4: clipped text
document.head.append(Object.assign(document.createElement('style'),{textContent:'*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}'}))  // S5: text spacing
```
