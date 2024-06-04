import puppeteer from "puppeteer";
import Handlebars from "handlebars";
import fs from "fs";
import path from "path";
import process from "process";

const getPath = (p: string) => path.join(__dirname, "..", p);

const stylesFile = getPath("assets/styles.css");
const baseFile = getPath("assets/base.html");

function populateTemplateStyles(inputFile: string, styleFile: string) {
  const styles = fs.readFileSync(styleFile, "utf8");
  const templateHtml = fs.readFileSync(inputFile, "utf8");
  const template = Handlebars.compile(templateHtml);
  const html = template({ styles: styles });
  return html;
}

const renderWeb = () => {
  const webHtml = populateTemplateStyles(baseFile, stylesFile);
  fs.writeFileSync(getPath("output/resume.html"), webHtml);
  return webHtml;
};

function renderPdf(inputFile: string, inputStylesFile: string): void {
  (async () => {
    const html = renderWeb();

    const browser = await puppeteer.launch({
      headless: true,
      // YES this is a huge security hole
      // but we're not actually connecting Chromium to the internet at all, just using the renderer, so it's fine
      args: ["--no-sandbox"],
    });
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: "networkidle0" });
    await page.pdf({
      path: getPath("output/resume.pdf"),
      format: "A4",
      preferCSSPageSize: true,
    });
    await browser.close();
  })();
}

function main() {
  fs.mkdirSync(getPath("output"), { recursive: true });

  const desiredFormat = process.argv[2] ?? "all";
  console.log(desiredFormat);

  switch (desiredFormat?.toLowerCase()) {
    case "pdf":
      renderPdf(baseFile, stylesFile);
      break;

    case "web":
      renderWeb();
      break;

    case "all":
      renderPdf(baseFile, stylesFile);
      break;

    default:
      throw new Error(`Not a valid format ${desiredFormat}`);
  }
}

main();
