#!/usr/bin/env python3
r"""FEAT-1928 T-02 object half: re-run every baseline case against the OBJECT validator.

    parity-object.py            write object-results.json and print the table columns
    parity-object.py --table    also rewrite validator-parity.md's `new result`/`match`

The owning test modules are executed from their source AT THE BASELINE SHA (git show), so
each group rebuilds exactly the state (git range, claims, artifacts, stubs) it built for the
baseline run, while their `VALIDATE` path is the worktree's object validator. Every call to
it is intercepted and its digest re-expressed as the mapping the case means:

  CLI      stdin text  -> JSON of the case's mapping
  hook     `last_assistant_message` -> `digest_object` (absent stays absent, null stays null)
  shadow   the in-process `_errors` seam calls validate(persona, mapping, ...)
  readers / claim-lifecycle   validate(persona, mapping) / the CLI with the mapping

The mapping is `yaml.safe_load` of the text from its last `^\\s*VERDICT:` anchor (the same
tail the baseline validator sliced), with one reading rule the baseline parser applied and
YAML does not: a bare top-level DIGEST key is an EMPTY LIST ("bare key followed by nothing
is an empty list"), and VERDICT is its first token (the baseline read `VERDICT:\s*(\S+)`, so
a retired template's `PASS | FAIL | ...` line meant PASS). Text with no mapping (the syntax-only rows) is sent as its object
counterpart: a blank or absent message as absent `data`, a bare string as that string.
Rows are aligned to baseline.json by call order within each group; a count mismatch stops.
"""
import ast, hashlib, importlib.util, json, os, re, subprocess, sys, types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
BIN = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
VALIDATE = os.path.join(BIN, "validate-digest.py")
FIX = os.path.join(HERE, "parity-fixtures")
BASELINE = json.load(open(os.path.join(HERE, "baseline.json")))
BASE_SHA = BASELINE["baseline_sha"]
sys.path.insert(0, BIN)
import yaml  # noqa: E402

_REAL_RUN = subprocess.run
RECORD = []
_ABSENT = object()
SPELLED = []  # per validator call, in call order: the ruling fields the translation spelled

sys.path.insert(0, BIN)
import digest_schema  # noqa: E402

# The FEAT-1928 operator ruling (2026-09-29): every DIGEST field is required and a field that
# does not apply is spelled `none` (scalar) or `[]` (list). At the baseline these fields were
# optional or conditional, and OMITTING one was how a digest said "does not apply". The
# mapping a baseline case means therefore spells each one it omits as not-applicable — the
# same table tests/integration/test-validate-digest.py's `fixture()` uses.
_LEAD = {"adequacy_notes": [], "sc_status": [], "needs_approval": "none", "severity_max": "none",
         "matrix_ok": "none", "coverage_gaps": [], "findings": [], "readers": []}
_DEV = {"task_verify": "n/a"}
RULING_FIELDS = {
    "harness-eng-lead": {**_LEAD, "amendments": []}, "harness-product-lead": _LEAD,
    "harness-validator-lead": _LEAD, "harness-backend-dev": _DEV, "harness-frontend-dev": _DEV,
    "harness-ai-dev": _DEV, "harness-data-engineer": _DEV,
    "harness-dev-ops": {**_DEV, "test_kinds_written": []},
    "harness-qa": {"kinds": [], "sc_evidence": []},
    "harness-code-reviewer": {"spec_violations": [], "human_commits_in_scope": [],
                              "grade_2_reasons": []},
    "harness-security-reviewer": {"in_scope": "none", "scope_reason": "none", "threat_model": []},
    "harness-ui-reviewer": {"mode": "none", "in_scope": "none", "states_unspecified": [],
                            "contract_violations": [], "a11y": []},
    "harness-visual-designer": {"needs_prototype": "none", "why": "none", "prototype": "none"},
    "harness-documentor": {"stale_found": []},
    "harness-orchestrator": {"judgement": "none"},
}


# The ruling also closed each list-entry object to its minimal shape. The baseline validator
# read only `verdict`/`status`/`reason` of a member, `kind`/`scope`/`severity` of a finding and
# `kind`/`state` of a kinds entry; every other entry key was free text it never read. So an
# entry means the same once its unread keys are dropped and its unread required keys are
# spelled not-applicable. A key the baseline DID read is never added (a member without a
# verdict, a proportionality finding without a scope stay exactly as written).
_MEMBER_RAN = ("step", "persona", "verdict", "headline", "files_touched")
_MEMBER_SKIPPED = ("step", "persona", "status", "reason")


