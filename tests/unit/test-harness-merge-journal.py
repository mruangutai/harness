#!/usr/bin/env python3
"""test-harness-merge-journal.py — house-shape suite for harness_merge's journaled pair write
and journal recovery (FEAT-2488 T-01).

Every case runs in a fresh tempfile.mkdtemp() and never touches a real .harness path. A case that
raises is reported as one FAIL line naming the exception, so a missing API fails per case instead
of aborting the run. Interleavings are deterministic: a test-side wrapper around
harness_merge.acquire mutates the disk before the real lock is taken — no sleeps, no threads.
"""
import base64
import contextlib
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from unittest.mock import patch

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
sys.path.insert(0, BIN_DIR)

import harness_merge  # noqa: E402

RESULTS = []
SUFFIX = ".harness-merge.journal"
SCHEMA = "harness-merge-journal/1"
PLAN = "plan.yaml"
LEDGER = "feature.json"
P0, P1, P2 = b"plan: base\n", b"plan: amended\n", b"plan: amended again\n"
S0, S1, S2 = b'{"ledger": []}\n', b'{"ledger": ["a"]}\n', b'{"ledger": ["a", "b"]}\n'
MINE = b"# caller's own change\n"


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(("PASS" if ok else "FAIL") + f" - {name}" + (f" ({detail})" if detail and not ok else ""))


# ---- fixtures ------------------------------------------------------------------------------

def sha(data):
    return None if data is None else hashlib.sha256(data).hexdigest()


def write(path, data):
    if data is None:
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)
        return
    with open(path, "wb") as fh:
        fh.write(data)


def read(path):
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except FileNotFoundError:
        return None


def snapshot(d):
    """Every file in d except the lock files (which are deliberately never removed)."""
    return {name: read(os.path.join(d, name)) for name in sorted(os.listdir(d))
            if not name.endswith(".lock")}


def journal_bytes(members):
    return json.dumps({"schema": SCHEMA, "members": [
        {"name": name, "before_sha256": sha(before), "after_sha256": sha(after),
         "after_b64": base64.b64encode(after).decode("ascii")}
        for name, before, after in members]}, sort_keys=True).encode("utf-8")


def put_journal(d, members):
    """The journal is named for its primary, the first member."""
    write(os.path.join(d, members[0][0] + SUFFIX), journal_bytes(members))


def pair_dir(plan, ledger, members=None):
    d = tempfile.mkdtemp()
    write(os.path.join(d, PLAN), plan)
    write(os.path.join(d, LEDGER), ledger)
    if members:
        put_journal(d, members)
    return d, os.path.join(d, PLAN), os.path.join(d, LEDGER)


J1 = [(PLAN, P0, P1), (LEDGER, S0, S1)]


def outcome(fn, *args, **kwargs):
    """('ok', value) | ('refusal', code, text) | ('pending', exc) | ('error', 'Type: msg')."""
    try:
        return ("ok", fn(*args, **kwargs))
    except harness_merge.MergeRefusal as exc:
        return ("refusal", exc.code, " ".join(exc.lines))
    except Exception as exc:  # noqa: BLE001 - JournalPending, ValueError, anything else
        if type(exc).__name__ == "JournalPending":
            return ("pending", exc)
        return ("error", f"{type(exc).__name__}: {exc}")


def refused(result, code, marker):
    return result[0] == "refusal" and result[1] == code and marker in result[2]


def failing_replace(target):
    """A replace_bytes stand-in raising OSError for `target` only; returns (wrapper, error)."""
    real = harness_merge.replace_bytes
    error = OSError(5, "injected replace failure", target)

    def wrapper(path, data):
        if os.path.realpath(path) == os.path.realpath(target):
            raise error
        return real(path, data)
    return wrapper, error


