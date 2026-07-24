// render_pdf.mjs — Paged.js → PDF renderer for the MAGE print edition.
//
// WHY a Node script (not headless-Chrome `--print-to-pdf`, not `pagedjs-cli`):
//   • Chrome `--print-to-pdf` snapshots the page before Paged.js finishes its async
//     DOM re-pagination, so it emits ~3 unpaginated pages regardless of virtual-time-budget.
//   • `pagedjs-cli` paginates correctly but its `--page-size` / `-w` / `-h` flags are broken
//     in the version resolved via npx (always emits a US-Letter sheet), ignoring the CSS
//     `@page { size: 6in 9in }`, so the 6×9 layout lands on a letter sheet with dead margins.
// This script loads the combined print HTML, WAITS for Paged.js to signal completion, then
// prints with `preferCSSPageSize: true` so the 6×9 book trim from the print stylesheet is honored.
//
// Invoked by `build_book_html.py --pdf` (which builds the print HTML first). Also runs in the
// Pages CI. Chrome path comes from PUPPETEER_EXECUTABLE_PATH or CHROME_PATH; on CI the runner's
// preinstalled google-chrome is used.

import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import puppeteer from "puppeteer";

const inputHtml = process.argv[2];
const outputPdf = process.argv[3];
if (!inputHtml || !outputPdf) {
  console.error("usage: node render_pdf.mjs <print.html> <out.pdf>");
  process.exit(2);
}

const executablePath =
  process.env.PUPPETEER_EXECUTABLE_PATH || process.env.CHROME_PATH || undefined;

const browser = await puppeteer.launch({
  headless: "new",
  executablePath,
  args: ["--no-sandbox", "--disable-setuid-sandbox"],
});

try {
  const page = await browser.newPage();
  // Surface page console errors (a Paged.js CSS error would otherwise be silent).
  page.on("pageerror", (e) => console.error("PAGE ERROR:", e.message));

  await page.goto(pathToFileURL(inputHtml).href, {
    waitUntil: "networkidle0",
    timeout: 120000,
  });

  // Wait for Paged.js to finish repaginating. The polyfill adds `.pagedjs_pages` to the DOM
  // and exposes the rendered flow; we poll until the page container exists and its child count
  // stops growing (pagination complete). Fail loud if it never completes.
  await page.waitForFunction(
    () => document.querySelector(".pagedjs_pages") !== null,
    { timeout: 180000 }
  );
  // Let layout settle: wait until the rendered page count is stable across two ticks.
  await page.waitForFunction(
    () => {
      const pages = document.querySelectorAll(".pagedjs_page");
      const n = pages.length;
      if (window.__lastPageCount === n && n > 0) return true;
      window.__lastPageCount = n;
      return false;
    },
    { timeout: 180000, polling: 400 }
  );

  await page.pdf({
    path: outputPdf,
    preferCSSPageSize: true, // honor `@page { size: 6in 9in }` from the print stylesheet
    printBackground: true,
    displayHeaderFooter: false,
  });

  const pageCount = await page.evaluate(
    () => document.querySelectorAll(".pagedjs_page").length
  );
  console.log(`rendered ${outputPdf} — Paged.js laid out ${pageCount} pages`);
} finally {
  await browser.close();
}
