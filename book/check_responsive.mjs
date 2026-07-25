// check_responsive.mjs — deploy-blocking responsive-layout gate for the landing page.
//
// WHY this exists: the landing's tiled region (`<div class="masonry">`, CSS `columns: 320px`)
// is the author's stated deliverable — "at much higher width we get a DIFFERENT layout than at
// tight phone width." That success metric is here turned into a mechanical, deploy-blocking check:
// load the built index.html in headless Chrome, measure the number of masonry columns at a wide
// (2560px) and a phone (390px) viewport, and ASSERT the wide layout is multi-column while the phone
// layout collapses to exactly one column. A regression that flattens the masonry (e.g. `columns:1`
// everywhere, or a dropped media query) fails the deploy.
//
// This is NOT part of `catalog.py validate` (that gate is stdlib-only, clone-and-run, no browser
// dep). Like the PDF density/mermaid gates, it is a non-stdlib deploy-time check that needs a
// browser — so it lives here in book/ alongside render_pdf.mjs and reuses the same Puppeteer dep.
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
const WIDE_MIN_COLUMNS = 3; // a wide viewport must tile into >= 3 masonry columns
const PHONE_COLUMNS = 1; // a phone viewport must collapse to exactly 1 column

const executablePath =
  process.env.PUPPETEER_EXECUTABLE_PATH || process.env.CHROME_PATH || undefined;

// Count how many distinct masonry columns the tiles occupy, by bucketing the left-edge
// x-positions of the direct `.masonry > .tile` children. CSS multi-column lays each column's tiles
// at a shared left x, so the number of distinct left-edges == the number of columns. `.tile.wide`
// tiles use `column-span: all` and sit at the container's left edge spanning every column — they do
// NOT indicate a *tile column*, so they're excluded from the measurement (otherwise they'd inject a
// spurious x-bucket at the container origin). Buckets tolerate sub-pixel rounding (8px).
async function measureColumns(page, viewportWidth) {
  await page.setViewport({ width: viewportWidth, height: 1400, deviceScaleFactor: 1 });
  // Give layout a tick to reflow after the viewport change.
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  return page.evaluate(() => {
    const masonry = document.querySelector(".masonry");
    if (!masonry) return { error: "no .masonry element found on the landing page" };
    const tiles = Array.from(masonry.children).filter(
      (el) => el.classList.contains("tile") && !el.classList.contains("wide")
    );
    if (tiles.length === 0) return { error: "no non-wide .masonry > .tile children found" };
    const lefts = tiles.map((el) => el.getBoundingClientRect().left);
    // Bucket left-edges with an 8px tolerance to absorb sub-pixel rounding.
    const buckets = [];
    for (const x of lefts.sort((a, b) => a - b)) {
      if (buckets.length === 0 || Math.abs(x - buckets[buckets.length - 1]) > 8) buckets.push(x);
    }
    return { columns: buckets.length, tileCount: tiles.length };
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
    console.error(`ERROR measuring masonry: ${wide.error || phone.error}`);
    process.exit(1);
  }

  console.log("Responsive-layout gate — landing `.masonry` column counts:");
  console.log(`  wide  (${WIDE_VIEWPORT}px): ${wide.columns} columns  (${wide.tileCount} tiles)`);
  console.log(`  phone (${PHONE_VIEWPORT}px): ${phone.columns} columns  (${phone.tileCount} tiles)`);

  const wideOk = wide.columns >= WIDE_MIN_COLUMNS;
  const phoneOk = phone.columns === PHONE_COLUMNS;

  if (!wideOk) {
    console.error(
      `FAIL: wide viewport rendered ${wide.columns} columns, need >= ${WIDE_MIN_COLUMNS}. ` +
        "The landing did not tile into a multi-column layout at wide width."
    );
    failed = true;
  }
  if (!phoneOk) {
    console.error(
      `FAIL: phone viewport rendered ${phone.columns} columns, need exactly ${PHONE_COLUMNS}. ` +
        "The landing did not collapse to a single column at phone width."
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