def acquire_hook(lock_path, mutate):
    """An acquire stand-in that runs `mutate` on its first call for lock_path, then delegates
    to the real acquire. Returns (wrapper, fired)."""
    real = harness_merge.acquire
    fired = []

    def wrapper(path, timeout=None):
        if not fired and os.path.realpath(path) == os.path.realpath(lock_path):
            fired.append(path)
            mutate()
        return real(path, timeout)
    return wrapper, fired


def appending(seen=None, extra=MINE):
    def transform(base):
        if seen is not None:
            seen.append(base)
        return (base or b"") + extra
    return transform


def run_case(fn):
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - a case that raises is one FAIL line
        check(f"{fn.__name__}: runs to completion", False, f"{type(exc).__name__}: {exc}")


# ---- API surface ---------------------------------------------------------------------------

def case_api_surface():
    check("api: JOURNAL_SUFFIX names the per-primary journal",
          harness_merge.JOURNAL_SUFFIX == SUFFIX, repr(harness_merge.JOURNAL_SUFFIX))
    cause = OSError("disk full")
    exc = harness_merge.JournalPending("/x/plan.yaml" + SUFFIX, cause)
    check("api: JournalPending stores journal, cause, replay defaulting false",
          (exc.journal, exc.cause, exc.replay) == ("/x/plan.yaml" + SUFFIX, cause, False))
    check("api: JournalPending message is '<cause type>: <cause>'",
          str(exc) == "OSError: disk full", str(exc))
    replay = harness_merge.JournalPending("j", cause, replay=True)
    check("api: JournalPending carries replay=True", replay.replay is True)


# ---- locked_pair_update --------------------------------------------------------------------

def case_pair_success():
    d, plan, ledger = pair_dir(P0, None)
    seen = []
    harness_merge.locked_pair_update(plan, lambda b: seen.append(b) or P1,
                                     ledger, lambda b: seen.append(b) or S1)
    check("pair: transforms receive both bases (None for an absent secondary)",
          seen == [P0, None], repr(seen))
    check("pair: success writes both images, no journal and no temp file",
          snapshot(d) == {LEDGER: S1, PLAN: P1}, repr(snapshot(d)))


def _refuse(base):
    raise harness_merge.MergeRefusal(7, ["refused by transform"])


def _explode(base):
    raise ValueError("transform blew up")


def case_pair_transform_failure():
    for label, primary_t, secondary_t, expect in (
            ("primary refusal", _refuse, appending(), ("refusal", 7)),
            ("secondary refusal", appending(), _refuse, ("refusal", 7)),
            ("secondary ValueError", appending(), _explode, ("error",))):
        d, plan, ledger = pair_dir(P0, S0)
        result = outcome(harness_merge.locked_pair_update, plan, primary_t, ledger, secondary_t)
        check(f"pair: {label} propagates unchanged", result[:len(expect)] == expect, repr(result))
        check(f"pair: {label} leaves both files byte-identical and no journal",
              snapshot(d) == {LEDGER: S0, PLAN: P0}, repr(snapshot(d)))


