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
import stat
import sys
import tempfile
from unittest.mock import patch

from unit_support import BIN

import harness_merge  # noqa: E402
from check_support import Checks  # noqa: E402

C = Checks()
check = C.check
# One root for every case's own mkdtemp() directory, removed when the run exits.
TMP = tempfile.TemporaryDirectory(prefix="merge-journal-")
SUFFIX = ".harness-merge.journal"
SCHEMA = "harness-merge-journal/1"
PLAN = "plan.yaml"
LEDGER = "feature.json"
P0, P1, P2 = b"plan: base\n", b"plan: amended\n", b"plan: amended again\n"
S0, S1, S2 = b'{"ledger": []}\n', b'{"ledger": ["a"]}\n', b'{"ledger": ["a", "b"]}\n'
MINE = b"# caller's own change\n"


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
    d = tempfile.mkdtemp(dir=TMP.name)
    write(os.path.join(d, PLAN), plan)
    write(os.path.join(d, LEDGER), ledger)
    if members:
        put_journal(d, members)
    return d, os.path.join(d, PLAN), os.path.join(d, LEDGER)


J1 = [(PLAN, P0, P1), (LEDGER, S0, S1)]
TRUNCATED = journal_bytes(J1)[: len(journal_bytes(J1)) // 2]


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


def raised(result, name):
    return result[0] == "error" and result[1].startswith(name + ":")


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


def appending(seen=None):
    def transform(base):
        if seen is not None:
            seen.append(base)
        return (base or b"") + MINE
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
          raised(result, "ValueError"), repr(result))
    same = outcome(harness_merge.locked_pair_update, plan, appending(), plan, appending())
    check("pair: the same file twice raises ValueError",
          raised(same, "ValueError"), repr(same))
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
    journal = read(plan + SUFFIX)
    check("pending: primary at after, secondary at before, journal present",
          snapshot(d) == {LEDGER: S0, PLAN: P1, PLAN + SUFFIX: journal}
          and journal is not None, repr(snapshot(d)))
    check_journal_record(d)
    check("pending: recover_journals(primary) rolls forward", harness_merge.recover_journals(plan))
    check("pending: both files converge to after and the journal is gone",
          snapshot(d) == {LEDGER: S1, PLAN: P1}, repr(snapshot(d)))


# ---- recovery from constructed torn states -------------------------------------------------

def _route_recover(plan, ledger):
    ok = harness_merge.recover_journals(plan)
    check("torn: recover_journals(primary) returns True", ok is True, repr(ok))
    return {LEDGER: S1, PLAN: P1}


def _route_update_primary(plan, ledger):
    seen = []
    harness_merge.locked_update(plan, appending(seen))
    check("torn: locked_update(primary) transform sees the after image", seen == [P1], repr(seen))
    return {LEDGER: S1, PLAN: P1 + MINE}


def _route_update_secondary(plan, ledger):
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
            expected = fn(plan, ledger)
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
    write(plan + SUFFIX, TRUNCATED)
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
    write(plan + SUFFIX, TRUNCATED)
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


def _keyless_via_feature_json(d, plan, ledger, before):
    result = outcome(harness_merge.locked_update, ledger, appending(), timeout=0.2)
    check("unreadable: the missing key via locked_update(feature.json) refuses with code 5 naming "
          "the journal and the key", _refused_naming(result, plan + SUFFIX)
          and "before_sha256" in result[2], repr(result))
    check("unreadable: via locked_update(feature.json) the absent ledger is not recreated; "
          "nothing is written", snapshot(d) == before, repr(snapshot(d)))


def _explicit_null_still_means_absent():
    d, plan, ledger = pair_dir(P0, None, [(PLAN, P0, P1), (LEDGER, None, S1)])
    result = outcome(harness_merge.recover_journals, plan)
    check("absent: an explicit null before_sha256 still records an absent member, which the "
          "replay creates", result == ("ok", True) and snapshot(d) == {LEDGER: S1, PLAN: P1},
          repr((result, snapshot(d))))


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
    _keyless_via_feature_json(d, plan, ledger, before)
    _explicit_null_still_means_absent()