def _reshape_member(entry):
    keys = _MEMBER_SKIPPED if entry.get("status") == "skipped" else _MEMBER_RAN
    out = {k: entry[k] for k in keys if k in entry}
    if keys is _MEMBER_RAN:
        out.setdefault("headline", "none")
        out.setdefault("files_touched", [])
    return out


def _reshape_finding(entry):
    out = dict(entry)
    if out.get("kind") != "proportionality":
        out.setdefault("scope", "none")
    for key in ("reader", "summary", "why"):
        out.setdefault(key, "none")
    return out


def _reshape_kind(entry):
    out = dict(entry)
    out["cmd"] = out["cmd"] if isinstance(out.get("cmd"), str) else "none"
    out.setdefault("named_tests", "none")
    return out


def _reshape_reader(entry):
    out = dict(entry)
    out.setdefault("persona", "none")
    out.setdefault("reason", "none")
    return out


_RESHAPE = {"members": _reshape_member, "findings": _reshape_finding, "kinds": _reshape_kind,
            "readers": _reshape_reader}


def _reshape_entries(digest):
    notes = []
    for field, reshape in _RESHAPE.items():
        entries = digest.get(field)
        if not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            if isinstance(entry, dict) and reshape(entry) != entry:
                entries[index] = reshape(entry)
                notes.append(f"{field}[{index}]")
    runs = digest.get("runs")
    if isinstance(runs, list):
        for index, run in enumerate(runs):
            if isinstance(run, str):  # `runs: [r1]` named the run id only
                runs[index] = {"id": run, "squad": "none", "verdict": "none"}
                notes.append(f"runs[{index}]")
    return notes


def spell_ruling(obj, persona):
    """`obj` translated to the ruling: every ruling field it omits spelled not-applicable and
    every entry closed to its minimal shape; the fields and entries touched."""
    digest = obj.get("DIGEST") if isinstance(obj, dict) else None
    try:
        canonical = digest_schema.canonical_persona(persona) if isinstance(persona, str) else None
    except digest_schema.DigestSchemaError:
        canonical = None
    if not isinstance(digest, dict) or canonical is None:
        return []
    as_written = digest_schema.validate_object(canonical, json.loads(json.dumps(obj)))
    spelled = [f for f in RULING_FIELDS.get(canonical, {}) if f not in digest]
    for field in spelled:
        value = RULING_FIELDS[canonical][field]
        digest[field] = list(value) if isinstance(value, list) else value
    touched = spelled + _reshape_entries(digest)
    # Every touched row is refused AS WRITTEN (a required field absent, an entry open); the
    # schema's own verdict on the untranslated mapping is kept as the evidence of that.
    return touched + (["as-written schema errors: %d" % len(as_written)] if touched else [])


def _tail(text):
    anchors = list(re.finditer(r"^\s*VERDICT:", text, re.M))
    return text[anchors[-1].start():] if anchors else text


def as_object(text):
    """The mapping a baseline digest text means, or None when it has none."""
    if not isinstance(text, str):
        return None
    try:
        doc = yaml.safe_load(_tail(text))
    except yaml.YAMLError:
        return None
    if not isinstance(doc, dict):
        return None
    verdict = doc.get("VERDICT")
    if isinstance(verdict, str) and verdict.split():
        doc["VERDICT"] = verdict.split()[0]   # the baseline read `VERDICT:\s*(\S+)`
    digest = doc.get("DIGEST")
    if isinstance(digest, dict):
        for key, value in digest.items():
            if value is None:
                digest[key] = []
    return doc


# Syntax-only CLI rows: the baseline text has no mapping, so the object counterpart the
# baseline doc names is built from the text's intent. P0025 jams three fields on one line;
# its counterpart is the digest with the two lost fields MISSING.
def _p0025_counterpart(text):
    fixed = text.replace("  team: build            steps_run: 3   cycles_used: 0\n",
                         "  team: build\n")
    return as_object(fixed)


