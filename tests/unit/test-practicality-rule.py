#!/usr/bin/env python3
"""Unit floor for FEAT-2622 T-01: the practicality rule in the digest schema and validate-digest.

Every reader finding carries `exposure` {trigger, vs_today, control} or, in a lead digest only,
the string `unrated`. A finding that is contrived, no worse than today and not adversary-
controlled is discounted: it is at most med, never in must_fix, never the support of a gating
severity_max, never the sole reason a review FAILs, and an open panel row it backs does not deny
a plan reader the DEC-123 carve-out.

Imports nothing that is absent at the feature's base, so the red-first run there reaches every
check and prints its FAIL line.

    ./test-practicality-rule.py   -> exit 0 all pass, 1 otherwise
"""
import copy
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
sys.path.insert(0, str(ROOT / "tests"))

import digest_schema  # noqa: E402
import harness_boundary  # noqa: E402
import panel_findings  # noqa: E402
from check_support import Checks  # noqa: E402

vd = harness_boundary.load_repo_module("validate_digest_practicality",
                                       str(BIN / "validate-digest.py"))
rollup = harness_boundary.load_repo_module(
    "plan_rollup_fixtures", str(ROOT / "tests" / "unit" / "test-validate-digest-plan-rollup.py"))

C = Checks()
RULE = "practicality rule"
PLAUSIBLE = {"trigger": "plausible", "vs_today": "regression", "control": "chance"}
DISCOUNTED = {"trigger": "contrived", "vs_today": "no_worse", "control": "user"}

UNIVERSAL = {"headline": "fixture", "open_questions": [], "files_touched": [],
             "expertise_update": []}
REVIEW = {"severity_max": "high", "must_fix": [], "findings": []}
LEAD = {"team": "build", "steps_run": 1, "cycles_used": 0, "must_fix": [], "branch": "none",
        "escalations": [], "adequacy_notes": [],
        "members": [{"step": "s1", "persona": "harness-qa", "verdict": "PASS",
                     "headline": "green", "files_touched": []}],
        "sc_status": [], "needs_approval": "none", "severity_max": "low", "matrix_ok": "none",
        "coverage_gaps": [], "findings": [], "readers": []}
FIELDS = {
    "harness-code-reviewer": {**REVIEW, "code_grade": "n_a", "reviewed": "none",
                              "grade_2_reasons": [], "spec_violations": [],
                              "human_commits_in_scope": []},
    "harness-security-reviewer": {**REVIEW, "in_scope": True, "scope_reason": "none",
                                  "threat_model": []},
    "harness-ui-reviewer": {**REVIEW, "mode": "B", "in_scope": True, "states_unspecified": [],
                            "contract_violations": [], "a11y": []},
    "harness-eng-lead": {**LEAD, "amendments": []},
    "harness-product-lead": {**LEAD, "needs_approval": True},
    "harness-validator-lead": {**LEAD, "matrix_ok": True},
}


def finding(summary, exposure=PLAUSIBLE, severity="high", reader="code-reviewer"):
    item = {"kind": "substance", "scope": "none", "severity": severity, "reader": reader,
            "summary": summary, "why": "fixture"}
    if exposure is not None:
        item["exposure"] = copy.deepcopy(exposure)
    return item


def digest(persona, findings, verdict="FAIL", **overrides):
    body = {**copy.deepcopy(UNIVERSAL), **copy.deepcopy(FIELDS[persona]),
            "findings": list(findings), **overrides}
    return {"VERDICT": verdict, "DIGEST": body, "artifact": "notes/run/digest.md"}


def errors_of(persona, obj):
    try:
        return vd.validate(persona, obj)
    except Exception as exc:  # noqa: BLE001  a base-tree red must still print its line
        return [f"{type(exc).__name__}: {exc}"]


def refused(errors):
    return any(RULE in e for e in errors)


def accepted(errors):
    return not any(RULE in e or "exposure" in e for e in errors)


def show(errors):
    return " | ".join(errors) if errors else "no errors"


# --- Schema: exposure is required, and closed.
def schema_refused(name, exposure, drop=False):
    item = finding("a stale cache entry")
    if drop:
        item.pop("exposure")
    else:
        item["exposure"] = exposure
    errors = digest_schema.validate_object("harness-code-reviewer",
                                           digest("harness-code-reviewer", [item]))
    C.check(name, any("exposure" in e for e in errors)
            and not any("'exposure' was unexpected" in e for e in errors), show(errors))


schema_refused("practicality-missing-exposure-refused", None, drop=True)
schema_refused("practicality-offenum-exposure-refused",
               {"trigger": "rare", "vs_today": "no_worse", "control": "user"})
schema_refused("practicality-extra-key-refused", {**PLAUSIBLE, "likelihood": "low"})
schema_refused("practicality-missing-inner-key-refused",
               {"trigger": "plausible", "vs_today": "regression"})
schema_refused("practicality-invalid-string-refused", "rare")
wellformed = digest_schema.validate_object(
    "harness-code-reviewer", digest("harness-code-reviewer", [finding("a stale cache entry")]))
C.check("practicality-wellformed-accepted", accepted(wellformed), show(wellformed))