MISBOUND = (
    ("a one-member journal", [(PLAN, P0, P1)]),
    ("a journal binding a sibling in feature.json's place", [(PLAN, P0, P1), (BRIEF, B0, B1)]),
    ("a three-member journal", [(PLAN, P0, P1), (LEDGER, S0, S1), (BRIEF, B0, B1)]),
)
MISBOUND_ROUTES = (
    ("recover_journals(primary)", lambda plan: harness_merge.recover_journals(plan, timeout=0.2)),
    ("locked_update(primary)",
     lambda plan: harness_merge.locked_update(plan, appending(), timeout=0.2)),
)


def case_misbound_journal_refuses():
    for label, members in MISBOUND:
        for route, op in MISBOUND_ROUTES:
            d, plan, _ = pair_dir(P0, S0, members)
            write(os.path.join(d, BRIEF), B0)
            before = snapshot(d)
            result = outcome(op, plan)
            check(f"bound: {label} via {route} refuses with code 5 naming JOURNAL UNREADABLE "
                  "and the journal", _refused_naming(result, plan + SUFFIX), repr(result))
            check(f"bound: {label} via {route} writes nothing", snapshot(d) == before,
                  repr(snapshot(d)))


# ---- discovery is the producer's one name (validate c3 MF-12, remedy (b)) -------------------

# *.harness-merge.journal entries no producer writes: garbage, a well-formed pair record under
# BRIEF.md's name, and the reversed (feature.json-primary) record under feature.json's name —
# the shape that would take feature.json.lock before plan.yaml.lock if it were ever acted on.
FOREIGN = (
    ("garbage evil" + SUFFIX, "evil" + SUFFIX, b"\x00 not a journal\n"),
    ("well-formed " + BRIEF + SUFFIX, BRIEF + SUFFIX, journal_bytes(J1)),
    ("well-formed " + LEDGER + SUFFIX, LEDGER + SUFFIX,
     journal_bytes([(LEDGER, S0, S1), (PLAN, P0, P1)])),
)

# route, op(plan, ledger), the locks it takes in order, the pair it leaves from (P0, S0)
FOREIGN_ROUTES = (
    ("locked_update(plan.yaml)",
     lambda plan, ledger: harness_merge.locked_update(plan, appending(), timeout=0.2),
     [PLAN + ".lock"], {PLAN: P0 + MINE, LEDGER: S0}),
    ("locked_update(feature.json)",
     lambda plan, ledger: harness_merge.locked_update(ledger, appending(), timeout=0.2),
     [LEDGER + ".lock"], {PLAN: P0, LEDGER: S0 + MINE}),
    ("locked_pair_update", lambda plan, ledger: harness_merge.locked_pair_update(
        plan, appending(), ledger, appending(), timeout=0.2),
     [PLAN + ".lock", LEDGER + ".lock"], {PLAN: P0 + MINE, LEDGER: S0 + MINE}),
)


def _taking_locks(taken):
    """An acquire stand-in recording each lock's basename, then delegating."""
    real = harness_merge.acquire

    def wrapper(path, timeout=None):
        taken.append(os.path.basename(path))
        return real(path, timeout)
    return wrapper


def _plant_foreign(d):
    """Every FOREIGN entry written into d; returns {name: bytes}."""
    for _, name, data in FOREIGN:
        write(os.path.join(d, name), data)
    return {name: data for _, name, data in FOREIGN}


def case_foreign_journal_names_are_inert():
    """Each foreign name planted alone: every write route succeeds, writes its change on the
    bases (nothing replayed), takes only its own locks in the one order, and leaves the foreign
    file byte-identical with no journal of its own left behind."""
    for label, name, data in FOREIGN:
        for route, op, locks, after in FOREIGN_ROUTES:
            d, plan, ledger = pair_dir(P0, S0)
            write(os.path.join(d, name), data)
            taken = []
            with patch.object(harness_merge, "acquire", _taking_locks(taken)):
                result = outcome(op, plan, ledger)
            check(f"foreign: {label} via {route} succeeds, writes, foreign file untouched",
                  result == ("ok", None) and snapshot(d) == dict(after, **{name: data}),
                  repr((result, snapshot(d))))
            check(f"foreign: {label} via {route} takes only {locks}", taken == locks, repr(taken))


