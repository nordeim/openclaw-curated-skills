const fs = require('node:fs');
const path = require('node:path');
const { renderPostTradeTemplate } = require('./renderReport.js');

async function generateTradeReport(data, outputPath) {
  const htmlContent = renderPostTradeTemplate(data);

  let puppeteer;
  try {
    puppeteer = require('puppeteer');
  } catch (_e) {
    const fallbackPath = outputPath.replace(/\.pdf$/i, '.html');
    fs.writeFileSync(fallbackPath, htmlContent, 'utf8');
    throw new Error(
      `puppeteer is not installed; wrote HTML report instead at ${fallbackPath}. Install optional dependency 'puppeteer' for PDF output.`
    );
  }

  const outDir = path.dirname(outputPath);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 1600 });
  await page.emulateMediaType('print');
  await page.setContent(htmlContent, { waitUntil: 'load' });

  await page.pdf({
    path: outputPath,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: false,
    margin: { top: '10px', bottom: '10px', left: '10px', right: '10px' }
  });

  await browser.close();
  return outputPath;
}

module.exports = { generateTradeReport };