# --- A discounted finding is at most med.
def severity_case(name, exposure, severity, want_refused, persona="harness-code-reviewer"):
    """A gating severity is a FAIL review; a non-gating one is a PASS."""
    gating = severity not in ("info", "low", "med")
    item = finding("a stale cache entry", exposure, severity)
    errors = errors_of(persona, digest(persona, [item], verdict="FAIL" if gating else "PASS",
                                       severity_max="high" if gating else severity))
    C.check(name, refused(errors) if want_refused else accepted(errors), show(errors))


severity_case("practicality-discounted-high-refused", DISCOUNTED, "high", True)
severity_case("practicality-discounted-unrated-severity-refused", DISCOUNTED, "unrated", True)
severity_case("practicality-discounted-med-accepted", DISCOUNTED, "med", False)
severity_case("practicality-adversary-high-accepted", {**DISCOUNTED, "control": "adversary"},
              "high", False)
severity_case("practicality-regression-high-accepted", {**DISCOUNTED, "vs_today": "regression"},
              "high", False)
severity_case("practicality-plausible-high-accepted", {**DISCOUNTED, "trigger": "plausible"},
              "high", False)
severity_case("practicality-unrated-exposure-high-accepted", "unrated", "high", False,
              persona="harness-validator-lead")


# --- A discounted finding never enters must_fix.
def must_fix_case(name, must_fix, want_refused):
    stale = finding("a stale cache entry", DISCOUNTED, "med")
    real = finding("the token is logged in clear", PLAUSIBLE, "med")
    errors = errors_of("harness-code-reviewer",
                       digest("harness-code-reviewer", [real, stale], must_fix=must_fix,
                              severity_max="med"))
    C.check(name, refused(errors) if want_refused else accepted(errors), show(errors))


STALE_ID = panel_findings.finding_id("code-reviewer", "a stale cache entry")
must_fix_case("practicality-mustfix-summary-refused", ["Fix: A stale  cache entry"], True)
must_fix_case("practicality-mustfix-pfid-refused", [f"see {STALE_ID[:11]}"], True)
must_fix_case("practicality-mustfix-other-finding-accepted",
              ["fix: the token is logged in clear"], False)


# --- unrated is a lead's transcription, never a harness reviewer's own value.
for persona in ("harness-code-reviewer", "harness-security-reviewer", "harness-ui-reviewer",
                "harness-eng-lead", "harness-product-lead", "harness-validator-lead"):
    short = persona.removeprefix("harness-")
    lead = persona in ("harness-product-lead", "harness-validator-lead")
    errors = errors_of(persona, digest(persona, [finding("a stale cache entry", "unrated", "low")],
                                       verdict="PASS", severity_max="low"))
    if lead:
        C.check(f"practicality-unrated-accepted-{short}", accepted(errors), show(errors))
    else:
        C.check(f"practicality-unrated-refused-{short}", refused(errors), show(errors))


# --- A discounted finding never decides severity_max or a reviewer's FAIL.
def verdict_case(name, want_refused, verdict="FAIL", severity_max="med", extra=(), must_fix=()):
    items = [*extra, finding("a stale cache entry", DISCOUNTED, "med")]
    errors = errors_of("harness-code-reviewer",
                       digest("harness-code-reviewer", items, verdict=verdict,
                              severity_max=severity_max, must_fix=list(must_fix)))
    C.check(name, refused(errors) if want_refused else accepted(errors), show(errors))


verdict_case("practicality-severity-max-discounted-only-refused", True, severity_max="high")
verdict_case("practicality-severity-max-witnessed-accepted", False, severity_max="high",
             extra=[finding("the token is logged in clear", PLAUSIBLE, "high")])
verdict_case("practicality-fail-discounted-only-refused", True)
verdict_case("practicality-fail-with-mustfix-accepted", False,
             extra=[finding("the token is logged in clear", PLAUSIBLE, "med")],
             must_fix=["fix: the token is logged in clear"])
verdict_case("practicality-discounted-only-pass-accepted", False, verdict="PASS")


# --- DEC-123 as amended: an open row discounted at med does not deny the carve-out.
def carveout_case(name, exposure, want_relief):
    item = finding("a speculative refactor", exposure, "med", reader="fable-advisor")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(os.path.realpath(tmp))
        feature = rollup.build(root, [rollup.row(item, "open", exposure=copy.deepcopy(exposure))])
        obj = rollup.product_digest(feature, "PASS", [item], member_list=rollup.members(
            scope="PASS", **{"should-not-exist": "FAIL"}))
        obj["DIGEST"]["severity_max"] = "med"
        errors = vd.validate(rollup.PRODUCT, obj, feature_dir=str(feature))
    worst = rollup.worst_error(errors)
    C.check(name, not worst if want_relief else worst, show(errors))


def run_carveout(name, exposure, want_relief):
    try:
        carveout_case(name, exposure, want_relief)
    except Exception as exc:  # noqa: BLE001  a base-tree red must still print its line
        C.check(name, False, f"{type(exc).__name__}: {exc}")


run_carveout("practicality-carveout-discounted-open-relieved", DISCOUNTED, True)
run_carveout("practicality-carveout-plausible-open-denied", {**DISCOUNTED, "trigger": "plausible"},
             False)

sys.exit(C.report())
