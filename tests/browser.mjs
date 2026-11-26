import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { copyFile, mkdtemp, readFile, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { promisify } from "node:util";

const browserPath = process.argv[2];
assert.ok(browserPath, "Indiquez le chemin d’un navigateur Chromium.");
const root = new URL("../", import.meta.url);
const directory = await mkdtemp(join(tmpdir(), "unfollowspy-"));
const source = await readFile(new URL("index.html", root), "utf8");
await writeFile(join(directory, "index.html"), source.replace("</head>", '<script defer src="browser-check.js"></script></head>'));
await Promise.all(["app.js", "styles.css", "tests/browser-check.js"].map((file) =>
  copyFile(fileURLToPath(new URL(file, root)), join(directory, file.split("/").at(-1)))
));

const { stdout } = await promisify(execFile)(browserPath, [
  "--headless=new", "--no-first-run", "--no-default-browser-check", "--disable-background-networking",
  "--disable-gpu", "--no-sandbox", "--virtual-time-budget=8000", "--dump-dom",
  "--user-data-dir=" + join(directory, "profile"), pathToFileURL(join(directory, "index.html")).href,
], { timeout: 30000, maxBuffer: 4 * 1024 * 1024 });
const report = stdout.match(/data-browser-report="([^"]+)"/)?.[1];
assert.ok(report, "Le parcours web n’a pas produit de résultat.");
const result = JSON.parse(decodeURIComponent(report));
assert.ok(result.passed, result.message);
console.log("Parcours web vérifié dans Chromium.");




