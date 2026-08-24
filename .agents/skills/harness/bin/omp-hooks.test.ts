import { describe, expect, test } from "bun:test";
import {
  detectHarnessAgent,
  extractEditPaths,
  yieldContractText,
} from "../../../../.omp/extensions/harness-hooks.ts";

describe("detectHarnessAgent", () => {
  test("finds the canonical machine-readable marker", () => {
    expect(detectHarnessAgent([
      "base system prompt",
      "HARNESS_AGENT_ID: harness-backend-dev\n\n# Harness: Backend Engineer",
      "project context",
    ])).toBe("harness-backend-dev");
  });

  test("returns undefined for the main session", () => {
    expect(detectHarnessAgent(["base", "project"])).toBeUndefined();
  });

  test("rejects conflicting markers", () => {
    expect(() => detectHarnessAgent([
      "HARNESS_AGENT_ID: harness-backend-dev",
      "HARNESS_AGENT_ID: harness-pm",
    ])).toThrow("conflicting Harness agent markers");
  });

  test("ignores unsafe agent names", () => {
    expect(detectHarnessAgent(["HARNESS_AGENT_ID: ../../etc/passwd"])).toBeUndefined();
  });
});

describe("extractEditPaths", () => {
  test("extracts one hash-anchored file", () => {
    expect(extractEditPaths(`*** Begin Patch\n[src/a.ts#A1B2]\nPUT 1.=1:\n+new\n*** End Patch\n`))
      .toEqual(["src/a.ts"]);
  });

  test("extracts and deduplicates multiple files", () => {
    expect(extractEditPaths(`*** Begin Patch\n[a.ts#A1B2]\nPUT 1.=1:\n+x\n[b.ts#C3D4]\nPUT 2.=2:\n+y\n[a.ts#A1B2]\nPUT 1.=1:\n+z\n*** End Patch\n`))
      .toEqual(["a.ts", "b.ts"]);
  });

  test("returns no paths for a non-patch input", () => {
    expect(extractEditPaths("not a patch")).toEqual([]);
  });
});

describe("yieldContractText", () => {
  test("unwraps text content", () => {
    expect(yieldContractText({ data: { content: "VERDICT: PASS" } })).toBe("VERDICT: PASS");
  });

  test("renders a structured digest for the validator", () => {
    const rendered = yieldContractText({
      data: {
        VERDICT: "PASS",
        DIGEST: {
          headline: "No changes.",
          files_touched: [],
          open_questions: [],
        },
        artifact: "none",
      },
    });
    expect(rendered).toContain("VERDICT: PASS");
    expect(rendered).toContain("DIGEST:");
    expect(rendered).toContain("  files_touched: []");
    expect(rendered).toContain("artifact: none");
  });

  test("uses the last assistant message for an omitted yield payload", () => {
    expect(yieldContractText({}, "VERDICT: PASS")).toBe("VERDICT: PASS");
  });
});