def case_pair_secondary_locked():
    d, plan, ledger = pair_dir(P0, S0)
    holder = os.open(ledger + ".lock", os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = outcome(harness_merge.locked_pair_update, plan, appending(), ledger,
                         appending(), timeout=0.2)
    finally:
        os.close(holder)
    check("pair: a held secondary lock refuses with code 6 naming LOCKED",
          refused(result, 6, "LOCKED"), repr(result))
    check("pair: the LOCKED refusal writes nothing",
          snapshot(d) == {LEDGER: S0, PLAN: P0}, repr(snapshot(d)))


def case_pair_two_directories():
    d1, plan, _ = pair_dir(P0, S0)
    _, _, other_ledger = pair_dir(P0, S0)
    result = outcome(harness_merge.locked_pair_update, plan, appending(), other_ledger, appending())
    check("pair: members in two directories raise ValueError",
          result[0] == "error" and result[1].startswith("ValueError"), repr(result))
    same = outcome(harness_merge.locked_pair_update, plan, appending(), plan, appending())
    check("pair: the same file twice raises ValueError",
          same[0] == "error" and same[1].startswith("ValueError"), repr(same))
    check("pair: a ValueError writes nothing", snapshot(d1) == {LEDGER: S0, PLAN: P0})


def check_journal_record(d):
    record = json.loads(read(os.path.join(d, PLAN + SUFFIX)))
    members = record.get("members") or []
    check("pending: the journal is schema harness-merge-journal/1, members primary then secondary",
          record.get("schema") == SCHEMA and [m.get("name") for m in members] == [PLAN, LEDGER],
          repr(record))
    check("pending: the journal records before/after hashes and the after images",
          [(m["before_sha256"], m["after_sha256"], base64.b64decode(m["after_b64"]))
           for m in members] == [(sha(P0), sha(P1), P1), (sha(S0), sha(S1), S1)])


def case_pair_pending_after_publish():
    d, plan, ledger = pair_dir(P0, S0)
    wrapper, error = failing_replace(ledger)
    with patch.object(harness_merge, "replace_bytes", wrapper):
        result = outcome(harness_merge.locked_pair_update, plan, lambda b: P1, ledger, lambda b: S1)
    exc = result[1] if result[0] == "pending" else None
    check("pending: a secondary replace failure raises JournalPending", exc is not None, repr(result))
    check("pending: journal attribute is the primary plus JOURNAL_SUFFIX, cause the OSError, "
          "replay false", exc is not None and (exc.journal, exc.cause, exc.replay, exc.__cause__)
          == (plan + SUFFIX, error, False, error), repr(exc and vars(exc)))
    check("pending: primary at after, secondary at before, journal present",
          snapshot(d) == {LEDGER: S0, PLAN: P1, PLAN + SUFFIX: read(plan + SUFFIX)}
          and read(plan + SUFFIX) is not None, repr(snapshot(d)))
    check_journal_record(d)
    check("pending: recover_journals(primary) rolls forward", harness_merge.recover_journals(plan))
    check("pending: both files converge to after and the journal is gone",
          snapshot(d) == {LEDGER: S1, PLAN: P1}, repr(snapshot(d)))


# ---- recovery from constructed torn states -------------------------------------------------

def _route_recover(d, plan, ledger):
    ok = harness_merge.recover_journals(plan)
    check("torn: recover_journals(primary) returns True", ok is True, repr(ok))
    return {LEDGER: S1, PLAN: P1}


def _route_update_primary(d, plan, ledger):
    seen = []
    harness_merge.locked_update(plan, appending(seen))
    check("torn: locked_update(primary) transform sees the after image", seen == [P1], repr(seen))
    return {LEDGER: S1, PLAN: P1 + MINE}


def _route_update_secondary(d, plan, ledger):
    seen = []
    harness_merge.locked_update(ledger, appending(seen))
    check("torn: locked_update(secondary) transform sees the after image", seen == [S1], repr(seen))
    return {LEDGER: S1 + MINE, PLAN: P1}


TORN_STATES = (("primary at after", P1, S0), ("secondary at after", P0, S1),
               ("both at after", P1, S1))
ROUTES = (("recover_journals(primary)", _route_recover),
          ("locked_update(primary)", _route_update_primary),
          ("locked_update(secondary)", _route_update_secondary))


def case_torn_states_converge():
    for state, plan_bytes, ledger_bytes in TORN_STATES:
        for route, fn in ROUTES:
            d, plan, ledger = pair_dir(plan_bytes, ledger_bytes, J1)
            expected = fn(d, plan, ledger)
            check(f"torn [{state}] via {route}: converges, journal removed",
                  snapshot(d) == expected, repr(snapshot(d)))
            again = harness_merge.recover_journals(plan)
            check(f"torn [{state}] via {route}: a second recover_journals is False, no byte "
                  "changes", again is False and snapshot(d) == expected, repr(again))


# ---- refusals ------------------------------------------------------------------------------

def _diverged_ops(plan, ledger):
    calls = []
    return calls, (
        ("recover_journals(primary)", lambda: harness_merge.recover_journals(plan)),
        ("recover_journals(secondary)", lambda: harness_merge.recover_journals(ledger)),
        ("locked_update(primary)", lambda: harness_merge.locked_update(plan, appending(calls))),
        ("locked_update(secondary)", lambda: harness_merge.locked_update(ledger, appending(calls))))


def case_diverged_member():
    d, plan, ledger = pair_dir(P0, b"third content\n", J1)
    before = snapshot(d)
    calls, ops = _diverged_ops(plan, ledger)
    for label, op in ops:
        result = outcome(op)
        check(f"diverged: {label} refuses with code 5 naming JOURNAL DIVERGED",
              refused(result, 5, "JOURNAL DIVERGED"), repr(result))
        check(f"diverged: {label} leaves both files and the journal byte-identical",
              snapshot(d) == before, repr(snapshot(d)))
    check("diverged: no caller transform ran", calls == [], repr(calls))
    third = os.path.join(d, "notes.txt")
    result = outcome(harness_merge.locked_update, third, lambda b: b"unrelated\n")
    check("diverged: locked_update on a third file in the directory succeeds",
          result == ("ok", None), repr(result))
    check("diverged: the third write leaves both members and the journal byte-identical",
          snapshot(d) == dict(before, **{"notes.txt": b"unrelated\n"}), repr(snapshot(d)))


def case_truncated_journal():
    d, plan, ledger = pair_dir(P0, S0)
    whole = journal_bytes(J1)
    write(plan + SUFFIX, whole[: len(whole) // 2])
    before = snapshot(d)
    result = outcome(harness_merge.recover_journals, plan)
    check("unreadable: a truncated journal refuses with code 5 naming JOURNAL UNREADABLE",
          refused(result, 5, "JOURNAL UNREADABLE"), repr(result))
    third = outcome(harness_merge.locked_update, os.path.join(d, "notes.txt"), appending())
    check("unreadable: it fails closed for a third file in the directory too",
          refused(third, 5, "JOURNAL UNREADABLE"), repr(third))
    check("unreadable: nothing is written", snapshot(d) == before, repr(snapshot(d)))


def case_malformed_membership():
    for label, members in (
            ("a journal listing the primary twice", [(PLAN, P0, P1), (PLAN, P0, P2)]),
            ("a journal whose first member is not its primary", [(LEDGER, S0, S1), (PLAN, P0, P1)])):
        d, plan, ledger = pair_dir(P0, S0)
        write(plan + SUFFIX, journal_bytes(members))
        before = snapshot(d)
        result = outcome(harness_merge.recover_journals, plan, timeout=0.2)
        check(f"unreadable: {label} refuses with code 5 naming JOURNAL UNREADABLE, never LOCKED",
              refused(result, 5, "JOURNAL UNREADABLE"), repr(result))
        check(f"unreadable: {label} writes nothing", snapshot(d) == before, repr(snapshot(d)))


def _malformed(top=None, **member):
    """J1's record with its first member's fields and then its top-level keys overridden."""
    record = json.loads(journal_bytes(J1))
    record["members"][0].update(member)
    record.update(top or {})
    return json.dumps(record).encode("utf-8")


MALFORMED = (
    ("a wrong schema", _malformed({"schema": "harness-merge-journal/2"})),
    ("an empty member list", _malformed({"members": []})),
    ("a member name with a path separator", _malformed(name="sub/plan.yaml")),
    ("a member name '..'", _malformed(name="..")),
    ("an uppercase-hex before_sha256", _malformed(before_sha256=sha(P0).upper())),
    ("an after_b64 that does not hash to after_sha256",
     _malformed(after_b64=base64.b64encode(P2).decode("ascii"))),
    ("an after_b64 that is not base64", _malformed(after_b64="not base64!")),
)


def case_journal_shape_refusals():
    for label, raw in MALFORMED:
        d, plan, _ = pair_dir(P0, S0)
        write(plan + SUFFIX, raw)
        before = snapshot(d)
        result = outcome(harness_merge.recover_journals, plan)
        check(f"unreadable: {label} refuses with code 5 naming JOURNAL UNREADABLE",
              refused(result, 5, "JOURNAL UNREADABLE") and plan + SUFFIX in result[2],
              repr(result))
        check(f"unreadable: {label} writes nothing", snapshot(d) == before, repr(snapshot(d)))


# ---- replay failure ------------------------------------------------------------------------

def _check_replay_pending(label, result, journal, error):
    exc = result[1] if result[0] == "pending" else None
    check(f"replay: {label} raises JournalPending with replay True, that journal and that OSError",
          exc is not None and (exc.replay, exc.journal, exc.cause, exc.__cause__)
          == (True, journal, error, error), repr(result))


def case_replay_failure():
    d, plan, ledger = pair_dir(P0, S0, J1)
    journal = read(plan + SUFFIX)
    calls = []
    wrapper, error = failing_replace(ledger)
    with patch.object(harness_merge, "replace_bytes", wrapper):
        _check_replay_pending("recover_journals(primary)",
                              outcome(harness_merge.recover_journals, plan), plan + SUFFIX, error)
        check("replay: primary at after, secondary at before, journal present",
              snapshot(d) == {LEDGER: S0, PLAN: P1, PLAN + SUFFIX: journal}, repr(snapshot(d)))
        result = outcome(harness_merge.locked_pair_update, plan, appending(calls), ledger,
                         appending(calls))
        _check_replay_pending("locked_pair_update", result, plan + SUFFIX, error)
    check("replay: locked_pair_update called neither transform", calls == [], repr(calls))
    check("replay: the restored replace_bytes converges", harness_merge.recover_journals(plan))
    check("replay: both at after, journal gone", snapshot(d) == {LEDGER: S1, PLAN: P1},
          repr(snapshot(d)))
    check("replay: a second recover_journals returns False",
          harness_merge.recover_journals(plan) is False)


# ---- interleavings -------------------------------------------------------------------------

def _interleave(label, plan, target, mutate):
    wrapper, fired = acquire_hook(plan + ".lock", mutate)
    with patch.object(harness_merge, "acquire", wrapper):
        result = outcome(harness_merge.recover_journals, target)
    check(f"interleave {label}: the wrapper reached the primary's lock first",
          bool(fired), repr(fired))
    return result


def case_interleave_generation_change():
    d, plan, ledger = pair_dir(P0, S0, J1)

    def mutate():
        write(plan, P2)
        write(ledger, S1)
        put_journal(d, [(PLAN, P1, P2), (LEDGER, S1, S2)])
    result = _interleave("(i)", plan, ledger, mutate)
    check("interleave (i): a replaced generation replays without refusal",
          result == ("ok", True), repr(result))
    check("interleave (i): both at J2's after images, no journal",
          snapshot(d) == {LEDGER: S2, PLAN: P2}, repr(snapshot(d)))


def case_interleave_fresh_generation():
    d, plan, ledger = pair_dir(P0, S0, J1)

    def mutate():
        write(plan, P1)
        write(ledger, S1)
        put_journal(d, [(PLAN, P1, P2), (LEDGER, S1, S2)])
    result = _interleave("(ii)", plan, ledger, mutate)
    check("interleave (ii): a fresh generation is replayed, never unlinked unreplayed",
          result == ("ok", True) and snapshot(d) == {LEDGER: S2, PLAN: P2}, repr(snapshot(d)))


def case_interleave_disappearance():
    d, plan, ledger = pair_dir(P0, S0, J1)

    def mutate():
        write(plan, P1)
        write(ledger, S1)
        os.remove(plan + SUFFIX)
    result = _interleave("(iii)", plan, ledger, mutate)
    check("interleave (iii): a vanished journal returns False", result == ("ok", False),
          repr(result))
    check("interleave (iii): no byte changes after the wrapper's",
          snapshot(d) == {LEDGER: S1, PLAN: P1}, repr(snapshot(d)))


def case_interleave_membership_change():
    """(iv), bound to the amendment pair (validate c0 MF-2): every legal generation names
    exactly plan.yaml and feature.json, so a journal can stop naming a file X only by going
    from unreadable (which names every file) to readable. Discovered lock-free as naming X,
    the generation re-read under the primary's lock does not: recover_journals(X) returns
    False and writes nothing."""
    d, plan, _ = pair_dir(P0, S0)
    whole = journal_bytes(J1)
    write(plan + SUFFIX, whole[: len(whole) // 2])
    x = os.path.join(d, "x.txt")
    write(x, b"x0\n")
    after_wrapper = {}

    def mutate():
        put_journal(d, J1)
        after_wrapper.update(snapshot(d))
    result = _interleave("(iv)", plan, x, mutate)
    check("interleave (iv): a generation that no longer names X returns False",
          result == ("ok", False), repr(result))
    check("interleave (iv): plan, ledger, X and J2 stay byte-identical to the wrapper's result",
          snapshot(d) == after_wrapper and PLAN + SUFFIX in after_wrapper, repr(snapshot(d)))


# ---- the journal is bound to the amendment pair (validate c0 MF-2, MF-4) --------------------

BRIEF = "BRIEF.md"
B0, B1 = b"# brief\n", b"# brief, rewritten\n"


def _refused_naming(result, journal):
    return refused(result, 5, "JOURNAL UNREADABLE") and journal in result[2]


def _record_without(key, index):
    """J1's record with `key` deleted from member `index`."""
    record = json.loads(journal_bytes(J1))
    del record["members"][index][key]
    return json.dumps(record).encode("utf-8")


def case_missing_before_key_refuses():
    d, plan, ledger = pair_dir(P0, None)
    write(plan + SUFFIX, _record_without("before_sha256", 1))
    before = snapshot(d)
    result = outcome(harness_merge.recover_journals, plan)
    check("unreadable: a member with no before_sha256 key refuses with code 5 naming the journal "
          "and the key", _refused_naming(result, plan + SUFFIX) and "before_sha256" in result[2],
          repr(result))
    check("unreadable: the missing key never recreates the absent ledger; nothing is written",
          snapshot(d) == before, repr(snapshot(d)))
    d, plan, ledger = pair_dir(P0, None, [(PLAN, P0, P1), (LEDGER, None, S1)])
    result = outcome(harness_merge.recover_journals, plan)
    check("absent: an explicit null before_sha256 still records an absent member, which the "
          "replay creates", result == ("ok", True) and snapshot(d) == {LEDGER: S1, PLAN: P1},
          repr((result, snapshot(d))))


MISBOUND = (
    ("a one-member journal", [(PLAN, P0, P1)]),
    ("a journal binding a sibling in feature.json's place", [(PLAN, P0, P1), (BRIEF, B0, B1)]),
    ("a three-member journal", [(PLAN, P0, P1), (LEDGER, S0, S1), (BRIEF, B0, B1)]),
)


def case_misbound_journal_refuses():
    for label, members in MISBOUND:
        for route, op in (
                ("recover_journals(primary)",
                 lambda plan: harness_merge.recover_journals(plan, timeout=0.2)),
                ("locked_update(primary)",
                 lambda plan: harness_merge.locked_update(plan, appending(), timeout=0.2))):
            d, plan, _ = pair_dir(P0, S0, members)
            write(os.path.join(d, BRIEF), B0)
            before = snapshot(d)
            result = outcome(op, plan)
            check(f"bound: {label} via {route} refuses with code 5 naming JOURNAL UNREADABLE "
                  "and the journal", _refused_naming(result, plan + SUFFIX), repr(result))
            check(f"bound: {label} via {route} writes nothing", snapshot(d) == before,
                  repr(snapshot(d)))


REVERSED_ROUTES = (
    ("locked_update(secondary)",
     lambda plan, ledger: harness_merge.locked_update(ledger, appending(), timeout=0.2)),
    ("recover_journals(primary)",
     lambda plan, ledger: harness_merge.recover_journals(plan, timeout=0.2)),
    ("locked_pair_update", lambda plan, ledger: harness_merge.locked_pair_update(
        plan, appending(), ledger, appending(), timeout=0.2)),
)


def case_reversed_primary_refuses_before_any_lock():
    """A journal with feature.json as its primary would take feature.json.lock before
    plan.yaml.lock — the reversed order no path may take. It refuses before any lock."""
    real = harness_merge.acquire
    for route, op in REVERSED_ROUTES:
        d, plan, ledger = pair_dir(P0, S0, [(LEDGER, S0, S1), (PLAN, P0, P1)])
        before = snapshot(d)
        taken = []

        def wrapper(path, timeout=None):
            taken.append(os.path.basename(path))
            return real(path, timeout)
        with patch.object(harness_merge, "acquire", wrapper):
            result = outcome(op, plan, ledger)
        check(f"bound: a feature.json-primary journal via {route} refuses with code 5 naming "
              "JOURNAL UNREADABLE and the journal", _refused_naming(result, ledger + SUFFIX),
              repr(result))
        check(f"bound: a feature.json-primary journal via {route} refuses before any lock",
              taken == [], repr(taken))
        check(f"bound: a feature.json-primary journal via {route} writes nothing",
              snapshot(d) == before, repr(snapshot(d)))


def case_pair_is_the_amendment_pair():
    for label, swap in (("a sibling in feature.json's place", False), ("the pair reversed", True)):
        d, plan, ledger = pair_dir(P0, S0)
        brief = os.path.join(d, BRIEF)
        write(brief, B0)
        primary, secondary = (ledger, plan) if swap else (plan, brief)
        result = outcome(harness_merge.locked_pair_update, primary, appending(), secondary,
                         appending())
        check(f"pair: {label} raises ValueError", result[0] == "error"
              and result[1].startswith("ValueError"), repr(result))
        check(f"pair: {label} writes nothing and leaves no journal",
              snapshot(d) == {BRIEF: B0, LEDGER: S0, PLAN: P0}, repr(snapshot(d)))


def case_nested_secondary_write_under_the_primary_lock():
    """sign-approval's shape: a feature.json write nested in a locked plan.yaml write."""
    d, plan, ledger = pair_dir(P0, S0)

    def outer(base):
        harness_merge.locked_update(ledger, lambda b: S1, timeout=0.2)
        return P1
    result = outcome(harness_merge.locked_update, plan, outer, timeout=0.2)
    check("bound: a feature.json write nested in a locked plan write succeeds",
          result == ("ok", None) and snapshot(d) == {LEDGER: S1, PLAN: P1},
          repr((result, snapshot(d))))


# ---- a journal entry that is not a regular file (validate c0 MF-3) --------------------------

_PROBE = """
import sys
sys.path.insert(0, {bin_dir!r})
import harness_merge
try:
    {call}
except harness_merge.MergeRefusal as exc:
    print("REFUSED", exc.code, " ".join(exc.lines))
    sys.exit(exc.code)
print("RETURNED")
"""


def _probe(call, timeout=5):
    """`call` in a fresh interpreter, bounded: a hang (a FIFO open, a recovery loop) is a
    'timeout' result rather than a stuck suite. ('exited', code, output) | ('timeout',)."""
    try:
        r = subprocess.run([sys.executable, "-c", _PROBE.format(bin_dir=BIN_DIR, call=call)],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return ("timeout",)
    return ("exited", r.returncode, r.stdout + r.stderr)


def _dangling(journal, d):
    os.symlink(os.path.join(d, "gone"), journal)


def _fifo(journal, d):
    os.mkfifo(journal)


def _linked(journal, d):
    target = os.path.join(tempfile.mkdtemp(), "elsewhere")
    write(target, journal_bytes(J1))
    os.symlink(target, journal)


NON_REGULAR = (
    ("a dangling symlink", _dangling, PLAN + SUFFIX, "locked_update(plan)",
     "harness_merge.locked_update({plan!r}, lambda b: b'x')"),
    ("a symlink to a well-formed journal", _linked, PLAN + SUFFIX, "recover_journals(plan)",
     "harness_merge.recover_journals({plan!r})"),
    ("a FIFO", _fifo, PLAN + SUFFIX, "recover_journals(plan)",
     "harness_merge.recover_journals({plan!r})"),
    ("a FIFO under another journal name", _fifo, "other" + SUFFIX, "locked_update(notes.txt)",
     "harness_merge.locked_update({notes!r}, lambda b: b'x')"),
)


def _entries(d):
    """Each entry's name and lstat mode, lock files aside. Never opens one: a FIFO would block."""
    return {n: os.lstat(os.path.join(d, n)).st_mode for n in os.listdir(d)
            if not n.endswith(".lock")}


def case_non_regular_journal_refuses():
    for label, make, entry, route, call in NON_REGULAR:
        d, plan, _ = pair_dir(P0, S0)
        journal = os.path.join(d, entry)
        make(journal, d)
        before = _entries(d)
        result = _probe(call.format(plan=plan, notes=os.path.join(d, "notes.txt")))
        check(f"entry: {label} via {route} refuses with code 5 naming JOURNAL UNREADABLE and "
              "the journal, never hangs", result[0] == "exited" and result[1] == 5
              and "JOURNAL UNREADABLE" in result[2] and journal in result[2], repr(result))
        check(f"entry: {label} via {route} writes nothing", _entries(d) == before
              and read(plan) == P0 and read(os.path.join(d, LEDGER)) == S0,
              repr(sorted(os.listdir(d))))


# ---- bounded diagnostics -------------------------------------------------------------------

def case_refusal_diagnostics_are_bounded():
    long_bad = "x/" + "A" * 5000
    for label, raw in (
            ("a 5000-character member name", _malformed(name=long_bad)),
            ("a 5000-character misbound member",
             journal_bytes([(PLAN, P0, P1), ("B" * 5000 + "\x1b[31m", B0, B1)]))):
        d, plan, _ = pair_dir(P0, S0)
        write(plan + SUFFIX, raw)
        result = outcome(harness_merge.recover_journals, plan, timeout=0.2)
        check(f"bounded: {label} refuses with code 5 naming the journal",
              _refused_naming(result, plan + SUFFIX), repr(result)[:300])
        check(f"bounded: {label} is echoed truncated and escaped",
              result[0] == "refusal" and "A" * 200 not in result[2] and "B" * 200 not in result[2]
              and "\x1b" not in result[2], repr(result)[:300])


CASES = (
    case_api_surface,
    case_pair_success,
    case_pair_transform_failure,
    case_pair_secondary_locked,
    case_pair_two_directories,
    case_pair_pending_after_publish,
    case_torn_states_converge,
    case_diverged_member,
    case_truncated_journal,
    case_malformed_membership,
    case_journal_shape_refusals,
    case_replay_failure,
    case_interleave_generation_change,
    case_interleave_fresh_generation,
    case_interleave_disappearance,
    case_interleave_membership_change,
    case_missing_before_key_refuses,
    case_misbound_journal_refuses,
    case_reversed_primary_refuses_before_any_lock,
    case_pair_is_the_amendment_pair,
    case_nested_secondary_write_under_the_primary_lock,
    case_non_regular_journal_refuses,
    case_refusal_diagnostics_are_bounded,
)


def main():
    for case in CASES:
        run_case(case)
    failed = [r for r in RESULTS if not r[1]]
    if failed:
        print(f"FAIL - {len(failed)}/{len(RESULTS)} checks failed")
        sys.exit(1)
    print(f"PASS - {len(RESULTS)}/{len(RESULTS)} checks passed")


if __name__ == "__main__":
    main()
