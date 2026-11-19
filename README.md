# Sunrise Clinic Desk (Part B project)

The Part A project (Clinic Desk and Sunrise Clinic API) with the tests of Sessions 08 to 13. See `TESTING.md` for what is tested where.

## Every test, with one command
Once: the first-run steps of Lab 12 (database `m9_e2e`, its tables, `npm install` in `web`, `npx playwright install chromium`). Then, in a terminal in this folder:
1. Activate the API's virtual environment: PowerShell `api\.venv\Scripts\Activate.ps1`, macOS and Linux `source api/.venv/bin/activate`.
2. Set a made-up test password for this terminal only: PowerShell `$env:E2E_PASSWORD = [System.Net.NetworkCredential]::new("", (Read-Host "Test password" -AsSecureString)).Password`, macOS and Linux `read -s E2E_PASSWORD && export E2E_PASSWORD`.
3. Stop your own API and Vite, then run `npm run test:all`.

The expiry test runs only with a short token life: PowerShell `$env:JWT_ACCESS_SECONDS="3"; npm run test:e2e; Remove-Item Env:JWT_ACCESS_SECONDS`, macOS and Linux `JWT_ACCESS_SECONDS=3 npm run test:e2e`.

## Done when
- `npm run test:all` passes: unit, components, API (coverage 99% or more) and browser.
- With `JWT_ACCESS_SECONDS=3`, the expiry test passes too.
- `TESTING.md` says which level tests each flow, and lists the gaps.
