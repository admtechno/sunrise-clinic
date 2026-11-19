# Release checklist (Sunrise Clinic Desk)

Before the release
- [ ] main is green: both checks of the CI workflow passed on the commit to release.
- [ ] CHANGELOG.md has a section for the new version, written for the clinic's staff.
- [ ] Migrations: none removes or renames a column the running version still reads (Session 17, Demonstration 5).
- [ ] New settings are set on Render and Vercel before the deploy, not only in .env or test.py.
- [ ] The way back is known: the version before, and how to start it again.

The release
- [ ] `git tag -a vX.Y.Z -m "..."` on the green commit, then `git push origin vX.Y.Z`.
- [ ] Watch the deploy on Render until it is live; Vercel's production deploy for the same commit.

After the release (within 15 minutes)
- [ ] `python scripts/smoke_test.py <api> --origin <web> --expect-version <commit>` passes.
- [ ] `python scripts/web_smoke_test.py <web>` passes.
- [ ] The log has no ERROR line since the deploy (`scripts/log_summary.py`).
- [ ] The uptime monitor shows UP.
- [ ] If any of these fails: roll back first, find the cause afterwards.