def case_recovery_with_only_foreign_journals_is_false():
    d, plan, ledger = pair_dir(P0, S0)
    _plant_foreign(d)
    before = snapshot(d)
    for target in (plan, ledger, os.path.join(d, "notes.txt")):
        result = outcome(harness_merge.recover_journals, target, timeout=0.2)
        check(f"foreign: recover_journals({os.path.basename(target)}) with only foreign journals "
              "returns False", result == ("ok", False), repr(result))
    check("foreign: recover_journals changes no byte", snapshot(d) == before, repr(snapshot(d)))


def case_the_real_journal_recovers_beside_foreign_ones():
    for state, plan_bytes, ledger_bytes in TORN_STATES:
        for route, fn in ROUTES:
            d, plan, ledger = pair_dir(plan_bytes, ledger_bytes, J1)
            foreign = _plant_foreign(d)
            expected = fn(plan, ledger)
            check(f"foreign: torn [{state}] via {route} beside every foreign journal converges, "
                  "the real journal removed, the foreign files untouched",
                  snapshot(d) == dict(expected, **foreign), repr(snapshot(d)))


def _notes_update(plan, ledger):
    return harness_merge.locked_update(os.path.join(os.path.dirname(plan), "notes.txt"),
                                       appending(), timeout=0.2)


def case_an_unreadable_real_journal_still_refuses():
    """Fail closed is kept for the one real name: a truncated plan.yaml journal beside every
    foreign one refuses exit 5 naming the REAL journal, for the pair's routes and a third file."""
    d, plan, ledger = pair_dir(P0, S0)
    write(plan + SUFFIX, TRUNCATED)
    _plant_foreign(d)
    before = snapshot(d)
    routes = [(route, op) for route, op, _, _ in FOREIGN_ROUTES]
    for route, op in routes + [("locked_update(notes.txt)", _notes_update)]:
        result = outcome(op, plan, ledger)
        check(f"foreign: an unreadable real journal via {route} refuses with code 5 naming it",
              _refused_naming(result, plan + SUFFIX), repr(result))
    check("foreign: the unreadable real journal's refusals write nothing", snapshot(d) == before,
          repr(snapshot(d)))


def _folds_case(d):
    """True when d's filesystem folds case (APFS and HFS+ by default)."""
    probe = os.path.join(d, "case-probe")
    write(probe, b"")
    try:
        return os.path.exists(os.path.join(d, "CASE-PROBE"))
    finally:
        os.remove(probe)


def _variant_planting(variant):
    def transform(base):
        write(variant, b"variant\n")
        return P1
    return transform


def case_the_producers_name_as_the_filesystem_resolves_it():
    """A case variant of the real name appearing inside the lock window. Where the filesystem
    folds case, the producer's os.replace lands on it and keeps the variant's spelling, so the
    pending journal is LISTED as Plan.yaml.harness-merge.journal: discovery must ask the
    filesystem for the producer's one path, never compare listed spellings, or a torn pair
    goes silent. Where case is significant the variant is foreign and inert."""
    d, plan, ledger = pair_dir(P0, S0)
    variant = os.path.join(d, "Plan.yaml" + SUFFIX)
    folds = _folds_case(d)
    wrapper, _ = failing_replace(ledger)
    with patch.object(harness_merge, "replace_bytes", wrapper):
        result = outcome(harness_merge.locked_pair_update, plan, _variant_planting(variant),
                         ledger, lambda b: S1)
    listed = sorted(n for n in os.listdir(d) if n.endswith(SUFFIX))
    check(f"case: the pair is pending under the {'variant' if folds else 'real'} spelling "
          f"(folds case: {folds})", result[0] == "pending" and listed == (
              ["Plan.yaml" + SUFFIX] if folds else ["Plan.yaml" + SUFFIX, PLAN + SUFFIX]),
          repr((result, listed)))
    recovered = outcome(harness_merge.recover_journals, ledger, timeout=0.2)
    check("case: recover_journals rolls the pending pair forward",
          recovered == ("ok", True) and snapshot(d) == dict(
              {LEDGER: S1, PLAN: P1}, **({} if folds else {"Plan.yaml" + SUFFIX: b"variant\n"})),
          repr((recovered, snapshot(d))))