def cli_input(text, persona):
    obj = as_object(text)
    if obj is None and "steps_run: 3   cycles_used: 0" in (text or ""):
        obj = _p0025_counterpart(text)
    SPELLED.append(spell_ruling(obj, persona) if obj is not None else [])
    return json.dumps(obj) if obj is not None else json.dumps(text)


def hook_input(stdin):
    try:
        payload = json.loads(stdin)
    except (TypeError, ValueError):
        SPELLED.append([])
        return stdin  # P0000: an unreadable payload is forwarded unchanged
    if not isinstance(payload, dict):
        SPELLED.append([])
        return stdin
    SPELLED.append([])
    text = payload.pop("last_assistant_message", _ABSENT)
    if text is _ABSENT:
        return json.dumps(payload)
    if text is None:
        payload["digest_object"] = None
        return json.dumps(payload)
    obj = as_object(text)
    if obj is not None:
        SPELLED[-1] = spell_ruling(obj, payload.get("agent_type"))
        payload["digest_object"] = obj
    elif str(text).strip():
        payload["digest_object"] = text          # wrong-type: string data
    return json.dumps(payload)                 # blank: missing (absent data)


def _validator_index(argv):
    for index, arg in enumerate(argv[:2]):
        if os.path.abspath(str(arg)) == VALIDATE:
            return index
    return None


def _recording_run(argv, *a, **kw):
    index = _validator_index(argv) if isinstance(argv, (list, tuple)) else None
    if index is not None:
        stdin = kw.get("input")
        tail = list(argv[index + 1:])
        del SPELLED[:]
        if "--hook" in tail:
            kw["input"] = hook_input(stdin)
        elif len(tail) == 1:
            kw["input"] = cli_input(stdin, tail[0])
        else:
            SPELLED.append([])
        r = _REAL_RUN(argv, *a, **kw)
        RECORD.append((list(argv), kw.get("input"), r.returncode, r.stdout, r.stderr,
                       SPELLED[0] if SPELLED else []))
        return r
    return _REAL_RUN(argv, *a, **kw)


def _baseline_module(name, rel):
    src = _REAL_RUN(["git", "-C", ROOT, "show", f"{BASE_SHA}:{rel}"], capture_output=True,
                    text=True, check=True).stdout
    mod = types.ModuleType(name)
    mod.__file__ = os.path.join(ROOT, rel)
    sys.modules[name] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


