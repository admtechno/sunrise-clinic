# How the Sunrise Clinic Desk is tested (Part B project)

One command runs every test: `npm run test:all` in the project folder (the API's virtual environment active, `E2E_PASSWORD` set). It stops at the first level that fails.

| Level | Command | Tools | What it checks | Where |
|---|---|---|---|---|
| Unit | `npm run test:unit` | node --test | Pure functions: the roles and menus, the search parameters of the doctors list | `web/test/unit` |
| Components | `npm run test:components` | Vitest, jsdom, Testing Library, MSW | Each screen with a fake API client (Session 10) and over a fake network with recorded answers (Session 11): errors, slow answers, retries, token refresh | `web/test/components`, `web/test/network` |
| API | `npm run test:api` | pytest, pytest-django, factory-boy, time-machine, jsonschema | Every endpoint, the roles matrix, the time rules, the OpenAPI contract, the query counts, the reset command; at least 99% of `api` covered | `api/api/tests` |
| Browser | `npm run test:e2e` | Playwright, Chromium | The flows that matter, through the real browser, front end, API and database `m9_e2e` | `web/e2e` |

## The flows, and the level that tests each one

| Flow | Unit | Components | API | Browser |
|---|:-:|:-:|:-:|:-:|
| Find a doctor (filter, search, pages) | yes | yes | yes | yes |
| Log in, stay logged in after a reload, log out | | yes | yes | yes |
| Book a slot (and the API's field errors) | | yes | yes | yes |
| Two patients, one slot | | | yes | yes |
| An access token that expires during a booking | | yes | yes | yes (`JWT_ACCESS_SECONDS=3`) |
| Cancel an appointment (optimistic) | | yes | yes | yes |
| What each role finds, and is refused | yes | | yes | yes |
| Reception adds a slot that a patient books | | | yes | yes |
| A doctor completes a visit | | | yes | yes |
| Upload a report | | | yes | |

## Rules for the browser tests
- One database of their own (`m9_e2e`), reset before every test by `python manage.py reset_test_data`, which refuses any other database.
- The password of the test logins comes from `E2E_PASSWORD` in the terminal; no file holds it. A trace records what a test typed, so `test-results/` and `playwright-report/` stay out of Git.
- Role locators and checks that wait (`await expect(...)`); no fixed waits, except the one that waits for a token to expire.
- A test is run twice (`--repeat-each 2`) before it is kept. A test that is flaky is fixed, not retried; `retries` is 2 in CI only, and a flaky result there is read.

## Known gaps
- Only Chromium. Firefox and WebKit are one line each in `projects` (Session 13, Try Changing).
- Uploads are tested on the API only.
- Any doctor can read any appointment through the API (found in the Session 09 mini challenge; the API is not changed yet).
