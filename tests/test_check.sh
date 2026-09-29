#!/bin/sh
# The checker must pass the good fixture and fail closed on each bad one.
set -u
cd "$(dirname "$0")/.."
mkdir -p "${TMPDIR:-/tmp}" && t=$(mktemp -d)
trap 'rm -rf "$t"' EXIT
rc=0
for f in good bad-cdn bad-fetch; do
  rm -rf "$t/e" && mkdir "$t/e" && cp -R "tests/fixtures/$f" "$t/e/$f"
  python3 scripts/check.py "$t/e" >/dev/null; got=$?
  want=1; [ "$f" = good ] && want=0
  [ "$got" -eq "$want" ] && echo "pass $f" || { echo "FAIL $f (exit $got, want $want)"; rc=1; }
done
exit $rc
