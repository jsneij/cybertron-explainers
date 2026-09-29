#!/usr/bin/env python3
"""Minimum useful CI for explainers: each page parses and is self-contained.

Checks every explainers/<slug>/index.html:
  - the file exists and parses as HTML with a <title>
  - no external resource is referenced (src/href/srcset/poster/action to http(s):// or //);
    plain <a href> links are navigation, not loads, and are allowed
  - no CSS url()/@import to a remote host, in <style> blocks or style attributes
  - no obvious network calls in inline scripts (fetch, XMLHttpRequest, WebSocket,
    EventSource, sendBeacon, import(), importScripts)
  - no sibling files: the directory holds index.html only

Exit 1 with one line per violation. Stdlib only, no install step.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REMOTE = re.compile(r"^\s*(?:https?:)?//", re.I)
CSS_REMOTE = re.compile(r"""(?:url\(\s*['"]?|@import\s+['"]?)\s*(?:https?:)?//""", re.I)
JS_NET = re.compile(
    r"\b(fetch\s*\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|importScripts\s*\(|import\s*\()"
)
URL_ATTRS = {"src", "href", "srcset", "poster", "action", "data", "formaction"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.problems, self.title, self._in = [], "", None

    def handle_starttag(self, tag, attrs):
        self._in = tag if tag in ("title", "script", "style") else self._in
        for k, v in attrs:
            v = v or ""
            if k in URL_ATTRS and not (tag == "a" and k == "href") and REMOTE.match(v.split(",")[0] if k == "srcset" else v):
                self.problems.append(f"<{tag} {k}> loads remote URL: {v[:80]}")
            if k == "style" and CSS_REMOTE.search(v):
                self.problems.append(f"<{tag}> style attribute loads remote URL")
        if tag == "meta" and dict(attrs).get("http-equiv", "").lower() == "refresh":
            self.problems.append("meta refresh navigates away")

    def handle_endtag(self, tag):
        if tag == self._in:
            self._in = None

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in == "style" and CSS_REMOTE.search(data):
            self.problems.append("<style> loads remote URL via url()/@import")
        elif self._in == "script" and JS_NET.search(data):
            self.problems.append(f"<script> makes a network call: {JS_NET.search(data).group(1)}")


def check(page: Path):
    out = []
    if not page.is_file():
        return [f"missing {page.name}"]
    extras = sorted(p.name for p in page.parent.iterdir() if p.name != "index.html")
    if extras:
        out.append(f"directory must hold index.html only, found: {', '.join(extras)}")
    p = Page()
    try:
        p.feed(page.read_text(encoding="utf-8"))
        p.close()
    except Exception as e:  # noqa: BLE001 - any parse failure is a failed check
        return out + [f"does not parse: {e}"]
    if not p.title.strip():
        out.append("missing or empty <title>")
    return out + p.problems


def main(root: Path) -> int:
    dirs = sorted(d for d in root.iterdir() if d.is_dir()) if root.is_dir() else []
    failed = 0
    for d in dirs:
        problems = check(d / "index.html")
        for msg in problems:
            print(f"FAIL {d.name}: {msg}")
        failed += bool(problems)
        if not problems:
            print(f"ok   {d.name}")
    print(f"{len(dirs)} explainer(s) checked, {failed} failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "explainers")))
