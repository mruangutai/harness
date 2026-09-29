#!/usr/bin/env python3
"""FEAT-1928 T-02 baseline half: run the CURRENT validate-digest.py exactly as each owning
test does, record every digest-validation case with its accept/reject result, and emit the
equivalent object mapping as a JSON fixture.

    parity-baseline.py            write parity-fixtures/*.json + baseline.json + table rows
    parity-baseline.py --check    re-run and diff against baseline.json (exit 1 on drift)

Throwaway receipt harness: it loads the owning test modules and wraps subprocess.run /
the shadow `_errors` seam to observe each validator call; it edits nothing under test.
"""
import hashlib, importlib.util, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
BIN = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
VALIDATE = os.path.join(BIN, "validate-digest.py")
FIX = os.path.join(HERE, "parity-fixtures")
BASELINE = os.path.join(HERE, "baseline.json")
sys.path.insert(0, BIN)
import yaml  # noqa: E402

_REAL_RUN = subprocess.run
RECORD = []   # (argv_tail, stdin, returncode, stdout, stderr)


def _is_baseline_validator(argv):
    return any(os.path.abspath(str(a)) == VALIDATE for a in argv[:2])


def _recording_run(argv, *a, **kw):
    r = _REAL_RUN(argv, *a, **kw)
    if isinstance(argv, (list, tuple)) and _is_baseline_validator(argv):
        RECORD.append((list(argv), kw.get("input"), r.returncode, r.stdout, r.stderr))
    return r


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ object mapping ----
def _tail(text):
    anchors = list(re.finditer(r"^\s*VERDICT:", text, re.M))
    return text[anchors[-1].start():] if anchors else text


def to_object(text):
    """(mapping|None, why). Same tail anchor the validator/INV-15 use; yaml.safe_load."""
    if text is None:
        return None, "no digest text in payload"
    try:
        doc = yaml.safe_load(_tail(text))
    except yaml.YAMLError as e:
        return None, f"yaml: {str(e).splitlines()[0]}"
    if not isinstance(doc, dict):
        return None, f"not a mapping ({type(doc).__name__})"
    return doc, ""


# Hand-classified where the reason text does not name the shape: a missing agent_type with a
# bare-string message is a string (not mapping) return under the object contract.
COUNTERPART_OVERRIDE = {"F6 missing agent_type key is loud, not silent": "wrong-type"}


def counterpart(reasons, case=""):
    """Object-level rejection a syntax-only reject maps to."""
    if case in COUNTERPART_OVERRIDE:
        return COUNTERPART_OVERRIDE[case]
    low = reasons.lower()
    if re.search(r"missing|absent|required|empty|no digest|null|nonetype", low):
        return "missing"
    if re.search(r"unknown|unexpected key|not allowed|extra|stray|duplicate", low):
        return "extra"
    if re.search(r"one of|must be (pass|fail|blocked)|enum|not a valid|invalid verdict", low):
        return "enum-invalid"
    return "wrong-type"

