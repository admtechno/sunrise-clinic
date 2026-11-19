// Session 11: records real answers of the API into test/msw/recorded/, so the
// fake network of the tests answers what the real API answers. Start the API,
// then run: node tools/record_answers.mjs   (public endpoints only, no login)
import { mkdirSync, writeFileSync } from "node:fs";

const API = process.env.API_URL ?? "http://127.0.0.1:8000/api/v1";
const OUT = new URL("../test/msw/recorded/", import.meta.url);
const ANSWERS = {
  "specialities.json": "/specialities/?page_size=20",
  "doctors_page1.json": "/doctors/?page=1&page_size=3",
  "doctors_page2.json": "/doctors/?page=2&page_size=3",
  "doctor_1.json": "/doctors/1/",
  "doctor_1_slots.json": "/doctors/1/slots/",
};

mkdirSync(OUT, { recursive: true });
for (const [file, path] of Object.entries(ANSWERS)) {
  const headers = { Accept: "application/json" };
  const response = await fetch(API + path, { headers });
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  const body = await response.json();
  writeFileSync(new URL(file, OUT), JSON.stringify(body, null, 2) + "\n");
  console.log(`${response.status} ${path} -> test/msw/recorded/${file}`);
}
