# cybertron-explainers

Self-contained interactive web explainers. Each explainer is a standalone page that
teaches one subject through timelines, browsers, maps and quizzes.

## What this repo ships

One directory per explainer under `explainers/`. An explainer is a finished page —
content, interaction and styling together — not a component in a framework.

A page is expected to do the teaching work itself: a scrubbable timeline, a
filterable browser, a relationship map, progressive disclosure instead of a wall of
text, and a short quiz that explains its answers rather than chasing a score.

## The self-contained rule

**Every explainer is a single HTML file that opens from `file://` and makes zero
network requests at load.**

That is the rule, and it is stated this way because it is testable: open the page
from disk with the network off, and it must work completely. In practice it means:

- No build step. The file in the repo is the file that ships.
- No CDN, no external fonts, no remote data fetches, no analytics.
- CSS and JavaScript live inline. Images and data are inlined or omitted.

The rule exists so an explainer stays readable years from now, survives being
emailed as an attachment, and cannot quietly break because someone else's host went
away.

## Source discipline

Every factual claim carries a source note next to the data it describes. Unknown
stays unknown — nothing is invented to fill a gap. Where sources genuinely
contradict each other, the contradiction is the content, not something to smooth
over.

## Conventions

The full studio conventions — file layout, the data/view split, the performance
budget, the design token set, and the accessibility bar every page must clear —
live in `EXPLAINER.md` at the root of this repo.

## Layout

```
explainers/          one directory per explainer
EXPLAINER.md         studio conventions every explainer inherits
README.md            this file
```
