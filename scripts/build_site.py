#!/usr/bin/env python3
"""Assemble the Pages artifact: _site/<slug>/index.html plus a generated _site/index.html.

The explainer files are copied byte-for-byte; nothing is built or rewritten.
"""
import html
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check import Page  # noqa: E402

src, out = Path("explainers"), Path("_site")
shutil.rmtree(out, ignore_errors=True)
out.mkdir()
items = []
for d in sorted(p for p in src.iterdir() if p.is_dir()) if src.is_dir() else []:
    page = d / "index.html"
    if not page.is_file():
        continue
    (out / d.name).mkdir()
    shutil.copyfile(page, out / d.name / "index.html")
    p = Page()
    p.feed(page.read_text(encoding="utf-8"))
    items.append((d.name, p.title.strip() or d.name))

rows = "\n".join(
    f'      <li><a href="{html.escape(s)}/">{html.escape(t)}</a></li>' for s, t in items
) or "      <li>No explainers published yet.</li>"
(out / "index.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cybertron explainers</title>
  <style>
    body {{ font: 1.125rem/1.5 system-ui, sans-serif; max-width: 40rem; margin: 3rem auto; padding: 0 1rem; color: #1a1a1a; background: #fff; }}
    a {{ color: #0b57d0; }}
    li {{ margin: .5rem 0; }}
  </style>
</head>
<body>
  <main>
    <h1>Cybertron explainers</h1>
    <ul>
{rows}
    </ul>
  </main>
</body>
</html>
""", encoding="utf-8")
(out / ".nojekyll").touch()
print(f"built {len(items)} explainer(s) into {out}/")