def _load_new_validator():
    spec = importlib.util.spec_from_file_location("_parity_new_vd", VALIDATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GROUPS = ("run_canonical_reader_strictness_cases", "run_feat65_guard_cases",
          "run_cli_cases", "run_empty_red_case", "run_dec156_worktree_red_case",
          "run_bug919_qa_matrix_cases", "run_bug919_resolve_fallback_case",
          "run_bug919_resolve_by_artifact_case", "run_joint_hint_case",
          "run_code_grade_cases", "run_hook_cases", "run_bug1305_artifact_resolution_cases",
          "run_t09", "run_t51_suspension_cases", "run_bug1898_exact_release_cases",
          "run_template_cases", "run_reviewer_severity_enum_cases",
          "run_documented_contract_cases", "run_t01_schema_cases",
          "run_t04_unknown_key_cases", "run_t08_revision_proof")


def _replay_fixture_rows(group):
    """A baseline group that can no longer run (it reads a table or template the hard cut
    deleted) is replayed from its recorded fixtures: each call's persona and mapping."""
    out = []
    for row_id in sorted(BASELINE["results"]):
        fixture = json.load(open(os.path.join(FIX, row_id + ".json")))
        if fixture["source"] != f"cli-group:{group}":
            continue
        del SPELLED[:]
        r = _REAL_RUN([VALIDATE, fixture["persona"]],
                      input=cli_input(fixture["text"], fixture["persona"]),
                      capture_output=True, text=True)
        out.append((f"{group} (fixture replay)", r.returncode, r.stdout.strip()[:600],
                    SPELLED[0]))
    return out


def collect_validate_digest(results):
    t = _baseline_module("_parity_obj_tvd", "tests/integration/test-validate-digest.py")
    # The baseline red proofs build a mutant by matching the OLD validator's source text;
    # that text is gone, so each mutant is the new source plus a comment. Only the mutant
    # binary changes; the real-validator call each group makes (a baseline row) is kept.
    t._bug919_red_mutant = lambda: open(VALIDATE).read() + "\n# parity\n"
    t._empty_red_mutant = lambda source: source + "\n# parity\n"
    t._dec156_owner_root_mutant = lambda source: source + "\n# parity\n"
    # The two normative text templates were retired by the hard cut; the template group
    # reads them as they stood at the baseline SHA.
    baseline_extract = t.extract_fenced_block

    def extract_at_baseline(path, anchor):
        rel = os.path.relpath(os.path.realpath(path), os.path.realpath(ROOT))
        src = _REAL_RUN(["git", "-C", ROOT, "show", f"{BASE_SHA}:{rel}"], capture_output=True,
                        text=True, check=True).stdout
        tmp = os.path.join(HERE, ".baseline-template.md")
        with open(tmp, "w") as fh:
            fh.write(src)
        try:
            return baseline_extract(tmp, anchor)
        finally:
            os.remove(tmp)
    t.extract_fenced_block = extract_at_baseline
    # T-04's in-process half reads the deleted parse_digest/SCHEMAS tables; its two hook
    # calls (the baseline rows) are the same helper with the same three-rogue-key digest.
    t.run_t04_unknown_key_cases = lambda: t._t04_hook_failures(t._t04_with_fields(
        t.LEAD_BLOCK, {"rogue_alpha": 1, "rogue_beta": 2, "rogue_gamma": 3}))
    subprocess.run = _recording_run
    devnull = open(os.devnull, "w")
    try:
        for name in GROUPS:
            start = len(RECORD)
            real_stdout, sys.stdout = sys.stdout, devnull
            try:
                getattr(t, name)()
            except Exception as error:  # noqa: BLE001 — a baseline group reading a deleted table
                results.append(("group-error", name, repr(error)))
                del RECORD[start:]
                results.extend(_replay_fixture_rows(name))
                continue
            finally:
                sys.stdout = real_stdout
            for argv, stdin, code, out, err, spelled in RECORD[start:]:
                results.append((name, code, (err if "--hook" in argv else out).strip()[:600],
                                spelled))
    finally:
        subprocess.run = _REAL_RUN
        devnull.close()


def collect_shadows(results, v):
    s = _baseline_module("_parity_obj_shadows", "tests/integration/test-validate-digest-shadows.py")
    for fn in ("case_matrix_floor", "case_human_commits", "case_dirty_tree", "case_qa_kinds",
               "case_receipt", "case_inspection_citations", "case_findings_order",
               "case_grade_2_names", "case_qa_unearned_fail"):
        def spy(_v, persona, text, fd, cfg):
            obj = as_object(text)
            spelled = spell_ruling(obj, persona)
            errs = v.validate(persona, obj, cfg, fd, branch_override=None)
            results.append(("shadow", 0 if not errs else 2, "; ".join(errs)[:600], spelled))
            return errs
        s._errors = spy
        getattr(s, fn)()


def collect_probe(results):
    src = _REAL_RUN(["git", "-C", ROOT, "show", f"{BASE_SHA}:tests/manual/probe-inflight-claim-lifecycle.py"],
                    capture_output=True, text=True, check=True).stdout
    ns = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) in ("FEATURE", "DIGEST", "LEAD_DIGEST")
                                                for t in node.targets):
            exec(ast.get_source_segment(src, node), ns)
    for persona, text in (("harness-orchestrator", ns["DIGEST"]), ("harness-eng-lead", ns["LEAD_DIGEST"])):
        obj = as_object(text)
        spelled = spell_ruling(obj, persona)
        r = _REAL_RUN([VALIDATE, persona], input=json.dumps(obj), capture_output=True, text=True)
        results.append(("claim-lifecycle", r.returncode, r.stdout.strip()[:600], spelled))


# Readers no longer validate (SC-07): INV-15/46 read digest_record's final fenced mapping and
# accept a record carrying VERDICT, DIGEST and artifact; INV-47 reads that mapping's VERDICT.
# The fixture text is the block the baseline reader saw, fenced as the durable file holds it.
READER_TAIL_VERDICT = {"P0288": "BLOCKED", "P0289": "PASS", "P0290": "n/a"}


