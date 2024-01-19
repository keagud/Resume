"use strict";

const puppeteer = require('puppeteer');
const Handlebars = require('handlebars');
const fs = require('fs');
const path = require('path');
const process = require('process')

/** @param {string} inputFile
 * @param {string} styleFile
 * @returns {string}
 */
function populateTemplateStyles(inputFile, styleFile) {
  const styles = fs.readFileSync(styleFile, 'utf8');
  const templateHtml = fs.readFileSync(inputFile, "utf8");
  const template = Handlebars.compile(templateHtml);
  const html = template({ styles: styles });
  return html;
}
/** @param {string} inputFile
 * @param {string} inputStylesFile
 * @returns {string}
 */
function renderPdf(inputFile, inputStylesFile) {
  (async () => {
    const html = populateTemplateStyles(inputFile, inputStylesFile);

    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setContent(html);
    await page.pdf({ path: "./output/output.pdf", format: "A4" });
    await browser.close();
  })();

}

function main() {
  const pdfStyles = "./css/pdf.css";
  const webStyles = "./css/web.css";

  const baseFile = "./base.html"

  const desiredFormat = process.argv[2];
  console.log(desiredFormat);

  switch (desiredFormat?.toLowerCase()) {
    case "pdf":
      renderPdf(baseFile, pdfStyles);
      break;

    case "web":
      const webHtml = populateTemplateStyles(baseFile, webStyles);
      fs.writeFileSync("./output/output.html", webHtml);
      break;

    default:
      throw new Error(`Not a valid format ${desiredFormat}`);
  }
}

main();
