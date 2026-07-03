#!/usr/bin/env bash
# Bootstrap OPTIONAL dev/test dependencies for the catalogue.
#
# The catalogue tool (catalog.py) and its test suite's Tier 1 are stdlib-Python and need NOTHING —
# `git clone && python3 catalog.py build` just works. This script installs the OPTIONAL Node tooling
# used by the Tier-2 accessibility check (axe-core). Requires Node.js + a Chrome/Chromium browser.
#
# See DEVELOP.md for the full dependency map and how the test tiers work.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Install Node.js first: https://nodejs.org  (then re-run ./setup.sh)"
  exit 2
fi

echo "Installing axe-core CLI (Tier-2 a11y test dependency)…"
npm install

echo
echo "Done. Run the full test suite with:   python3 catalog.py test"
echo "(axe needs a Chrome/Chromium browser on the machine; without one, the axe tier auto-skips.)"
