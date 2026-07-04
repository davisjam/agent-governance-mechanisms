#!/usr/bin/env bash
# Bootstrap OPTIONAL dev/test dependencies for the catalogue.
#
# The catalogue tool (catalog.py) and its test suite's Tier 1 are stdlib-Python and need NOTHING —
# `git clone && python3 catalog.py build` just works. This script installs the OPTIONAL Node tooling
# used by the Tier-2 checks (axe-core a11y + html-validate HTML validity). axe also needs a Chrome/Chromium browser.
#
# See DEVELOP.md for the full dependency map and how the test tiers work.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Install Node.js first: https://nodejs.org  (then re-run ./setup.sh)"
  exit 2
fi

echo "Installing Tier-2 test tooling (axe-core + html-validate)…"
# `npm ci` installs the EXACT tree pinned in package-lock.json (with integrity hashes) — deterministic,
# and it never silently bumps a dependency the way `npm install` can. Same command CI uses.
npm ci

echo
echo "Done. Run the full test suite with:   python3 catalog.py test"
echo "(axe needs a Chrome/Chromium browser on the machine; without one, the axe tier auto-skips.)"