# ------------------------------------------------------------------ collectors --------
def collect_validate_digest(rows):
    t = _load("_parity_tvd", os.path.join(ROOT, "tests/integration/test-validate-digest.py"))
    checks = [n for n in ("run_canonical_reader_strictness_cases", "run_feat65_guard_cases",
              "run_cli_cases", "run_empty_red_case", "run_dec156_worktree_red_case",
              "run_bug919_qa_matrix_cases", "run_bug919_resolve_fallback_case",
              "run_bug919_resolve_by_artifact_case", "run_joint_hint_case",
              "run_code_grade_cases", "run_hook_cases", "run_bug1305_artifact_resolution_cases",
              "run_t09", "run_t51_suspension_cases", "run_bug1898_exact_release_cases",
              "run_template_cases", "run_reviewer_severity_enum_cases",
              "run_documented_contract_cases", "run_t01_schema_cases",
              "run_t04_unknown_key_cases", "run_t08_revision_proof")]
    subprocess.run = _recording_run
    devnull = open(os.devnull, "w")
    try:
        for name in checks:
            start = len(RECORD)
            real_stdout, sys.stdout = sys.stdout, devnull
            try:
                getattr(t, name)()
            finally:
                sys.stdout = real_stdout
            calls = RECORD[start:]
            if name == "run_cli_cases":
                assert len(calls) == len(t.CASES), (len(calls), len(t.CASES))
                labels = [(c[0], c[1], "cli") for c in t.CASES]
                source = "cli"
            elif name == "run_hook_cases":
                assert len(calls) == len(t.HOOK_CASES), (len(calls), len(t.HOOK_CASES))
                labels = [(c[0], c[1].get("agent_type"), "hook") for c in t.HOOK_CASES]
                source = "hook"
            else:
                labels = None
                source = "hook-group" if name in ("run_t09", "run_t51_suspension_cases",
                                                  "run_bug1898_exact_release_cases",
                                                  "run_bug1305_artifact_resolution_cases",
                                                  "run_bug919_qa_matrix_cases",
                                                  "run_bug919_resolve_fallback_case",
                                                  "run_bug919_resolve_by_artifact_case",
                                                  "run_dec156_worktree_red_case",
                                                  "run_empty_red_case") else "cli-group"
            for i, (argv, stdin, code, out, err) in enumerate(calls):
                if "--hook" in argv:
                    try:
                        payload = json.loads(stdin or "")
                    except ValueError:
                        payload = None
                    persona = (payload or {}).get("agent_type") if isinstance(payload, dict) else None
                    text = (payload or {}).get("last_assistant_message") if isinstance(payload, dict) else None
                    mode, reasons = "hook", err
                else:
                    persona, text, mode, reasons = argv[-1], stdin, "cli", out
                if labels:
                    cname = labels[i][0]
                    persona = labels[i][1] if source == "cli" else persona
                else:
                    cname = f"{name}#{i:03d}"
                rows.append(dict(case=cname, source=f"{source}:{name}" if not labels else source,
                                 persona=persona, mode=mode, text=text, exit=code,
                                 reasons=(reasons or "").strip()[:600]))
    finally:
        subprocess.run = _REAL_RUN
        devnull.close()


def collect_shadows(rows):
    s = _load("_parity_shadows", os.path.join(ROOT, "tests/integration/test-validate-digest-shadows.py"))
    real = s._errors
    for fn in ("case_matrix_floor", "case_human_commits", "case_dirty_tree", "case_qa_kinds",
               "case_receipt", "case_inspection_citations", "case_findings_order",
               "case_grade_2_names", "case_qa_unearned_fail"):
        seq = [0]

        def spy(v, persona, text, fd, cfg, _fn=fn):
            errs = real(v, persona, text, fd, cfg)
            rows.append(dict(case=f"{_fn}#{seq[0]:02d}", source="shadow", persona=persona,
                             mode="in-process validate()", text=text,
                             exit=0 if not errs else 2, reasons="; ".join(errs)[:600]))
            seq[0] += 1
            return errs
        s._errors = spy
        getattr(s, fn)()
    s._errors = real
    return len(s.RESULTS)


def collect_probe(rows):
    src = open(os.path.join(ROOT, "tests/manual/probe-inflight-claim-lifecycle.py")).read()
    import ast
    ns = {}
    wanted = ("FEATURE", "DIGEST", "LEAD_DIGEST")
    for node in ast.parse(src).body:  # constants only; the live probe needs OMP + a provider
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) in wanted for t in node.targets):
            exec(ast.get_source_segment(src, node), ns)
    for cname, persona, text in (
            ("S1/S2/S3 orchestrator child DIGEST", "harness-orchestrator", ns["DIGEST"]),
            ("S3 nested lead LEAD_DIGEST", "harness-eng-lead", ns["LEAD_DIGEST"])):
        r = _REAL_RUN([VALIDATE, persona], input=text.strip() + "\n", capture_output=True, text=True)
        rows.append(dict(case=cname, source="claim-lifecycle", persona=persona, mode="cli",
                         text=text, exit=r.returncode, reasons=r.stdout.strip()[:600]))


