// One-browser axe-core scan over a list of URLs.
//
// WHY this exists (not `@axe-core/cli`): the CLI launches a fresh Chrome per URL, so a whole-site scan
// pays the ~1-3s browser cold-start cost once per page (dozens of launches, ~20 min). This script
// launches ONE headless Chrome and reuses it across every URL — the per-page cost drops to a navigation
// plus the axe run. Same engine (@axe-core/webdriverjs + axe-core), same pinned versions from npm ci.
//
// Invocation: node tests/axe_scan.cjs <load-delay-ms> <url> [<url> ...]
// Output: one `Violation of "<rule-id>" with <n> node(s)` line per (page, rule) with findings — the
//   exact shape the Python caller (tests/external.py:check_axe) already parses. Exits 2 if any page
//   yielded a violation, 1 on a launch/run error (no browser), 0 when clean.
'use strict';
const { Builder } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const AxeBuilder = require('@axe-core/webdriverjs');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const loadDelay = parseInt(process.argv[2], 10) || 0;
  const urls = process.argv.slice(3);
  if (urls.length === 0) {
    console.error('axe_scan: no URLs given');
    process.exit(1);
  }

  const opts = new chrome.Options()
    .addArguments('--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage');
  let driver;
  try {
    driver = await new Builder().forBrowser('chrome').setChromeOptions(opts).build();
  } catch (e) {
    console.error('axe_scan: could not launch headless Chrome: ' + (e && e.message));
    process.exit(1);
  }

  let anyViolation = false;
  try {
    for (const url of urls) {
      await driver.get(url);
      if (loadDelay > 0) await sleep(loadDelay); // let async content (Mermaid CDN, figure iframes) settle
      const results = await new AxeBuilder(driver).analyze();
      for (const v of results.violations) {
        anyViolation = true;
        // Match `@axe-core/cli`'s wording so the Python regex stays unchanged.
        console.log(`${url}\n  Violation of "${v.id}" with ${v.nodes.length} node(s)`);
      }
    }
  } catch (e) {
    console.error('axe_scan: run error: ' + (e && e.message));
    await driver.quit().catch(() => {});
    process.exit(1);
  }
  await driver.quit().catch(() => {});
  process.exit(anyViolation ? 2 : 0);
}

main();
