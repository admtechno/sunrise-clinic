// Session 08: unit tests of the rules of the address (src/doctors/searchParams.ts).
// Run from demos/web: node --test "test/unit/**/*.test.ts"
import { describe, test } from "node:test";
import assert from "node:assert/strict";
import { readSearch, writeSearch } from "../../src/doctors/searchParams.ts";

const read = (text: string) => readSearch(new URLSearchParams(text));

describe("readSearch", () => {
  test("an empty address gives the defaults", () => {
    assert.deepEqual(read(""), {
      page: 1,
      search: undefined, // zod keeps a key for every optional field
      speciality: undefined,
      ordering: "name",
    });
  });

  test("a page that is not a whole number of 1 or more becomes page 1", () => {
    for (const page of ["abc", "0", "-3", "2.5"])
      assert.equal(read(`page=${page}`).page, 1, `page=${page}`);
  });

  test("a sort the page does not offer becomes the sort by name", () => {
    assert.equal(read("ordering=salary").ordering, "name");
  });

  test("a speciality with capitals or signs is left out", () => {
    assert.equal(read("speciality=ASTRO!").speciality, undefined);
  });

  test("good values are kept", () => {
    assert.deepEqual(read("speciality=general-medicine&ordering=-fee&page=2"), {
      page: 2,
      search: undefined,
      speciality: "general-medicine",
      ordering: "-fee",
    });
  });
});

describe("writeSearch", () => {
  test("the defaults are left out, so the plain list stays at /", () => {
    assert.equal(writeSearch(read("")).toString(), "");
  });

  test("read, then write, gives the same address back", () => {
    const address = "speciality=paediatrics&search=arjun&ordering=-fee&page=3";
    assert.equal(writeSearch(read(address)).toString(), address);
  });
});
