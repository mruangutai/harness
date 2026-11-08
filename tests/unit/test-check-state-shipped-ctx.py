#!/usr/bin/env python3
"""check_state's context drops shipped features before anything reads them (FEAT-2206 SC-01).

"Shipped" is one lenient read of a plan.yaml's top-level `status:` line equal to `done`. These
tests build the real `check_state.ctx.Ctx` in-process over synthetic feature directories and
record every file the construction opens with a Python audit hook, so "shipped records are not
opened" is observed rather than inferred.

CHECK_STATE_BIN_DIR points the import at another bin directory (a baseline export) so the same
assertions can be shown failing against the code before the change.

    ./test-check-state-shipped.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = (_anchor_os.environ.get("CHECK_STATE_BIN_DIR")
               or _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin"))
_anchor_sys.path.insert(0, _anchor_bin)
import json
import os
import sys
import tempfile

import artifact_accessors  # noqa: E402
from check_state import ctx as check_ctx  # noqa: E402

FAILURES = []

# Strict-schema-invalid on purpose: `tasks` must be a list. Shipped must not depend on it.
STRICT_INVALID_DONE = "schema: plan/1\nfeature: {fid}\nstatus: done\ntasks: 7\n"

PLANS = {
    "FEAT-1-shipped": STRICT_INVALID_DONE,
    "FEAT-2-shipped-quoted": 'schema: plan/1\nstatus: "done"   # landed\ntasks: []\n',
    "FEAT-3-building": "schema: plan/1\nstatus: building\ntasks: []\n",
    "FEAT-4-no-status": "schema: plan/1\ntasks: []\n",
    "FEAT-5-nested-status": "schema: plan/1\nmeta:\n  status: done\ntasks: []\n",
    "FEAT-6-no-plan": None,
    "FEAT-7-not-utf8": b"status: done\n\xff\xfe\n",
    "FEAT-8-list-document": "- status: done\n",
    "FEAT-9-two-statuses": "status: done\nstatus: building\n",
    # A second status KEY makes the plan ambiguous whatever its value: never "shipped".
    "FEAT-10-done-then-list": "status: done\nstatus: [building]\n",
    "FEAT-11-done-then-empty": "status: done\nstatus:\n",
    "FEAT-12-number-then-done": "status: 7\nstatus: done\n",
    "FEAT-13-done-then-quoted-key": 'status: done\n"status": building\n',
}
SHIPPED = {"FEAT-1-shipped", "FEAT-2-shipped-quoted"}
NOT_SHIPPED = sorted(set(PLANS) - SHIPPED)


def check(name, cond, detail=""):
    if cond:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}{(' — ' + detail) if detail else ''}")
        FAILURES.append(name)


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(path, mode) as fh:
        fh.write(data)


def _tree(root, plans=PLANS, feature_json=None):
    """One feature directory per plan; every one also carries an UNSIGNED BRIEF, a STATE.md and
    a feature.json, so a pass that opened a shipped directory would have something to open."""
    _write(os.path.join(root, ".harness", "harness.json"), "{}\n")
    for fid, plan in plans.items():
        d = os.path.join(root, ".harness", "harness", "features", fid)
        if plan is not None:
            _write(os.path.join(d, "plan.yaml"),
                   plan.replace("{fid}", fid) if isinstance(plan, str) else plan)
        _write(os.path.join(d, "BRIEF.md"), f"# BRIEF {fid}\n")
        _write(os.path.join(d, "STATE.md"), "# STATE\n")
        doc = (feature_json or {}).get(fid, {"feature_id": fid, "branch": "none"})
        _write(os.path.join(d, "feature.json"), doc if isinstance(doc, str) else json.dumps(doc))


class _Opens:
    """Every path opened while active, resolved to an absolute real path. Audit hooks cannot be
    removed, so one is installed once and records only while an instance is live."""
    _live = None
    _installed = False

    def __init__(self):
        self.paths = []
        if not _Opens._installed:
            sys.addaudithook(_Opens._hook)
            _Opens._installed = True

    @staticmethod
    def _hook(event, args):
        live = _Opens._live
        if live is not None and event == "open" and isinstance(args[0], (str, bytes)):
            p = os.fsdecode(args[0])
            live.paths.append(os.path.realpath(p if os.path.isabs(p) else os.path.join(os.getcwd(), p)))

    def __enter__(self):
        _Opens._live = self
        return self

    def __exit__(self, *exc):
        _Opens._live = None
        return False


def _ctx(root, keep=None):
    sys.argv = [sys.argv[0], root, _anchor_bin]
    return check_ctx.Ctx(root, keep=keep)


def _opened_in(paths, root, fid):
    base = os.path.realpath(os.path.join(root, ".harness", "harness", "features", fid)) + os.sep
    return sorted({p[len(base):] for p in paths if p.startswith(base)})


def case_classification_selects_only_unshipped_subjects():
    with tempfile.TemporaryDirectory() as root:
        _tree(root)
        # Precondition: the shipped fixture really is invalid under the strict loader, so the
        # selection below cannot be passing because the plan happened to parse.
        try:
            artifact_accessors.load_plan(
                os.path.join(root, ".harness", "harness", "features", "FEAT-1-shipped", "plan.yaml"))
            strict_rejects = False
        except Exception:  # noqa: BLE001 — any strict refusal satisfies the precondition
            strict_rejects = True
        check("precondition: the shipped fixture plan fails the strict loader", strict_rejects)
        ctx = _ctx(root)
        check("subjects are exactly the unshipped features (missing, unreadable, nested, "
              "non-mapping, ambiguous and non-done status stay checked)",
              ctx.features == NOT_SHIPPED, f"features={ctx.features}")
        check("the context records which discovered features shipped",
              getattr(ctx, "shipped", None) == SHIPPED, f"shipped={getattr(ctx, 'shipped', None)}")
        loading = [m for m in ctx.bad if "FEAT-1-shipped" in m or "FEAT-2-shipped" in m]
        check("a strict-invalid shipped plan produces no loading finding", not loading,
              "; ".join(loading))


def case_shipped_directories_are_not_read_up_front():
    with tempfile.TemporaryDirectory() as root:
        _tree(root)
        with _Opens() as seen:
            _ctx(root)
        for fid in sorted(SHIPPED):
            opened = _opened_in(seen.paths, root, fid)
            check(f"{fid}: context construction opens only its plan.yaml",
                  opened == ["plan.yaml"], f"opened={opened}")
        opened = _opened_in(seen.paths, root, "FEAT-3-building")
        check("control: an unshipped feature's BRIEF and plan are still read up front",
              "BRIEF.md" in opened and "plan.yaml" in opened, f"opened={opened}")


def case_an_explicit_shipped_keep_selects_nothing():
    with tempfile.TemporaryDirectory() as root:
        _tree(root)
        ctx = _ctx(root, keep={"FEAT-1-shipped"})
        check("keep={shipped} leaves no audit subject", ctx.features == [],
              f"features={ctx.features}")
        ctx = _ctx(root, keep={"FEAT-3-building"})
        check("control: keep={unshipped} keeps it", ctx.features == ["FEAT-3-building"],
              f"features={ctx.features}")


_POP_PLANS = {"FEAT-1-shipped": STRICT_INVALID_DONE, "FEAT-2-shipped-quoted": STRICT_INVALID_DONE,
              "FEAT-3-building": "schema: plan/1\nstatus: building\ntasks: []\n"}
_CLAIM = {"repo": "acme/widget", "issues": {"T-01": 11}}
_POP_DOCS = {"FEAT-1-shipped": {"feature_id": "FEAT-1-shipped", "factory": _CLAIM},
             "FEAT-2-shipped-quoted": "{ not json",
             "FEAT-3-building": {"feature_id": "FEAT-3-building", "factory": _CLAIM}}


def _population_fixture(root):
    """The context over the population tree, and the paths opened while it was built."""
    _tree(root, plans=_POP_PLANS, feature_json=_POP_DOCS)
    with _Opens() as seen:
        ctx = _ctx(root)
    return ctx, seen.paths


def case_population_reads_shipped_claims_lazily():
    with tempfile.TemporaryDirectory() as root:
        ctx, opened = _population_fixture(root)
        check("no shipped feature.json is opened while the context is built",
              not any("feature.json" in p for f in ("FEAT-1-shipped", "FEAT-2-shipped-quoted")
                      for p in _opened_in(opened, root, f)))
        population = ctx.population()
        shaped = all(isinstance(e, tuple) and len(e) == 3 for e in population)
        check("population entries carry (feature, document, shipped)", shaped, repr(population))
        by_id = {e[0]: e for e in population} if shaped else {}
        check("a readable shipped record is in the population, flagged shipped",
              by_id.get("FEAT-1-shipped", (None, None, False))[1:] == (_POP_DOCS["FEAT-1-shipped"], True),
              repr(by_id.get("FEAT-1-shipped")))
        check("an unshipped record is in the population, not flagged shipped",
              by_id.get("FEAT-3-building", (None, None, True))[2] is False, repr(by_id))


def case_an_unreadable_shipped_record_is_never_graded():
    with tempfile.TemporaryDirectory() as root:
        ctx, _opened = _population_fixture(root)
        by_id = {e[0]: e for e in ctx.population()}
        check("an unparseable shipped record contributes no claim",
              by_id.get("FEAT-2-shipped-quoted", (None, None))[1] is None, repr(by_id))
        graded = [m for m in ctx.bad + ctx.warn if "FEAT-2-shipped-quoted" in m]
        check("an unparseable shipped record is never reported", not graded, "; ".join(graded))


def main():
    case_classification_selects_only_unshipped_subjects()
    case_shipped_directories_are_not_read_up_front()
    case_an_explicit_shipped_keep_selects_nothing()
    case_population_reads_shipped_claims_lazily()
    case_an_unreadable_shipped_record_is_never_graded()
    print(f"\n{len(FAILURES)} failure(s)")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
