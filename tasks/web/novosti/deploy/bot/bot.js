import { createClient } from "redis";
import puppeteer from "puppeteer";
import fs from "fs";
import crypto from "crypto";

const REDIS_URL = process.env["REDIS_URL"];
const TASK_URL = process.env["TASK_URL"];

let ADMIN_TOKEN;

try {
  ADMIN_TOKEN = fs.readFileSync(process.env["ADMIN_TOKEN_FILE"], "utf8").trim();
} catch (e) {
  console.log(`Error reading ADMIN_TOKEN_FILE, will recreate it: ${e}`);
  ADMIN_TOKEN = crypto.randomBytes(32).toString("hex");
  console.log(`Generated admin token: ${ADMIN_TOKEN}`);
  fs.writeFileSync(process.env["ADMIN_TOKEN_FILE"], ADMIN_TOKEN);
  console.log(`Wrote ADMIN_TOKEN_FILE, will restart bot`);
  process.exit(0);
}

let browser = null;

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function visit(storyID) {
  console.log(`Visiting news story ${storyID}`);

  let context = null;
  try {
    if (!browser) {
      const args = [
        "--js-flags=--jitless,--no-expose-wasm",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--block-new-web-contents",
      ];

      browser = await puppeteer.launch({
        headless: "new",
        args,
      });
    }

    context = await browser.createIncognitoBrowserContext();

    const page = await context.newPage();
    await page.setCookie({
      name: "NOVOSTI_ADMIN_TOKEN",
      value: ADMIN_TOKEN,
      url: TASK_URL,
    });
    await page.goto(`${TASK_URL}/news/${storyID}`);
    await sleep(5000);
    await page.close();
  } catch (e) {
    console.log(`Unexpected error: ${e}`);
  } finally {
    if (context) await context.close();
  }
}

async function main() {
  const client = await createClient({
    url: REDIS_URL,
  })
    .on("error", (err) => console.log(`Failed to connect to redis: ${err}`))
    .connect();

  console.log("Connected to redis, waiting on news channel");

  await client.subscribe("news", visit);
}

process.on("SIGTERM", process.exit);
process.on("SIGINT", process.exit);

main();
