#!/usr/bin/env python3
"""test-harness-merge.py — house-shape suite for harness_merge.py (FEAT-32 T-02).

Resolves the module under test via HARNESS_MERGE_DIR so a mutated copy of the tree can be
swapped in without editing this file (see the task's verify: block, which does exactly that).
Every case runs in a fresh tempfile.mkdtemp() and never touches a real .harness path.
"""
from integration_support import BIN
import json
import os
import re
import signal
import sys
import tempfile
import time
from unittest import mock

sys.path.insert(0, os.environ.get("HARNESS_MERGE_DIR") or str(BIN))

import harness_merge  # noqa: E402
from check_support import Checks, raises  # noqa: E402

C = Checks()
check = C.check


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


def _wait_for(path, seconds=2):
    deadline = time.time() + seconds
    while not os.path.exists(path) and time.time() < deadline:
        time.sleep(0.02)


def case_1_create_from_missing():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "f.txt")

    def transform(base):
        check("case1: transform receives None for missing file", base is None, repr(base))
        return b"created-content"

    harness_merge.locked_update(path, transform)
    with open(path, "rb") as fh:
        data = fh.read()
    check("case1: file created with transform output", data == b"created-content", repr(data))


def case_2_apply_to_existing():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "f.txt")
    with open(path, "wb") as fh:
        fh.write(b"original")

    def transform(base):
        check("case2: transform receives original bytes", base == b"original", repr(base))
        return b"replaced-exactly-this"

    harness_merge.locked_update(path, transform)
    with open(path, "rb") as fh:
        data = fh.read()
    check("case2: result is exactly transform's bytes", data == b"replaced-exactly-this", repr(data))


def case_3_refusal_leaves_byte_identical():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "f.txt")
    original = b"untouched-original-bytes"
    with open(path, "wb") as fh:
        fh.write(original)

    def transform(base):
        raise harness_merge.MergeRefusal(7, ["refused: conflict"])

    raised = False
    try:
        harness_merge.locked_update(path, transform)
    except harness_merge.MergeRefusal:
        raised = True
    check("case3: MergeRefusal propagated", raised)

    with open(path, "rb") as fh:
        data = fh.read()
    check("case3: file byte-identical to before", data == original, repr(data))

    leftovers = [
        n for n in os.listdir(d)
        if n != "f.txt" and n != "f.txt.lock"
    ]
    check("case3: no tempfile left behind", leftovers == [], repr(leftovers))


def case_4_stale_lock():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "f.txt")
    with open(path, "wb") as fh:
        fh.write(b"before-stale-lock")
    lock_path = path + ".lock"
    ready_path = os.path.join(d, "ready")

    pid = os.fork()
    if pid == 0:
        # child: acquire the lock and then block forever
        try:
            with harness_merge.acquire(lock_path):
                with open(ready_path, "w") as fh:
                    fh.write("ready")
                while True:
                    time.sleep(1)
        except Exception:
            pass
        os._exit(1)

    # wait until the child really holds the lock before killing it
    _wait_for(ready_path)
    os.kill(pid, signal.SIGKILL)
    os.waitpid(pid, 0)

    def transform(base):
        return b"applied-after-stale-lock"

    err = raises(lambda: harness_merge.locked_update(path, transform), Exception)
    returned = check("case4: locked_update returned normally after stale lock killed",
                     err is None, f"raised {err!r} instead of returning normally")
    data = _read(path) if returned else None
    check("case4: transform output is on disk", data == b"applied-after-stale-lock",
          repr(data) if returned else "locked_update did not return")


def _contend(path, tag, results_path):
    """Child body: append tag under the lock and record "ok" or "refusal:<code>"."""
    def transform(base):
        time.sleep(0.02)
        base = base or b""
        return base + tag.encode() + b"\n"

    try:
        harness_merge.locked_update(path, transform)
        outcome = b"ok"
    except harness_merge.MergeRefusal as exc:
        outcome = f"refusal:{exc.code}".encode()
    with open(results_path, "wb") as rf:
        rf.write(outcome)


def _contention_trial():
    """(res1, res2, content) for one A-versus-B race on a fresh empty file."""
    d = tempfile.mkdtemp()
    path = os.path.join(d, "f.txt")
    with open(path, "wb") as fh:
        fh.write(b"")
    # Start both children before waiting on either, so they contend for the lock.
    result_paths = [os.path.join(d, "r1"), os.path.join(d, "r2")]
    pids = []
    for tag, results_path in zip("AB", result_paths):
        pid = os.fork()
        if pid == 0:
            _contend(path, tag, results_path)
            os._exit(0)
        pids.append(pid)
    for pid in pids:
        os.waitpid(pid, 0)
    res1, res2 = (_read(p).decode() for p in result_paths)
    return res1, res2, _read(path)


