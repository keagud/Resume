import puppeteer from "puppeteer";
import Handlebars from "handlebars";
import fs from "fs";
import path from "path";
import process from "process";
import { generateCustomSkillsComponent } from "./ai";
import { parseBuildArgs, Arguments } from "./cli";
import { promisify } from "util";

const readFileAsync = promisify(fs.readFile);

const getPath = (p: string) => path.join(__dirname, "..", p);

const stylesFile = getPath("assets/styles.css");
const baseFile = getPath("assets/base.html");

async function populateTemplate(jobDescriptionFile?: string) {
  const styles = await readFileAsync(stylesFile, "utf8");
  const templateHtml = await readFileAsync(baseFile, "utf8");

  const templateParams = {
    styles: styles,
    customSkills:
      jobDescriptionFile == undefined
        ? undefined
        : await readFileAsync(jobDescriptionFile, "utf8").then((d) =>
          generateCustomSkillsComponent(d),
        ),
  };

  const template = Handlebars.compile(templateHtml);
  const html = template(templateParams);
  return html;
}

const renderWeb = async (jobDescriptionFile?: string, saveFile: boolean = true) => {
  const webHtml = await populateTemplate(jobDescriptionFile);
  if (saveFile) {
    fs.writeFileSync(getPath("output/resume.html"), webHtml);
  }
  return webHtml;
};

async function renderPdf(html: string) {
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
}

async function main() {
  const { jobDescriptionFile, buildFormat } = await parseBuildArgs();

  fs.mkdirSync(getPath("output"), { recursive: true });

  const html = await renderWeb(jobDescriptionFile, buildFormat == 'web' || buildFormat == 'all');

  if (buildFormat != "web") {
    await renderPdf(html);
  }
}

(async () => await main())();