def collect_readers(results, v):
    import digest_record
    from check_state.run_state import _inv15_digest_verdict
    for row_id in ("P0284", "P0285", "P0286", "P0287", "P0288", "P0289", "P0290"):
        text = json.load(open(os.path.join(FIX, row_id + ".json")))["text"]
        fenced = text if "```" in text else f"# prose\n\n```yaml\n{_tail(text)}```\n"
        try:
            record = digest_record.last_fenced_mapping(fenced, row_id)
        except digest_record.DigestRecordError as error:
            results.append(("reader", 2, str(error)[:600], []))
            continue
        missing = [k for k in ("VERDICT", "DIGEST", "artifact") if k not in record]
        verdict = _inv15_digest_verdict(record)
        note = f"record keys missing {missing}" if missing else "record complete"
        if row_id in READER_TAIL_VERDICT:
            note += (f"; INV-47 verdict {verdict!r} "
                     f"({'==' if verdict == READER_TAIL_VERDICT[row_id] else '!='} baseline "
                     f"tail {READER_TAIL_VERDICT[row_id]!r})")
        results.append(("reader", 2 if missing else 0, note, []))


# The syntax-only rows whose ORIGINAL input the object validator cannot receive as a
# digest at all; each is also run as the explicit object counterpart case named in the
# baseline doc, and that counterpart must reject.
def counterpart_cases(v):
    base = json.load(open(os.path.join(FIX, "P0138.json")))["object"]  # a valid qa object
    extra = json.loads(json.dumps(base))
    extra["DIGEST"]["agent_type"] = "duplicate"
    missing = json.loads(json.dumps(base))
    del missing["DIGEST"]["suite"]
    lead = json.load(open(os.path.join(FIX, "P0023.json")))["object"]
    lead_missing = json.loads(json.dumps(lead))
    del lead_missing["DIGEST"]["steps_run"], lead_missing["DIGEST"]["cycles_used"]
    cases = {
        "P0000": ("extra key", v.validate("harness-qa", extra)),
        "P0025": ("missing steps_run, cycles_used", v.validate("harness-validator-lead", lead_missing)),
        "P0136": ("missing (absent data)", v.validate("harness-qa", None)),
        "P0157": ("missing (absent data)", v.validate("harness-qa", None)),
        "P0158": ("missing (absent data)", v.validate("harness-qa", None)),
        "P0159": ("missing (null data)", v.validate("harness-qa", None)),
        "P0161": ("wrong-type (string data)", v.validate("harness-qa", "done")),
        "P0169": ("wrong-type (string data)", v.validate("harness-qa", "whatever")),
        "P0194": ("missing field (suite)", v.validate("harness-qa", missing)),
        "P0195": ("missing field (suite)", v.validate("harness-qa", missing)),
    }
    return {k: {"counterpart": what, "reject": bool(errs), "reasons": "; ".join(errs)[:300]}
            for k, (what, errs) in cases.items()}


# Deltas the plan requires. Each id maps to the rule that makes the object result differ.
PLANNED = {
    "P0000": "SC-02: the object counterpart (an extra key) is refused; the unreadable payload itself still fails open under hook_guard",
    "P0158": "SC-02: absent yield data is blocked with the object instruction",
    "P0159": "SC-02: null yield data is blocked with the object instruction",
    "P0161": "SC-02: string data is blocked before the stop_hook_active pass-through",
    "P0169": "SC-02: string data is blocked even with no agent_type",
}
# SC-07 (Main-approved 2026-09-29): the lead append replaces DEC-156's file validation.
SC07_NARRATIVE = ("P0137", "P0162", "P0166", "P0178", "P0181")
SC07_UNRESOLVABLE = ("P0168", "P0182", "P0188")
# FEAT-1928 ruling: expertise_update entries are the closed expertise-merge op shapes. The
# distill fixtures' `{file, ops: 3}` entry is a summary, not an op, and no op can be derived
# from it without inventing its entry text — so these two rows are refused at that entry.
RULING_ENTRY = ("P0171", "P0174")


def classify(row_id, row):
    """The `match` cell: `yes` or the planned rule a delta follows, plus the ruling
    translation when the row needed one. None is an UNPLANNED mismatch and fails the run."""
    rule = _rule(row_id, row)
    touched = [t for t in row.get("ruling_spelled") or [] if not t.startswith("as-written")]
    if rule is None or not touched:
        return rule
    return (f"{rule} — as written refused by the FEAT-1928 ruling; translated "
            f"({', '.join(touched)})")