def _legal_outcome(res1, res2, content):
    both_lines = b"A\n" in content and b"B\n" in content
    one_refused = (
        (res1 == "ok" and res2.startswith("refusal:6"))
        or (res2 == "ok" and res1.startswith("refusal:6"))
    )
    if res1 == "ok" and res2 == "ok" and both_lines:
        return True
    if one_refused:
        # the refused side must have applied nothing: content is exactly the
        # winner's single line
        winner_line = b"A\n" if res1 == "ok" else b"B\n"
        return content == winner_line
    return False


def case_5_contention():
    trials = 20
    third_outcomes = []
    for trial in range(trials):
        res1, res2, content = _contention_trial()
        if not _legal_outcome(res1, res2, content):
            third_outcomes.append((trial, res1, res2, content))

    check(
        "case5: contention admits only the two legal outcomes over 20 trials",
        third_outcomes == [],
        f"illegal outcomes: {third_outcomes}",
    )


def _torn_read_reader(path, short_body, long_body, reader_out, duration):
    """Child body: read path in a loop for duration seconds and record what it saw as JSON."""
    bad = []
    reads = 0
    saw_short = False
    saw_long = False
    deadline = time.time() + duration
    while time.time() < deadline:
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except FileNotFoundError:
            continue
        reads += 1
        if data == short_body:
            saw_short = True
        elif data == long_body:
            saw_long = True
        else:
            bad.append(len(data))
    with open(reader_out, "w") as fh:
        json.dump({"bad": bad, "reads": reads, "saw_short": saw_short, "saw_long": saw_long}, fh)


def _alternate_writes(path, bodies, duration):
    # Alternate between two clearly different legal bodies for the whole duration, instead of a
    # single replace, so the reader races MANY replace windows rather than one microsecond-wide
    # one: a non-atomic write regresses this from near-certain detection to a single-shot coin
    # flip. Writing the same body twice in a row (the loop's first iteration) is still a real
    # replace onto disk and still a legitimate torn-read opportunity, so it is not skipped.
    i = 0
    deadline = time.time() + duration
    while time.time() < deadline:
        body = bodies[i % 2]
        i += 1

        def transform(base, body=body):
            return body

        harness_merge.locked_update(path, transform)


def case_6_no_torn_read():
    d = tempfile.mkdtemp()
    path = os.path.join(d, "f.txt")
    short_body = b"old" * 1000
    long_body = b"NEW" * 100000
    with open(path, "wb") as fh:
        fh.write(short_body)

    reader_out = os.path.join(d, "reader_out")
    duration = 3

    reader_pid = os.fork()
    if reader_pid == 0:
        _torn_read_reader(path, short_body, long_body, reader_out, duration)
        os._exit(0)

    _alternate_writes(path, [short_body, long_body], duration)
    os.waitpid(reader_pid, 0)

    with open(reader_out) as fh:
        r = json.load(fh)

    check("case6: no torn read observed by concurrent reader", r["bad"] == [], r["bad"])
    check("case6: reader observed at least one read", r["reads"] > 0, r["reads"])
    check(
        "case6: reader observed both the short and long body while racing the writer",
        r["saw_short"] and r["saw_long"],
        (r["saw_short"], r["saw_long"]),
    )


def _refusal_code(path, tail):
    """None when require_destination accepts path, else the MergeRefusal code."""
    err = raises(lambda: harness_merge.require_destination(path, tail, "the thing", ["hint"]),
                 harness_merge.MergeRefusal)
    return None if err is None else err.code


def case_7_require_destination():
    tail = re.compile(r"(?:^|/)mydir/(myfile-[a-z]+)\.md$")

    d = tempfile.mkdtemp()
    subdir = os.path.join(d, "mydir")
    os.makedirs(subdir)
    good_path = os.path.join(subdir, "myfile-abc.md")

    check("case7: matching resolved path is accepted", _refusal_code(good_path, tail) is None)

    bad_path = os.path.join(d, "otherdir", "myfile-abc.md")
    check("case7: non-matching path raises MergeRefusal(9)", _refusal_code(bad_path, tail) == 9)

    # Symlink escape: the literal argument's STRING ends in a matching tail, but the realpath it
    # resolves to does not. No purely-`..` literal can pin this: textually walking `..` collapses
    # to a path whose resolved form and literal form agree (or both fail to match), so the
    # property "the match is on the realpath, never the argument" needs a symlink to force a
    # divergence between the two. `mydir` is a real symlink pointing at `outside/`; the literal
    # path walks through it and ends in "mydir/myfile-zzz.md" (matches the tail regex verbatim),
    # but os.path.realpath resolves the symlink and the result is "outside/myfile-zzz.md", which
    # has no "mydir/" segment and does not match. An implementation that matches tail_regex
    # against `path` instead of `resolved` (line 152) accepts this; the correct one refuses it.
    outside_dir = os.path.join(d, "outside")
    os.makedirs(outside_dir)
    link_holder = os.path.join(d, "linkholder")
    os.makedirs(link_holder)
    mydir_link = os.path.join(link_holder, "mydir")
    os.symlink(outside_dir, mydir_link)
    symlink_literal = os.path.join(link_holder, "mydir", "myfile-zzz.md")
    check(
        "case7: symlink escape (literal ends in matching tail via symlinked 'mydir', "
        "realpath resolves outside and does not match) raises MergeRefusal(9)",
        _refusal_code(symlink_literal, tail) == 9,
    )


