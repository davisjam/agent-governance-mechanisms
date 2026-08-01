// check_responsive.mjs — deploy-blocking responsive-layout gate for the landing page.
//
// WHY this exists: the landing opens with a hero block (`<div class="hero-grid">`, CSS
// `grid-template-columns: minmax(0,1.02fr) minmax(0,1fr)`) that lays its prose beside its figure —
// a two-column split at desktop width that collapses to a single stacked column on a phone (the
// `@media (max-width:900px){ .hero-grid{ grid-template-columns:1fr } }` rule). That responsive
// behaviour — "at much higher width we get a DIFFERENT layout than at tight phone width" — is the
// author's stated deliverable, and this check turns it into a mechanical, deploy-blocking assertion:
// load the built index.html in headless Chrome, measure how many columns the hero grid's direct
// children occupy at a wide (2560px) and a phone (390px) viewport, and ASSERT the wide layout is
// multi-column while the phone layout collapses to exactly one column. A regression that flattens
// the hero (e.g. a dropped media query, or a `grid-template-columns:1fr` everywhere) fails the deploy.
//
// The success metric is unchanged from the prior gate — "a structurally different layout at wide vs
// phone, collapsing to a single column on phone." Only the measured element moved: the old landing's
// `.masonry` tile region was removed in the approved landing redraft, and `.hero-grid` is the element
// that now carries the responsive split.
//
// This is NOT part of `catalog.py validate` (that gate is stdlib-only, clone-and-run, no browser
// dep). It is a non-stdlib deploy-time check that needs a browser — so it lives here in book/ and
// reuses the Puppeteer dep that the build-time mermaid-SVG pre-render already installs.
//
// Invoked by `python3 catalog.py check-responsive` and by the Pages CI. Chrome comes from Puppeteer's
// bundled Chromium (installed by `npm ci` in book/) unless PUPPETEER_EXECUTABLE_PATH / CHROME_PATH
// overrides it. Exit 0 = PASS (prints the measured column counts); exit non-zero = FAIL (prints why).

import { pathToFileURL } from "node:url";
import { existsSync } from "node:fs";
import puppeteer from "puppeteer";

const indexHtml = process.argv[2];
if (!indexHtml) {
  console.error("usage: node check_responsive.mjs <abs-path-to-index.html>");
  process.exit(2);
}
if (!existsSync(indexHtml)) {
  console.error(`ERROR: index.html not found at ${indexHtml} — run \`python3 catalog.py build\` first`);
  process.exit(2);
}

// Thresholds — the assertion the author's success metric compiles to.
const WIDE_VIEWPORT = 2560;
const PHONE_VIEWPORT = 390;
const WIDE_MIN_COLUMNS = 2; // a wide viewport must lay the hero into >= 2 columns (prose | figure)
const PHONE_COLUMNS = 1; // a phone viewport must collapse to exactly 1 column

const executablePath =
  process.env.PUPPETEER_EXECUTABLE_PATH || process.env.CHROME_PATH || undefined;

// Count how many distinct columns the `.hero-grid` occupies, by bucketing the left-edge x-positions
// of its DIRECT children (`.hg-prose`, `.hg-fig`). CSS grid lays each column's items at a shared left
// x, so the number of distinct left-edges == the number of columns: two edges when the prose sits
// beside the figure (wide), one edge when they stack (phone). Buckets tolerate sub-pixel rounding (8px).
async function measureColumns(page, viewportWidth) {
  await page.setViewport({ width: viewportWidth, height: 1400, deviceScaleFactor: 1 });
  // Give layout a tick to reflow after the viewport change.
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  return page.evaluate(() => {
    const grid = document.querySelector(".hero-grid");
    if (!grid) return { error: "no .hero-grid element found on the landing page" };
    const items = Array.from(grid.children).filter((el) => el.nodeType === 1);
    if (items.length === 0) return { error: "no .hero-grid direct children found" };
    const lefts = items.map((el) => el.getBoundingClientRect().left);
    // Bucket left-edges with an 8px tolerance to absorb sub-pixel rounding.
    const buckets = [];
    for (const x of lefts.sort((a, b) => a - b)) {
      if (buckets.length === 0 || Math.abs(x - buckets[buckets.length - 1]) > 8) buckets.push(x);
    }
    return { columns: buckets.length, itemCount: items.length };
  });
}

const browser = await puppeteer.launch({
  headless: "new",
  executablePath,
  args: ["--no-sandbox", "--disable-setuid-sandbox"],
});

let failed = false;
try {
  const page = await browser.newPage();
  page.on("pageerror", (e) => console.error("PAGE ERROR:", e.message));
  await page.goto(pathToFileURL(indexHtml).href, { waitUntil: "networkidle0", timeout: 60000 });

  const wide = await measureColumns(page, WIDE_VIEWPORT);
  const phone = await measureColumns(page, PHONE_VIEWPORT);

  if (wide.error || phone.error) {
    console.error(`ERROR measuring .hero-grid: ${wide.error || phone.error}`);
    process.exit(1);
  }

  console.log("Responsive-layout gate — landing `.hero-grid` column counts:");
  console.log(`  wide  (${WIDE_VIEWPORT}px): ${wide.columns} columns  (${wide.itemCount} items)`);
  console.log(`  phone (${PHONE_VIEWPORT}px): ${phone.columns} columns  (${phone.itemCount} items)`);

  const wideOk = wide.columns >= WIDE_MIN_COLUMNS;
  const phoneOk = phone.columns === PHONE_COLUMNS;

  if (!wideOk) {
    console.error(
      `FAIL: wide viewport rendered ${wide.columns} columns, need >= ${WIDE_MIN_COLUMNS}. ` +
        "The hero grid did not lay prose beside figure at wide width."
    );
    failed = true;
  }
  if (!phoneOk) {
    console.error(
      `FAIL: phone viewport rendered ${phone.columns} columns, need exactly ${PHONE_COLUMNS}. ` +
        "The hero grid did not collapse to a single column at phone width."
    );
    failed = true;
  }
  if (!failed) {
    console.log(
      `PASS: wide (${wide.columns}) >= ${WIDE_MIN_COLUMNS} AND phone (${phone.columns}) == ${PHONE_COLUMNS} ` +
        "— the landing renders a structurally different layout at wide vs phone width."
    );
  }
} finally {
  await browser.close();
}

process.exit(failed ? 1 : 0);