def _rule(row_id, row):
    same = row["baseline_accept"] == row["new_accept"]
    if row_id in PLANNED:
        return "planned delta — " + PLANNED[row_id] if not same or row_id == "P0000" else None
    if row_id in SC07_NARRATIVE:
        return ("planned delta — SC-07: the lead's digest.md held prose (or an out-of-contract "
                "block) and the validated object is appended under it instead of refused"
                if not same else None)
    if row_id in RULING_ENTRY:
        return ("planned delta — FEAT-1928 ruling: expertise_update[0] `{file, ops}` is not "
                "one of the closed expertise-merge op shapes" if not same else None)
    if row_id in SC07_UNRESOLVABLE:
        return ("planned delta — SC-07: a lead artifact that does not resolve to an existing "
                "digest.md now refuses the return (was DEC-156's loud fail-open)"
                if not same else None)
    return "yes" if same else None


def write_table(rows):
    doc_path = os.path.join(HERE, "..", "validator-parity.md")
    lines = open(doc_path, encoding="utf-8").read().split("\n")
    out = []
    in_table = False
    for line in lines:
        if line.startswith("## "):
            in_table = line.strip() == "## Table"
        # Main-table rows only: `| P0123 case-name |` (id and case share the first cell).
        m = re.match(r"^\| (P\d{4}) [^|]", line) if in_table else None
        if m and m.group(1) in rows:
            row = rows[m.group(1)]
            cell = f"{'accept' if row['new_accept'] else 'reject'} (exit {row['new_exit']})"
            cp = row.get("counterpart")
            if cp:
                cell += f"; object counterpart ({cp['counterpart']}): {'reject' if cp['reject'] else 'ACCEPT'}"
            # The last two cells (`new result`, `match`) are this script's; rewrite them.
            kept = line.rstrip().rstrip("|").split(" | ")[:-2]
            line = " | ".join(kept) + f" | {cell} | {classify(m.group(1), row)} |"
        out.append(line)
    with open(doc_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


def main(argv):
    v = _load_new_validator()
    got = []
    collect_validate_digest(got)
    errors = [g for g in got if g[0] == "group-error"]
    got = [g for g in got if g[0] != "group-error"]
    collect_shadows(got, v)
    collect_probe(got)
    collect_readers(got, v)
    base = BASELINE["results"]
    ids = sorted(base)
    if len(got) != len(ids):
        print(f"ALIGNMENT: {len(got)} object calls vs {len(ids)} baseline rows; group errors {errors}")
        return 1
    rows = {}
    for row_id, (group, code, reasons, spelled) in zip(ids, got):
        case, source, persona, accept, exit_code = base[row_id]
        rows[row_id] = dict(case=case, source=source, persona=persona, baseline_accept=accept,
                            baseline_exit=exit_code, new_accept=code == 0, new_exit=code,
                            group=group, reasons=reasons, ruling_spelled=spelled)
    cps = counterpart_cases(v)
    for row_id, cp in cps.items():
        rows[row_id]["counterpart"] = cp
    out = {"baseline_sha": BASE_SHA,
           "validator_sha256": hashlib.sha256(open(VALIDATE, "rb").read()).hexdigest(),
           "head": _REAL_RUN(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True,
                             text=True).stdout.strip(),
           "group_errors": errors, "rows": rows}
    json.dump(out, open(os.path.join(HERE, "object-results.json"), "w"), indent=1, sort_keys=True)
    mism = [(k, r) for k, r in rows.items() if r["baseline_accept"] != r["new_accept"]]
    unplanned = [k for k, r in rows.items() if classify(k, r) is None]
    bad_counterparts = [k for k, c in cps.items() if not c["reject"]]
    for k, r in mism:
        print(f"DELTA {k} [{r['source']}] {r['case'][:70]!r} base={'A' if r['baseline_accept'] else 'R'}"
              f"{r['baseline_exit']} new={'A' if r['new_accept'] else 'R'}{r['new_exit']} :: {r['reasons'][:260]}")
    print(f"{len(rows)} rows, {len(mism)} accept/reject deltas, {len(unplanned)} unplanned "
          f"{unplanned}; counterparts rejecting: {len(cps) - len(bad_counterparts)}/{len(cps)}; "
          f"groups replayed after reading a deleted table: {[e[1] for e in errors]}")
    if unplanned or bad_counterparts:
        return 1
    if argv[:1] == ["--table"]:
        write_table(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
