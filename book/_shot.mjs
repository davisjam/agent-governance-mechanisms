import { pathToFileURL } from "node:url";
import puppeteer from "puppeteer";

const [indexHtml, outPng, wStr, hStr] = process.argv.slice(2);
const width = parseInt(wStr, 10);
const height = parseInt(hStr, 10) || 1440;

const browser = await puppeteer.launch({
  headless: "new",
  args: ["--no-sandbox", "--disable-setuid-sandbox"],
});
try {
  const page = await browser.newPage();
  page.on("pageerror", (e) => console.error("PAGE ERROR:", e.message));
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(indexHtml).href, { waitUntil: "networkidle0", timeout: 60000 });
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.screenshot({ path: outPng, fullPage: true });
  console.log("wrote", outPng);
} finally {
  await browser.close();
}