def case_pair_is_the_amendment_pair():
    for label, swap in (("a sibling in feature.json's place", False), ("the pair reversed", True)):
        d, plan, ledger = pair_dir(P0, S0)
        brief = os.path.join(d, BRIEF)
        write(brief, B0)
        primary, secondary = (ledger, plan) if swap else (plan, brief)
        result = outcome(harness_merge.locked_pair_update, primary, appending(), secondary,
                         appending())
        check(f"pair: {label} raises ValueError", raised(result, "ValueError"), repr(result))
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
        r = subprocess.run([sys.executable, "-c", _PROBE.format(bin_dir=str(BIN), call=call)],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return ("timeout",)
    return ("exited", r.returncode, r.stdout + r.stderr)


def _dangling(journal):
    os.symlink(os.path.join(os.path.dirname(journal), "gone"), journal)


def _fifo(journal):
    os.mkfifo(journal)


def _linked(journal):
    target = os.path.join(tempfile.mkdtemp(dir=TMP.name), "elsewhere")
    write(target, journal_bytes(J1))
    os.symlink(target, journal)


def _directory(journal):
    os.mkdir(journal)


_LOCKED_UPDATE = "harness_merge.locked_update({target!r}, lambda b: b'x')"
_RECOVER = "harness_merge.recover_journals({target!r})"

NON_REGULAR = (
    ("a dangling symlink", _dangling, "locked_update(plan)", _LOCKED_UPDATE, PLAN),
    ("a dangling symlink", _dangling, "locked_update(feature.json)", _LOCKED_UPDATE, LEDGER),
    ("a symlink to a well-formed journal", _linked, "recover_journals(plan)", _RECOVER, PLAN),
    ("a FIFO", _fifo, "recover_journals(plan)", _RECOVER, PLAN),
    ("a directory", _directory, "locked_update(plan)", _LOCKED_UPDATE, PLAN),
    ("a directory", _directory, "locked_update(feature.json)", _LOCKED_UPDATE, LEDGER),
    ("a directory", _directory, "recover_journals(plan)", _RECOVER, PLAN),
    ("a directory", _directory, "recover_journals(feature.json)", _RECOVER, LEDGER),
)


def _entries(d):
    """Each entry's name and lstat mode, lock files aside. Never opens one: a FIFO would block."""
    return {n: os.lstat(os.path.join(d, n)).st_mode for n in os.listdir(d)
            if not n.endswith(".lock")}


def case_non_regular_journal_refuses():
    for label, make, route, call, target in NON_REGULAR:
        d, plan, _ = pair_dir(P0, S0)
        journal = plan + SUFFIX
        make(journal)
        before = _entries(d)
        result = _probe(call.format(target=os.path.join(d, target)))
        check(f"entry: {label} via {route} refuses with code 5 naming JOURNAL UNREADABLE and "
              "the journal, never hangs", result[0] == "exited" and result[1] == 5
              and "JOURNAL UNREADABLE" in result[2] and journal in result[2], repr(result))
        check(f"entry: {label} via {route} writes nothing", _entries(d) == before
              and read(plan) == P0 and read(os.path.join(d, LEDGER)) == S0,
              repr(sorted(os.listdir(d))))


def case_a_foreign_fifo_is_never_opened():
    """validate c3 MF-12: a FIFO under a name no producer writes is never discovered, so it is
    never opened (no hang) and never refuses: the write returns and the FIFO stays a FIFO."""
    for route, target in (("locked_update(notes.txt)", "notes.txt"), ("locked_update(plan)", PLAN)):
        d, plan, _ = pair_dir(P0, S0)
        fifo = os.path.join(d, "other" + SUFFIX)
        os.mkfifo(fifo)
        result = _probe(_LOCKED_UPDATE.format(target=os.path.join(d, target)))
        check(f"foreign: a FIFO under another journal name via {route} returns, never hangs",
              result[0] == "exited" and result[1] == 0 and "RETURNED" in result[2], repr(result))
        check(f"foreign: via {route} the write lands and the FIFO is left in place",
              read(os.path.join(d, target)) == b"x" and stat.S_ISFIFO(os.lstat(fifo).st_mode),
              repr(sorted(os.listdir(d))))


def _buffered_fifo(path, data):
    """A FIFO at `path` already holding `data`, written and its writer closed. Returns the
    held-open reader descriptor that keeps the buffered bytes alive; the caller closes it."""
    os.mkfifo(path)
    keeper = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    writer = os.open(path, os.O_WRONLY | os.O_NONBLOCK)
    try:
        os.write(writer, data)
    finally:
        os.close(writer)
    return keeper


def _swap_before_open(journal, replacement, nth):
    """An os.open stand-in that renames `replacement` over `journal` just before the nth open
    of `journal` — the read under the primary's lock, after every lstat _require_regular made
    — then delegates. Returns (wrapper, swapped)."""
    real = os.open
    opens, swapped = [], []

    def wrapper(path, flags, *args, **kwargs):
        if os.fspath(path) == journal:
            opens.append(path)
            if len(opens) == nth:
                os.replace(replacement, journal)
                swapped.append(path)
        return real(path, flags, *args, **kwargs)
    return wrapper, swapped


# (route, op, which open of the journal is the read under plan.yaml.lock): recover_journals
# on the primary never reads in discovery (the name says it all); a feature.json write reads
# once in lock-free discovery, then again under the lock.
FIFO_SWAP_ROUTES = (
    ("recover_journals(plan)", lambda plan, ledger: harness_merge.recover_journals(plan), 1),
    ("locked_update(feature.json)",
     lambda plan, ledger: harness_merge.locked_update(ledger, appending(), timeout=0.2), 2),
)


def _fifo_swap_outcome(op, nth, record):
    """Run `op` with a FIFO holding `record` renamed over the journal after its lstat; returns
    (plan, ledger, journal, result, swapped, unread, entries)."""
    d, plan, ledger = pair_dir(P0, S0, J1)
    journal = plan + SUFFIX
    keeper = _buffered_fifo(os.path.join(d, "swap.fifo"), record)
    try:
        wrapper, swapped = _swap_before_open(journal, os.path.join(d, "swap.fifo"), nth)
        with patch.object(os, "open", wrapper):
            result = outcome(op, plan, ledger)
        unread = os.read(keeper, len(record) + 1)
    finally:
        os.close(keeper)
    return plan, ledger, journal, result, swapped, unread, sorted(os.listdir(d))


def case_fifo_swapped_after_lstat_refuses():
    """validate c1 MF-8: the entry is a regular file when _require_regular lstats it, then a
    FIFO already holding a well-formed J1 record is renamed over it before the read under the
    primary's lock. The opened descriptor is not a regular file, so the read refuses
    UNREADABLE naming the journal before reading a byte: no member is replayed, the FIFO is
    left in place and its buffered record is still unread."""
    record = journal_bytes(J1)
    for route, op, nth in FIFO_SWAP_ROUTES:
        plan, ledger, journal, result, swapped, unread, entries = _fifo_swap_outcome(op, nth, record)
        check(f"fifo swap via {route}: the swap happened after the lstat, before the open",
              swapped == [journal], repr(swapped))
        check(f"fifo swap via {route}: refuses with code 5 naming JOURNAL UNREADABLE and the "
              "journal", _refused_naming(result, journal), repr(result))
        check(f"fifo swap via {route}: both members untouched",
              (read(plan), read(ledger)) == (P0, S0), repr((read(plan), read(ledger))))
        check(f"fifo swap via {route}: the FIFO is left in place, its record unread",
              os.path.lexists(journal) and stat.S_ISFIFO(os.lstat(journal).st_mode)
              and unread == record, repr((entries, len(unread))))


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
    case_foreign_journal_names_are_inert,
    case_recovery_with_only_foreign_journals_is_false,
    case_the_real_journal_recovers_beside_foreign_ones,
    case_an_unreadable_real_journal_still_refuses,
    case_the_producers_name_as_the_filesystem_resolves_it,
    case_pair_is_the_amendment_pair,
    case_nested_secondary_write_under_the_primary_lock,
    case_non_regular_journal_refuses,
    case_a_foreign_fifo_is_never_opened,
    case_fifo_swapped_after_lstat_refuses,
    case_refusal_diagnostics_are_bounded,
)


def main():
    for case in CASES:
        run_case(case)
    sys.exit(C.report())


if __name__ == "__main__":
    main()
