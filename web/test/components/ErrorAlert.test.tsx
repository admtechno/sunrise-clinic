// Session 10, Demonstration 1: the first component test. render() puts the
// component into jsdom; screen finds what a person would find.
import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import ErrorAlert from "../../src/ErrorAlert";
import { ApiError } from "../../src/api";

const apiError = (status: number, message: string) =>
  new ApiError({ status, code: "x", message });

describe("ErrorAlert", () => {
  test("a 401 asks the person to log in again", () => {
    render(<ErrorAlert error={apiError(401, "Token is invalid")} />);
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Your session has ended. Please log in again.",
    );
  });

  test("a 403 says that this login may not, with the API's words", () => {
    const only = "Only the patient can upload reports.";
    render(<ErrorAlert error={apiError(403, only)} />);
    expect(screen.getByRole("alert")).toHaveTextContent(
      `Your login may not do this. The API says: ${only}`,
    );
  });

  test("any other error shows its own message", () => {
    render(<ErrorAlert error={new Error("Failed to fetch")} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Failed to fetch");
  });
});