def collect_readers(rows):
    """Non-plan digest readers: INV-15/46 (ctx.lead_digest -> validate('lead')) and the
    tail VERDICT read shared by INV-46/47 (_inv15_digest_verdict)."""
    rec = _load("_parity_rec", os.path.join(ROOT, "tests/integration/test-check-state-records.py"))
    f59 = _load("_parity_f59", os.path.join(ROOT, "tests/integration/test-check-state-feat59.py"))
    from check_state.run_state import _inv15_digest_verdict
    v = _load("_parity_vd", VALIDATE)
    cases = [(f"INV-15/46 BUG-440 lead digest {vd}", rec._bug440_digest(v, vd))
             for vd in ("FAIL", "PASS")]
    cases += [("INV-15 BUG-440 run X bare 'VERDICT: FAIL'", "VERDICT: FAIL\n"),
              ("INV-15 feat59 _digest_run 'VERDICT: PASS'", "VERDICT: PASS\n"),
              ("INV-47 _QA_BLOCKED note", f59._QA_BLOCKED),
              ("INV-47 _QA_PASS note", f59._QA_PASS),
              ("INV-47 _UI_NA note", f59._UI_NA)]
    for cname, text in cases:
        errs = v.validate("lead", text)
        m = _inv15_digest_verdict(text)
        rows.append(dict(case=cname, source="reader", persona="lead",
                         mode="validate('lead') + _inv15_digest_verdict", text=text,
                         exit=0 if not errs else 2,
                         tail_verdict=m.group(1) if m else None,
                         reasons="; ".join(errs)[:600]))


# ------------------------------------------------------------------ main -------------
def build():
    rows = []
    collect_validate_digest(rows)
    shadow_checks = collect_shadows(rows)
    collect_probe(rows)
    collect_readers(rows)
    for n, r in enumerate(rows):
        r["id"] = f"P{n:04d}"
        r["accept"] = r["exit"] == 0
        r["input_sha256"] = hashlib.sha256((r["text"] or "").encode()).hexdigest()[:16]
        obj, why = to_object(r["text"])
        r["object"] = obj
        r["syntax_only"] = obj is None
        r["counterpart"] = counterpart(r["reasons"] + " " + why, r["case"]) if obj is None else ""
        r["why_no_object"] = why
    return rows, shadow_checks


def result_key(rows):
    return {r["id"]: [r["case"], r["source"], r["persona"], r["accept"], r["exit"]] for r in rows}


def main(argv):
    rows, shadow_checks = build()
    if argv[:1] == ["--check"]:
        want = json.load(open(BASELINE))["results"]
        got = result_key(rows)
        drift = sorted(k for k in set(want) | set(got) if want.get(k) != got.get(k))
        for k in drift:
            print(f"DRIFT {k}: baseline={want.get(k)} now={got.get(k)}")
        print(f"{len(got)} cases, {len(drift)} drift")
        return 1 if drift else 0
    os.makedirs(FIX, exist_ok=True)
    for r in rows:
        with open(os.path.join(FIX, r["id"] + ".json"), "w") as fh:
            json.dump({k: r[k] for k in ("id", "case", "source", "persona", "mode", "input_sha256",
                                         "text", "object", "syntax_only", "counterpart",
                                         "why_no_object", "accept", "exit", "reasons")
                       if k in r}, fh, indent=1, sort_keys=True, default=str)
    head = _REAL_RUN(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    vsha = hashlib.sha256(open(VALIDATE, "rb").read()).hexdigest()
    json.dump({"baseline_sha": head, "validate_digest_sha256": vsha,
               "shadow_check_results": shadow_checks, "results": result_key(rows)},
              open(BASELINE, "w"), indent=1, sort_keys=True)
    with open(os.path.join(HERE, "parity-table.md"), "w") as fh:
        for r in rows:
            cname = r["case"].replace("|", "\\|").replace("\n", " ")[:140]
            fh.write(f"| {r['id']} {cname} | {r['source']} | {r['persona']} | "
                     f"{'accept' if r['accept'] else 'reject'} (exit {r['exit']}) | "
                     f"parity-fixtures/{r['id']}.json | "
                     f"{('syntax-only: ' + r['counterpart']) if r['syntax_only'] else ''} |  |  |\n")
    counts = {}
    for r in rows:
        counts[r["source"]] = counts.get(r["source"], 0) + 1
    print(json.dumps({"head": head, "validate_sha256": vsha, "rows": len(rows),
                      "shadow_check_results": shadow_checks, "counts": counts,
                      "syntax_only": [(r["id"], r["case"], r["counterpart"], r["why_no_object"])
                                      for r in rows if r["syntax_only"]]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
