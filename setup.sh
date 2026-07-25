#!/usr/bin/env bash
# Bootstrap the catalogue's dev/test Node tooling — BOTH node trees, so every check that runs in CI
# also runs locally (find failures where they're observable, not only on the runner).
#
# Tier-1 tests are stdlib-Python. But this is no longer a "needs nothing" build:
#   - book/  (REQUIRED by the build + deploy gates): mermaid-cli (mmdc) renders every ```mermaid fence to
#     inline SVG at build time, and Puppeteer drives the browser gates (book PDF, responsive-layout,
#     console-error). Without it, `python3 catalog.py build` fails loud on the first mermaid diagram.
#   - root   (Tier-2 checks): html-validate (HTML validity) + axe-core (accessibility).
# `npm ci` installs the EXACT tree pinned in each package-lock.json — deterministic, same as CI. Needs Node 22+.
#
# See DEVELOP.md for the full dependency map and how the test tiers work.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Install Node.js 22+ first: https://nodejs.org  (then re-run ./setup.sh)"
  exit 2
fi

echo "Installing book/ build + gate tooling (mermaid-cli for the build, Puppeteer for the PDF/responsive/console gates)…"
( cd book && npm ci )

echo "Installing root Tier-2 tooling (html-validate + axe-core)…"
npm ci

echo
echo "Done — both node trees installed. Every CI check now runs locally:"
echo "  python3 catalog.py test          # build + full suite (T1 + T2 html-validate / axe)"
echo "(the mermaid render + PDF/responsive/console gates use book/ Puppeteer's bundled Chromium.)"
