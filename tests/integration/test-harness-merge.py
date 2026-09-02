#!/usr/bin/env python3
"""test-harness-merge.py — house-shape suite for harness_merge.py (FEAT-32 T-02).

Resolves the module under test via HARNESS_MERGE_DIR so a mutated copy of the tree can be
swapped in without editing this file (see the task's verify: block, which does exactly that).
Every case runs in a fresh tempfile.mkdtemp() and never touches a real .harness path.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import re
import signal
import sys
import tempfile
import time

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
sys.path.insert(0, os.environ.get("HARNESS_MERGE_DIR") or HERE)

import harness_merge  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(("PASS" if ok else "FAIL") + f" - {name}" + (f" ({detail})" if detail and not ok else ""))


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

    pid = os.fork()
    if pid == 0:
        # child: acquire the lock and then block forever
        try:
            with harness_merge.acquire(lock_path):
                while True:
                    time.sleep(1)
        except Exception:
            pass
        os._exit(1)

    # give the child a moment to actually acquire the lock
    time.sleep(0.5)
    os.kill(pid, signal.SIGKILL)
    os.waitpid(pid, 0)

    def transform(base):
        return b"applied-after-stale-lock"

    ok = True
    detail = ""
    try:
        harness_merge.locked_update(path, transform)
    except Exception as exc:
        ok = False
        detail = f"raised {exc!r} instead of returning normally"
    check("case4: locked_update returned normally after stale lock killed", ok, detail)

    if ok:
        with open(path, "rb") as fh:
            data = fh.read()
        check("case4: transform output is on disk", data == b"applied-after-stale-lock", repr(data))
    else:
        check("case4: transform output is on disk", False, "locked_update did not return")


def case_5_contention():
    trials = 20
    third_outcomes = []
    for trial in range(trials):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "f.txt")
        with open(path, "wb") as fh:
            fh.write(b"")

        results = {}

        def run(tag, results_path):
            def transform(base):
                time.sleep(0.02)
                base = base or b""
                return base + tag.encode() + b"\n"

            try:
                harness_merge.locked_update(path, transform)
                with open(results_path, "wb") as rf:
                    rf.write(b"ok")
            except harness_merge.MergeRefusal as exc:
                with open(results_path, "wb") as rf:
                    rf.write(f"refusal:{exc.code}".encode())

        r1 = os.path.join(d, "r1")
        r2 = os.path.join(d, "r2")

        pid1 = os.fork()
        if pid1 == 0:
            run("A", r1)
            os._exit(0)
        pid2 = os.fork()
        if pid2 == 0:
            run("B", r2)
            os._exit(0)
        os.waitpid(pid1, 0)
        os.waitpid(pid2, 0)

        with open(r1, "rb") as fh:
            res1 = fh.read().decode()
        with open(r2, "rb") as fh:
            res2 = fh.read().decode()
        with open(path, "rb") as fh:
            content = fh.read()

        both_lines = b"A\n" in content and b"B\n" in content
        one_refused = (
            (res1 == "ok" and res2.startswith("refusal:6"))
            or (res2 == "ok" and res1.startswith("refusal:6"))
        )

        legal = False
        if res1 == "ok" and res2 == "ok" and both_lines:
            legal = True
        elif one_refused:
            # the refused side must have applied nothing: content is exactly the
            # winner's single line
            winner_line = b"A\n" if res1 == "ok" else b"B\n"
            if content == winner_line:
                legal = True

        if not legal:
            third_outcomes.append((trial, res1, res2, content))

    check(
        "case5: contention admits only the two legal outcomes over 20 trials",
        third_outcomes == [],
        f"illegal outcomes: {third_outcomes}",
    )


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
            status = ("BAD:" + ",".join(str(x) for x in bad)) if bad else "OK"
            fh.write(
                "|".join(
                    [
                        status,
                        f"reads={reads}",
                        f"saw_short={saw_short}",
                        f"saw_long={saw_long}",
                    ]
                )
            )
        os._exit(0)

    # Alternate between two clearly different legal bodies for the whole duration, instead of a
    # single replace, so the reader races MANY replace windows rather than one microsecond-wide
    # one: a non-atomic write regresses this from near-certain detection to a single-shot coin
    # flip. Writing the same body twice in a row (the loop's first iteration) is still a real
    # replace onto disk and still a legitimate torn-read opportunity, so it is not skipped.
    bodies = [short_body, long_body]
    i = 0
    deadline = time.time() + duration
    while time.time() < deadline:
        body = bodies[i % 2]
        i += 1

        def transform(base, body=body):
            return body

        harness_merge.locked_update(path, transform)
    os.waitpid(reader_pid, 0)

    with open(reader_out) as fh:
        result = fh.read()
    fields = result.split("|")
    status = fields[0]
    values = dict(p.split("=", 1) for p in fields[1:])
    reads = int(values["reads"])
    saw_short = values["saw_short"] == "True"
    saw_long = values["saw_long"] == "True"

    check("case6: no torn read observed by concurrent reader", status == "OK", status)
    check("case6: reader observed at least one read", reads > 0, reads)
    check(
        "case6: reader observed both the short and long body while racing the writer",
        saw_short and saw_long,
        (saw_short, saw_long),
    )


def case_7_require_destination():
    tail = re.compile(r"(?:^|/)mydir/(myfile-[a-z]+)\.md$")

    d = tempfile.mkdtemp()
    subdir = os.path.join(d, "mydir")
    os.makedirs(subdir)
    good_path = os.path.join(subdir, "myfile-abc.md")

    ok = True
    try:
        harness_merge.require_destination(good_path, tail, "the thing", ["hint"])
    except harness_merge.MergeRefusal as exc:
        ok = False
    check("case7: matching resolved path is accepted", ok)

    bad_path = os.path.join(d, "otherdir", "myfile-abc.md")
    raised_9 = False
    try:
        harness_merge.require_destination(bad_path, tail, "the thing", ["hint"])
    except harness_merge.MergeRefusal as exc:
        raised_9 = exc.code == 9
    check("case7: non-matching path raises MergeRefusal(9)", raised_9)

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
    raised_9_symlink = False
    try:
        harness_merge.require_destination(symlink_literal, tail, "the thing", ["hint"])
    except harness_merge.MergeRefusal as exc:
        raised_9_symlink = exc.code == 9
    check(
        "case7: symlink escape (literal ends in matching tail via symlinked 'mydir', "
        "realpath resolves outside and does not match) raises MergeRefusal(9)",
        raised_9_symlink,
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

    deadline = time.time() + 2
    while not os.path.exists(ready_path) and time.time() < deadline:
        time.sleep(0.02)

    original_timeout = harness_merge.LOCK_TIMEOUT_SECONDS
    original_interval = harness_merge.LOCK_RETRY_INTERVAL
    harness_merge.LOCK_TIMEOUT_SECONDS = 0.3
    harness_merge.LOCK_RETRY_INTERVAL = 0.02
    try:
        raised_code = None
        lines = []
        try:
            with harness_merge.acquire(lock_path):
                pass
        except harness_merge.MergeRefusal as exc:
            raised_code = exc.code
            lines = exc.lines
    finally:
        harness_merge.LOCK_TIMEOUT_SECONDS = original_timeout
        harness_merge.LOCK_RETRY_INTERVAL = original_interval
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)

    check("case8: acquire raises MergeRefusal(6) against a live holder", raised_code == 6, raised_code)
    names_path = any(lock_path in line for line in lines)
    check("case8: refusal lines name the lock path", names_path, lines)


def main():
    case_1_create_from_missing()
    case_2_apply_to_existing()
    case_3_refusal_leaves_byte_identical()
    case_4_stale_lock()
    case_5_contention()
    case_6_no_torn_read()
    case_7_require_destination()
    case_8_acquire_live_holder()

    failed = [r for r in RESULTS if not r[1]]
    if failed:
        print(f"FAIL - {len(failed)}/{len(RESULTS)} checks failed")
        sys.exit(1)
    print(f"PASS - {len(RESULTS)}/{len(RESULTS)} checks passed")


if __name__ == "__main__":
    main()
