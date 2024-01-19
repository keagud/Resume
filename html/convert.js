const puppeteer = require("puppeteer");

const fs = require("fs");
const path = require("path");

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Get the content of the file
  const contentHtml = fs.readFileSync("./output_pdf.html", "utf8");

  await page.setContent(contentHtml);
  await page.pdf({ path: "output.pdf", format: "A4" });

  await browser.close();
})();