def case_8_acquire_live_holder():
    d = tempfile.mkdtemp()
    lock_path = os.path.join(d, "held.lock")

    ready_path = os.path.join(d, "ready")

    pid = os.fork()
    if pid == 0:
        with harness_merge.acquire(lock_path):
            with open(ready_path, "w") as fh:
                fh.write("ready")
            time.sleep(3)
        os._exit(0)

    _wait_for(ready_path)

    raised_code = None
    lines = []
    try:
        with mock.patch.object(harness_merge, "LOCK_TIMEOUT_SECONDS", 0.3), \
                mock.patch.object(harness_merge, "LOCK_RETRY_INTERVAL", 0.02):
            with harness_merge.acquire(lock_path):
                pass
    except harness_merge.MergeRefusal as exc:
        raised_code = exc.code
        lines = exc.lines
    finally:
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)

    check("case8: acquire raises MergeRefusal(6) against a live holder", raised_code == 6, raised_code)
    names_path = any(lock_path in line for line in lines)
    check("case8: refusal lines name the lock path", names_path, lines)


def _refusal_under(lock_path, env_value, **kwargs):
    """(code, lines, seconds) for one acquire against a held lock with the override set."""
    with mock.patch.dict(os.environ, {harness_merge.LOCK_TIMEOUT_ENV: env_value}):
        start = time.monotonic()
        try:
            with harness_merge.acquire(lock_path, **kwargs):
                return None, [], time.monotonic() - start
        except harness_merge.MergeRefusal as exc:
            return exc.code, exc.lines, time.monotonic() - start


def _override_error(lock_path, env_value):
    """The error text a default-budget acquire raises with the override set, or None."""
    with mock.patch.dict(os.environ, {harness_merge.LOCK_TIMEOUT_ENV: env_value}):
        try:
            with harness_merge.acquire(lock_path, timeout=None):
                return None
        except ValueError as exc:
            return str(exc)
        except harness_merge.MergeRefusal as exc:
            return f"MergeRefusal {exc.code}"


def case_9_timeout_override_precedence():
    """HARNESS_LOCK_TIMEOUT_SECONDS replaces the DEFAULT budget only: it shortens a refusal
    against a live holder, an explicit `timeout=` still wins over it, and a value that is not a
    positive number is refused loudly rather than read as zero or as the default."""
    import fcntl
    d = tempfile.mkdtemp()
    lock_path = os.path.join(d, "held.lock")
    holder = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    fcntl.flock(holder, fcntl.LOCK_EX)
    try:
        code, lines, took = _refusal_under(lock_path, "0.2")
        check("case9: the override still refuses a live holder with exit 6", code == 6, code)
        check("case9: the refusal names the overridden budget",
              any("within 0.2s" in line for line in lines), lines)
        check("case9: and takes the short budget, not the 10s default", took < 2, took)

        code, lines, took = _refusal_under(lock_path, "30", timeout=0.1)
        check("case9: an explicit timeout= wins over the override",
              code == 6 and any("within 0.1s" in line for line in lines) and took < 2,
              (code, lines, took))

        for bad in ("0", "-1", "soon", "nan", "inf", "1e999"):
            raised = _override_error(lock_path, bad)
            check(f"case9: override {bad!r} is refused loudly, naming the variable",
                  raised is not None and harness_merge.LOCK_TIMEOUT_ENV in raised, raised)
    finally:
        os.close(holder)


def main():
    case_1_create_from_missing()
    case_2_apply_to_existing()
    case_3_refusal_leaves_byte_identical()
    case_4_stale_lock()
    case_5_contention()
    case_6_no_torn_read()
    case_7_require_destination()
    case_8_acquire_live_holder()
    case_9_timeout_override_precedence()
    sys.exit(C.report())


if __name__ == "__main__":
    main()
