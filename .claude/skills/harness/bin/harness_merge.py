#!/usr/bin/env python3
"""harness_merge.py — the one locked read-modify-write core (FEAT-32 T-02, D-01, D-02).

This is a LIBRARY, not a gate: it is imported by every write route in this feature and never
registered as a hook. It never calls sys.exit — MergeRefusal exists precisely so the core can
report a refusal as a value instead, because a library that exits cannot be tested for its
return value. The caller decides whether to print the refusal's lines and exit its code.

This core has NO identity source. No agent_type reaches a Bash-invoked CLI and no environment
variable carries one, so this module can check WHERE a write lands — via require_destination —
and it can never check WHO asked for it. That is a real gap, not an oversight: it is reachable
from a read-only persona because bash-write-guard.sh is allow-by-omission (it scans a command
for a write pattern it recognises and exits 0 when it finds none, before the read-only denial
and the domain walk ever run). That gap is issue #627 and is not fixed here.

Locking (D-02): the default path opens the lock file O_CREAT|O_RDWR — NEVER O_EXCL, so the
file's existence is not itself the lock — and takes an exclusive fcntl.flock, released by
closing the descriptor when the holder exits or is killed. The lock file is deliberately never
removed: flock has no stale state, so leaving the file behind costs nothing, and removing it
would reintroduce the create-and-delete race this design exists to avoid. The alternate branch
(USE_FLOCK = False) reproduces expertise-merge.py's create-and-delete O_EXCL behaviour exactly,
and exists ONLY so a test can prove the flock branch is what makes the stale-lock case pass —
nothing selects it at runtime, no flag and no environment variable.

python3 stdlib only, no third-party imports, so this runs on any machine that runs the harness.
"""
import contextlib
import errno
import fcntl
import os
import tempfile
import time

# Module-level literals. Each is mutated BY NAME in a copy of the tree by the test's red proof.
USE_FLOCK = True
LOCK_TIMEOUT_SECONDS = 10.0
LOCK_RETRY_INTERVAL = 0.05


class MergeRefusal(Exception):
    """Carries an integer exit code and the stderr lines a caller should print before exiting
    with that code. The core never calls sys.exit itself — it raises this instead, so it stays
    testable for its return value rather than for a process exit."""

    def __init__(self, code, lines):
        self.code = code
        self.lines = list(lines)
        super().__init__(f"MergeRefusal({code}): {'; '.join(self.lines)}")


@contextlib.contextmanager
def _acquire_flock(lock_path):
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    try:
        deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as exc:
                if exc.errno not in (errno.EACCES, errno.EAGAIN):
                    raise
                if time.monotonic() >= deadline:
                    raise MergeRefusal(
                        6,
                        [f"LOCKED: could not acquire {lock_path} within {LOCK_TIMEOUT_SECONDS}s"],
                    )
                time.sleep(LOCK_RETRY_INTERVAL)
        yield
    finally:
        # flock releases on close; the lock FILE is deliberately never removed (D-02).
        os.close(fd)


@contextlib.contextmanager
def _acquire_excl(lock_path):
    """Reproduces expertise-merge.py's create-and-delete O_EXCL lock exactly. This branch is
    NEVER selected at runtime — nothing sets USE_FLOCK to False except a test's mutated copy
    of this file — and it exists only to prove the flock branch is what survives a SIGKILLed
    holder: this branch leaves its lock file behind and every later acquire then times out."""
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise MergeRefusal(
                    6,
                    [f"LOCKED: could not acquire {lock_path} within {LOCK_TIMEOUT_SECONDS}s"],
                )
            time.sleep(LOCK_RETRY_INTERVAL)
    try:
        yield
    finally:
        try:
            os.remove(lock_path)
        except FileNotFoundError:
            pass


def acquire(lock_path):
    """A context manager guarding lock_path. See module docstring for the flock/O_EXCL split."""
    if USE_FLOCK:
        return _acquire_flock(lock_path)
    return _acquire_excl(lock_path)


def locked_update(path, transform):
    """The whole read-modify-write, under acquire(path + ".lock").

    Reads `path` as bytes (None if it does not exist), calls transform(base_bytes) to get the
    new bytes, and writes the result to a tempfile in the SAME directory as path before
    os.replace-ing it onto path. os.replace is what makes a mid-write read impossible: a reader
    sees the whole old file or the whole new one, never a prefix.

    If transform raises MergeRefusal, nothing is written at all and the refusal is re-raised:
    the file is left byte-identical to what it was before this call.
    """
    lock_path = path + ".lock"
    with acquire(lock_path):
        if os.path.exists(path):
            with open(path, "rb") as fh:
                base = fh.read()
        else:
            base = None

        new_bytes = transform(base)  # may raise MergeRefusal — nothing written in that case

        directory = os.path.dirname(os.path.abspath(path)) or "."
        fd, tmp_path = tempfile.mkstemp(dir=directory)
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(new_bytes)
            os.replace(tmp_path, path)
        except BaseException:
            try:
                os.remove(tmp_path)
            except FileNotFoundError:
                pass
            raise


def require_destination(path, tail_regex, what, hint_lines):
    """Resolve `path` with realpath(abspath(...)) and require tail_regex to match the RESOLVED
    string — never the argument as given. Matching the resolved path is what stops a dot-dot
    segment or a symlink from walking out of the file class this tool owns and back in under a
    tail that merely looks legal. Raises MergeRefusal(9) naming the given path, the resolved
    path, and what this tool does own."""
    resolved = os.path.realpath(os.path.abspath(path))
    if tail_regex.search(resolved):
        return resolved
    lines = [
        f"REFUSED: {path} is not {what}.",
        f"  resolved to: {resolved}",
        f"  this tool only writes: {what}",
    ]
    lines.extend(hint_lines)
    raise MergeRefusal(9, lines)
