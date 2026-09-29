# Rollback

Publishing is `.github/workflows/pages.yml`: every push to `main` runs the checks,
builds `_site/`, and deploys it to GitHub Pages. Live URL:
`https://jsneij.github.io/cybertron-explainers/` (each explainer at `/<slug>/`).

The site is exactly the last successful run on `main`. To undo a bad publish, make
`main` good again, or redeploy an earlier good run.

## 1. Revert (default; leaves history intact)

```sh
git checkout main && git pull
git revert <bad-commit-sha>          # or: git revert -m 1 <merge-sha>
git push origin main                 # via PR if branch protection requires it
```

The push triggers the normal publish. Takes about a minute.

## 2. Redeploy a previous good run (fastest, no new commit)

```sh
gh run list --workflow Publish --status success --limit 10   # pick the last good run
gh run rerun <run-id>
```

Re-running redeploys that run's commit. `main` still contains the bad commit, so
follow up with step 1 or the next merge will republish it.

## 3. Take the whole site down (emergency)

```sh
gh api -X DELETE repos/jsneij/cybertron-explainers/pages
```

Re-enabling needs Settings > Pages > Source: **GitHub Actions** (or
`gh api -X POST repos/jsneij/cybertron-explainers/pages -f build_type=workflow`).
Requires repo admin; do it only with approval on the ticket.

## Verify

```sh
curl -sI https://jsneij.github.io/cybertron-explainers/ | head -1     # HTTP/2 200
gh run list --workflow Publish --limit 1                              # latest run: success
```

## Blast radius

Static pages only, no data or accounts. A bad deploy shows readers a broken or
missing explainer until rolled back. Nothing else depends on the site.
