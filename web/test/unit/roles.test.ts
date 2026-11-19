// Session 08: unit tests of what each role is shown (src/auth/roles.ts).
// The API has the same rule (ReportRules); this level checks only the screen.
import { test } from "node:test";
import assert from "node:assert/strict";
import { canReadReports, canUploadReports } from "../../src/auth/roles.ts";

test("only a patient is offered the upload of a report", () => {
  assert.equal(canUploadReports("patient"), true);
  assert.equal(canUploadReports("doctor"), false);
  assert.equal(canUploadReports("admin"), false); // reception
  assert.equal(canUploadReports(null), false); // not logged in
});

test("the patient and the doctor may read the reports", () => {
  assert.equal(canReadReports("patient"), true);
  assert.equal(canReadReports("doctor"), true);
  assert.equal(canReadReports("admin"), false);
});
