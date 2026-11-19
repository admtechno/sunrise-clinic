// Session 14: checks the BUILT web app before it goes to a host.
//   node scripts/predeploy_check.mjs [web folder]      (run `npm run build` first)
// It only reads the files in dist: nothing is started, nothing is sent.
// Exit code 0 when every check passes, 1 when one fails.
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { gzipSync } from "node:zlib";

const dist = path.join(path.resolve(process.argv[2] ?? "web"), "dist");
const assets = path.join(dist, "assets");
const results = [];
const check = (name, ok, detail = "") => results.push({ name, ok, detail });
const kB = (bytes) => `${(bytes / 1024).toFixed(1)} kB`;

check("dist/index.html exists", existsSync(path.join(dist, "index.html")));
const names = existsSync(assets) ? readdirSync(assets) : [];
const files = names
  .filter((name) => name.endsWith(".js"))
  .map((name) => ({ name, text: readFileSync(path.join(assets, name), "utf8") }));
check("dist/assets holds JavaScript files", files.length > 0, `${files.length} files`);

// 1. Every visitor downloads these files: nothing of your own PC, and no secret
const forbidden = [
  [/(127\.0\.0\.1|localhost):\d+/, "address of your own PC",
    "set VITE_API_BASE_URL in .env.production"],
  [/DJANGO_SECRET_KEY|DB_PASSWORD|E2E_PASSWORD/, "name of a server secret"],
  [/postgres(ql)?:\/\/[^\s"'`]*@/, "database address with a login in it"],
  [/-----BEGIN [A-Z ]*PRIVATE KEY-----/, "private key"],
  [/eyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]{10,}/, "token"],
];
for (const [pattern, what, hint] of forbidden) {
  const hits = files.filter((f) => pattern.test(f.text)).map((f) => f.name);
  check(`no ${what}`, hits.length === 0,
    hits.length ? `in ${hits.join(", ")}${hint ? `: ${hint}` : ""}` : "");
}

// 2. The page asks for the API on its own server, at the path of the plan
check("the API is called at /api/v1", files.some((f) => /[`"']\/api\/v1[`"']/.test(f.text)));

// 3. Size, as a visitor downloads it (gzip). The budgets are this project's
const FILE_BUDGET = 150 * 1024;
const TOTAL_BUDGET = 250 * 1024;
const sizes = files.map((f) => ({ name: f.name, gz: gzipSync(f.text).length }));
const biggest = sizes.reduce((a, b) => (b.gz > a.gz ? b : a), { name: "-", gz: 0 });
check(`each file at most ${kB(FILE_BUDGET)} gzipped`, biggest.gz <= FILE_BUDGET,
  `largest ${kB(biggest.gz)}`);
const total = sizes.reduce((sum, s) => sum + s.gz, 0);
check(`all JavaScript at most ${kB(TOTAL_BUDGET)} gzipped`, total <= TOTAL_BUDGET, kB(total));

// 4. Source maps would publish your source code: not by accident
const maps = names.filter((name) => name.endsWith(".map"));
check("no source maps", maps.length === 0, maps.join(", "));

for (const r of results) {
  console.log(`${r.ok ? "PASS" : "FAIL"}  ${r.name}${r.detail ? `  (${r.detail})` : ""}`);
}
const failed = results.filter((r) => !r.ok).length;
console.log(`\n${results.length - failed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
