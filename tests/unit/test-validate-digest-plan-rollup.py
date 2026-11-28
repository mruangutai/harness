#!/usr/bin/env python3
"""Unit floor for BUG-2582 T-02: the plan-team reader carve-out in validate-digest's roll-up.

The plan team's readers return FAIL to carry findings, and pm's `apply` step resolves those
findings in the same run. DEC-123's worst-member roll-up forced the team VERDICT to FAIL anyway.
The carve-out ranks a plan-team reader's FAIL as PASS only when every finding attributed to it is
recorded `resolved` in the feature's plan.yaml, checked on disk. Every other team, mission or
unresolvable case keeps worst-wins.

    VALIDATE_DIGEST=<path to validate-digest.py>  optional: load another validator (red-first)
    ./test-validate-digest-plan-rollup.py         -> exit 0 all pass, 1 otherwise
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
sys.path.insert(0, str(ROOT / "tests"))

import harness_boundary  # noqa: E402
import panel_findings  # noqa: E402
from harness_config_support import write_config  # noqa: E402

vd = harness_boundary.load_repo_module(
    "validate_digest_plan_rollup", os.environ.get("VALIDATE_DIGEST") or str(BIN / "validate-digest.py"))

FEATURE = "BUG-99-fixture"
RUN = "2026-11-27-01-plan-product"
PRODUCT = "harness-product-lead"
WORST = "worst member verdict"
NOT_APPLIED = "plan-team reader carve-out not applied"
TASK = {"id": "T-01", "title": "fixture task", "change_type": "bugfix",
        "execution_mode": "main-session-direct", "execution_reason": "fixture", "files": ["x.py"],
        "verify": "true", "intent": "fixture"}
SCOPE_READER = "harness-code-reviewer"

failures = []


def report(name, ok, detail=""):
    if ok:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name}: {detail}")
        failures.append(name)


def finding(summary, reader=SCOPE_READER):
    return {"reader": reader, "kind": "substance", "scope": "none", "severity": "high",
            "summary": summary, "why": "fixture"}


def row(item, disposition="resolved", **override):
    out = {"id": panel_findings.finding_id(item["reader"], item["summary"]),
           "severity": item["severity"], "reader": item["reader"], "kind": item["kind"],
           "summary": item["summary"], "disposition": disposition}
    if disposition == "resolved":
        out["resolved_by"] = "T-01"
    out.update(override)
    return out


def members(**verdicts):
    """The plan team's six member entries; `verdicts` overrides a step's verdict."""
    steps = (("draft", "harness-pm"), ("scope", SCOPE_READER),
             ("should-not-exist", "fable-advisor"), ("design", "harness-ui-reviewer"),
             ("apply", "harness-pm"), ("goalcheck", "harness-pm"))
    base = {"scope": "FAIL"}
    base.update(verdicts)
    return [{"step": step, "persona": persona, "verdict": base.get(step, "PASS"),
             "headline": "fixture", "files_touched": []} for step, persona in steps]


def build(root, disk_findings=(), mission="plan", plan_text=None, with_plan=True,
          with_panel=True):
    """The fixture checkout; returns the feature directory."""
    (root / ".harness").mkdir(parents=True, exist_ok=True)
    (root / ".harness" / "team-config.yaml").write_text("agents: {}\n")
    write_config(root / ".harness" / "harness.json")
    feature = root / ".harness" / "harness" / "features" / FEATURE
    (feature / "runs" / RUN).mkdir(parents=True, exist_ok=True)
    (feature / "feature.json").write_text(json.dumps({
        "feature_id": FEATURE, "branch": "none", "pr": None, "review_sha": "none",
        "cycles_used": 0, "max_total_cycles": 10, "runs": [],
        "judgements": [{"at": "2026-11-27T00:00:00+00:00", "by": "operator", "kind": "mission",
                        "decision": mission, "reason": "fixture"}],
        "mission": mission}))
    if plan_text is not None:
        (feature / "plan.yaml").write_text(plan_text)
    elif with_plan:
        doc = {"schema": "plan/1", "feature": FEATURE, "status": "plan",
               "approval": {"status": "pending"}, "tasks": [TASK]}
        if with_panel:
            doc["panel"] = {"findings": list(disk_findings)}
        (feature / "plan.yaml").write_text(yaml.safe_dump(doc, sort_keys=False))
    return feature


def product_digest(feature, verdict="PASS", findings=(), team="plan", member_list=None):
    digest = {"headline": "plan ready", "team": team, "cycles_used": 0,
              "members": member_list if member_list is not None else members(),
              "must_fix": [], "files_touched": [], "expertise_update": [],
              "branch": "none", "escalations": [], "adequacy_notes": [], "sc_status": [],
              "needs_approval": True, "severity_max": "high", "matrix_ok": "none",
              "coverage_gaps": [], "findings": [dict(item) for item in findings],
              "readers": [{"reader": "scope", "status": "ran", "persona": SCOPE_READER,
                           "reason": "none"},
                          {"reader": "should-not-exist", "status": "ran",
                           "persona": "fable-advisor", "reason": "none"},
                          {"reader": "design", "status": "ran",
                           "persona": "harness-ui-reviewer", "reason": "none"},
                          {"reader": "goalcheck", "status": "ran", "persona": "harness-pm",
                           "reason": "none"}],
              "open_questions": []}
    digest["steps_run"] = len(digest["members"])
    return {"VERDICT": verdict, "DIGEST": digest,
            "artifact": str(feature / "runs" / RUN / "digest.md")}


def other_lead_digest(lead, feature, run):
    digest = {"headline": "fixture", "team": "build", "steps_run": 1, "cycles_used": 0,
              "members": [{"step": "build", "persona": "backend-dev", "verdict": "FAIL",
                           "headline": "fixture", "files_touched": []}],
              "must_fix": [], "branch": "none", "files_touched": [], "open_questions": [],
              "escalations": [], "expertise_update": [], "sc_status": [], "adequacy_notes": [],
              "needs_approval": "none", "severity_max": "none", "matrix_ok": "none",
              "coverage_gaps": [], "findings": [], "readers": []}
    if lead == "harness-eng-lead":
        digest["amendments"] = []
    return {"VERDICT": "PASS", "DIGEST": digest,
            "artifact": str(feature / "runs" / run / "digest.md")}


def errors_of(persona, obj, feature):
    return vd.validate(persona, obj, feature_dir=str(feature))


def joined(errors):
    return " | ".join(errors) if errors else "no errors"


def worst_error(errors, naming=None):
    return any(WORST in e.lower() and (naming is None or f"returned {naming}" in e)
               for e in errors)


def not_applied(errors, reason):
    return any(NOT_APPLIED in e.lower() and reason in e for e in errors)


def run_case(name, body):
    try:
        ok, detail = body()
    except Exception as exc:  # noqa: BLE001  a base-tree red must still print its line
        ok, detail = False, f"{type(exc).__name__}: {exc}"
    report(name, ok, detail)


def in_fixture(body):
    """Run `body(root)` in a fresh fixture directory."""
    def wrapped():
        with tempfile.TemporaryDirectory() as tmp:
            return body(Path(os.path.realpath(tmp)))
    return wrapped


F1 = finding("first fixture finding")
F2 = finding("second fixture finding")


def accepted(verdict="PASS", findings=(F1, F2), disk=None, **build_kw):
    """A case expecting no errors at all."""
    def body(root):
        feature = build(root, [row(f) for f in findings] if disk is None else disk, **build_kw)
        errors = errors_of(PRODUCT, product_digest(feature, verdict, findings), feature)
        return not errors, joined(errors)
    return in_fixture(body)


def denied(reason=None, naming=None, findings=(F1, F2), disk=None, member_list=None,
           team="plan", alternatives=(), **build_kw):
    """A case expecting the worst-member refusal and, with `reason`, the not-applied text."""
    def body(root):
        feature = build(root, [row(f) for f in findings] if disk is None else disk, **build_kw)
        errors = errors_of(PRODUCT, product_digest(feature, "PASS", findings, team, member_list),
                           feature)
        ok = worst_error(errors, naming)
        if reason is not None:
            ok = ok and any(not_applied(errors, text) for text in (reason, *alternatives))
        return ok, joined(errors)
    return in_fixture(body)


def relief_with_reader(reader):
    items = (finding("first fixture finding", reader), finding("second fixture finding", reader))
    return accepted(findings=items)


@in_fixture
def case_producer_witness(root):
    feature = build(root, with_panel=False)
    plan = feature / "plan.yaml"
    items = (finding("first fixture finding", "code-reviewer"),
             finding("second fixture finding", "code-reviewer"))
    fan_in = {"DIGEST": {
        "readers": [{"reader": "scope", "status": "ran", "persona": SCOPE_READER,
                     "reason": "fixture"},
                    {"reader": "should-not-exist", "status": "ran", "persona": "fable-advisor",
                     "reason": "fixture"},
                    {"reader": "design", "status": "ran", "persona": "harness-ui-reviewer",
                     "reason": "fixture"}],
        "findings": [{key: item[key] for key in ("reader", "severity", "kind", "summary")}
                     for item in items]}}
    panel_md = feature / "runs" / RUN / "panel-c1.md"
    panel_md.write_text("# Plan panel fan-in, fixture\n\n```yaml\n"
                        + yaml.safe_dump(fan_in, sort_keys=False) + "```\n")
    env = dict(os.environ, HARNESS_PROJECT_DIR=str(root))
    env.pop("HARNESS_AGENT_TYPE", None)

    def plan_merge(stdin_text, *argv):
        return subprocess.run([sys.executable, str(BIN / "plan-merge.py"), *argv],
                              input=stdin_text, cwd=root, env=env, capture_output=True,
                              text=True, timeout=60)

    recorded = plan_merge("", "record-panel", "--file", str(plan), "--digest", str(panel_md),
                          "--cycle", "1")
    if recorded.returncode != 0:
        return False, f"record-panel exit={recorded.returncode} {recorded.stderr.strip()}"
    panel = yaml.safe_load(plan.read_text())["panel"]
    for item in panel["findings"]:
        item["disposition"] = "resolved"
        item["resolved_by"] = "T-01"
    resolved = plan_merge(yaml.safe_dump(panel, sort_keys=False), "set-panel", "--file",
                          str(plan), "--value-file", "/dev/stdin")
    if resolved.returncode != 0:
        return False, f"set-panel exit={resolved.returncode} {resolved.stderr.strip()}"
    errors = errors_of(PRODUCT, product_digest(feature, "PASS", items), feature)
    return not errors, joined(errors)


def case_apply_prompt_resolves():
    team = yaml.safe_load((ROOT / ".claude/skills/harness/teams/plan.yaml").read_text())
    step = next(s for s in team["steps"] if s.get("id") == "apply")
    prompt = " ".join(str(step.get("prompt", "")).split())
    spots = [prompt.find(t) for t in ("plan-merge.py record-panel", "plan-merge.py set-panel",
                                      "plan-merge.py check")]
    missing = [t for t in ("disposition: resolved", "resolved_by", "scope: mission")
               if t not in prompt]
    ok = -1 not in spots and spots == sorted(spots) and not missing
    return ok, f"verb positions {spots}, missing {missing}"


def other_lead(lead, run):
    @in_fixture
    def body(root):
        feature = build(root, [row(F1), row(F2)])
        errors = errors_of(lead, other_lead_digest(lead, feature, run), feature)
        return worst_error(errors), joined(errors)
    return body


@in_fixture
def case_duplicate_step(root):
    feature = build(root, [row(F1), row(F2)])
    member_list = members()
    member_list.insert(2, {"step": "scope", "persona": "harness-security-reviewer",
                           "verdict": "ESCALATE", "headline": "fixture", "files_touched": []})
    errors = errors_of(PRODUCT, product_digest(feature, "PASS", (F1, F2), member_list=member_list),
                       feature)
    ok = worst_error(errors, "ESCALATE") and not_applied(errors, "duplicated reader step")
    return ok, joined(errors)


def main():
    run_case("bug2582-control-fail-verdict-valid", accepted(verdict="FAIL"))
    run_case("bug2582-relief-resolved", accepted())
    run_case("bug2582-relief-reader-code-reviewer", relief_with_reader("code-reviewer"))
    run_case("bug2582-relief-reader-slot", relief_with_reader("scope"))
    run_case("bug2582-producer-witness", case_producer_witness)
    run_case("bug2582-apply-prompt-resolves", case_apply_prompt_resolves)

    run_case("bug2582-deny-open-on-disk",
             denied("is not resolved", disk=[row(F1), row(F2, "open")]))
    run_case("bug2582-deny-historical-open",
             denied("is not resolved",
                    disk=[row(F1), row(F2), row(finding("an earlier fixture finding"), "open")]))
    run_case("bug2582-deny-absent-from-plan",
             denied("absent from plan.yaml panel.findings", disk=[row(F1)]))
    run_case("bug2582-deny-mismatched-row",
             denied("has no matching plan.yaml panel row",
                    disk=[row(F1), row(F2, reader="fable-advisor")]))
    run_case("bug2582-deny-folded-disposition",
             denied("panel.findings malformed", alternatives=("plan.yaml missing or unloadable",),
                    disk=[row(F1), row(F2, disposition="Resolved")]))
    malformed = row(F2)
    del malformed["summary"]
    run_case("bug2582-deny-malformed-row",
             denied("panel.findings malformed", alternatives=("plan.yaml missing or unloadable",),
                    disk=[row(F1), malformed]))
    run_case("bug2582-deny-no-findings",
             denied("no findings attributed to scope", findings=(), disk=[]))
    run_case("bug2582-deny-unattributable",
             denied("matches no member or more than one",
                    findings=(F1, F2, finding("a stray fixture finding", "someone-else"))))
    run_case("bug2582-deny-ambiguous",
             denied("matches no member or more than one",
                    disk=[row(F1), row(F2), row(finding("a pm fixture finding", "harness-pm"))]))
    run_case("bug2582-deny-duplicate-step", case_duplicate_step)
    run_case("bug2582-deny-no-plan", denied("plan.yaml missing or unloadable", with_plan=False))
    run_case("bug2582-deny-unloadable-plan",
             denied("plan.yaml missing or unloadable",
                    plan_text=f"schema: plan/1\nfeature: {FEATURE}\nstatus: plan\ntasks: []\n"))
    run_case("bug2582-deny-mission-patch", denied("mission is not plan", mission="patch"))
    run_case("bug2582-deny-team-build", denied(team="build"))
    for step in ("draft", "apply", "goalcheck"):
        run_case(f"bug2582-deny-nonreader-{step}",
                 denied(member_list=members(scope="PASS", **{step: "FAIL"})))
    for verdict in ("ESCALATE", "BLOCKED"):
        run_case(f"bug2582-deny-{verdict.lower()}",
                 denied(naming=verdict, member_list=members(scope=verdict)))
    run_case("bug2582-other-lead-eng",
             other_lead("harness-eng-lead", "2026-11-27-02-build-engineering"))
    run_case("bug2582-other-lead-validator",
             other_lead("harness-validator-lead", "2026-11-27-02-validate-validator"))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
