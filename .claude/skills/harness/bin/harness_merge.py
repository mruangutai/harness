#!/usr/bin/env python3
"""harness_merge.py — the one locked read-modify-write core (FEAT-32 T-02, D-01, D-02).

This is a LIBRARY, not a gate: it is imported by every write route in this feature and never
registered as a hook. It never calls sys.exit — MergeRefusal exists precisely so the core can
report a refusal as a value instead, because a library that exits cannot be tested for its
return value. The caller decides whether to print the refusal's lines and exit its code.

This core has NO identity source. No agent_type reaches a Bash-invoked CLI and no environment
variable carries one, so this module can check WHERE a write lands — via require_destination —
and it can never check WHO asked for it. That is a real gap, not an oversight: it is reachable
from a read-only persona because bash-write-guard.py is allow-by-omission (it scans a command
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

Journaled pair write (FEAT-2488 T-01). locked_pair_update writes two files in one directory all
or nothing through an intent journal. A pair's journal is named for its PRIMARY — the primary's
path plus JOURNAL_SUFFIX, so the amendment pair's journal is plan.yaml.harness-merge.journal
beside plan.yaml — and it is created, replaced and removed only while that primary's lock is
held. The single-primary rule is therefore structural, not a convention: every writer of a
journal holds its primary's lock for the journal's whole life. The journal records each
member's name, the sha256 of its bytes before the write (null when the file was absent) and of
its bytes after, and the after image itself in base64; _read_journal is its only parser.

The protocol: under both locks, read both bases and run both transforms; write the journal to a
temp file, fsync it, os.replace it into place and fsync the directory; then replace the primary,
replace the secondary and unlink the journal. fsync is performed on the journal file and its
directory ONLY — never on an ordinary locked_update write, and never on a member replacement —
so the guarantee is against a killed process, and an OS crash or power loss is not warranted.

The JournalPending boundary: any failure up to and including the journal's rename wrote nothing
and propagates unchanged. Any Exception after it — the directory fsync, either member replace or
the unlink — leaves the transaction committed-pending: the journal stays on disk and the call
raises JournalPending, and the next write naming a member rolls it forward. A replay that fails
part-way is committed-pending too and raises JournalPending with replay=True; the calling
write's own change was then never attempted. There is no compensation path.

Recovery lives here and nowhere else: recover_journals(path) is the one entry point, and it runs
before every locked_update and locked_pair_update that names a journal member. Discovering a
journal is lock-free and only a hint; each journal is acted on only as re-read, membership
included, under its primary's lock. A member at its after state is left alone, one at its before
state is replaced with its after image, and a member in neither state refuses (JOURNAL DIVERGED,
exit 5) with every file and the journal untouched. A journal that cannot be parsed refuses
(JOURNAL UNREADABLE, exit 5) for every write in its directory, because it cannot say which
files it names; a readable one blocks only its own members' writers.

Lock order: a pair takes its primary's lock before its secondary's, which for the amendment pair
is plan.yaml.lock then feature.json.lock. sign-approval's signed_task_hashes write takes the same
order, and its nested feature.json write finds no journal because its outer locked_update on the
plan already recovered and still holds the plan lock, so no journal naming the plan can appear.
approval's rework write takes feature.json.lock before, never while holding, the plan lock. No
path acquires them reversed.

python3 stdlib only, no third-party imports, so this runs on any machine that runs the harness.
"""
import base64
import contextlib
import errno
import fcntl
import hashlib
import json
import math
import os
import tempfile
import time

# Module-level literals. Each is mutated BY NAME in a copy of the tree by the test's red proof.
USE_FLOCK = True
LOCK_TIMEOUT_SECONDS = 10.0
LOCK_RETRY_INTERVAL = 0.05
# A caller-environment override of the DEFAULT only; an explicit `timeout=` still wins. It
# exists for the tests that observe a real LOCKED refusal: each one otherwise waits the whole
# 10s budget, and shortening it changes how long a refusal takes, never whether it happens.
LOCK_TIMEOUT_ENV = "HARNESS_LOCK_TIMEOUT_SECONDS"

# A pair's intent journal is its primary's path plus this suffix (see the module docstring).
JOURNAL_SUFFIX = ".harness-merge.journal"
JOURNAL_SCHEMA = "harness-merge-journal/1"
_JOURNAL_TMP_PREFIX = ".harness-merge-tmp-"
_HEX_DIGITS = frozenset("0123456789abcdef")
_UNREADABLE_HINT = ("  every write naming a file in this directory refuses until the files are "
                    "reconciled by hand and the journal is removed.")


def _default_timeout():
    raw = os.environ.get(LOCK_TIMEOUT_ENV)
    if raw is None:
        return LOCK_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"{LOCK_TIMEOUT_ENV} must be a positive finite number, got {raw!r}") from None
    # `inf` would make the deadline unreachable: the LOCKED refusal would never fire and every
    # default-timeout acquire would hang on a stuck holder, so it is refused like zero.
    if not (value > 0 and math.isfinite(value)):
        raise ValueError(f"{LOCK_TIMEOUT_ENV} must be a positive finite number, got {raw!r}")
    return value


class MergeRefusal(Exception):
    """Carries an integer exit code and the stderr lines a caller should print before exiting
    with that code. The core never calls sys.exit itself — it raises this instead, so it stays
    testable for its return value rather than for a process exit."""

    def __init__(self, code, lines):
        self.code = code
        self.lines = list(lines)
        super().__init__(f"MergeRefusal({code}): {'; '.join(self.lines)}")


class JournalPending(Exception):
    """A journaled transaction is committed-pending: its journal is still on disk and the next
    write naming a member rolls it forward. locked_pair_update raises it (replay=False) only after
    its own journal was published; recovery raises it (replay=True) when replaying an existing
    journal fails, in which case the calling write's own change was never attempted."""

    def __init__(self, journal, cause, replay=False):
        self.journal = journal
        self.cause = cause
        self.replay = replay
        super().__init__(f"{type(cause).__name__}: {cause}")


@contextlib.contextmanager
def _acquire_flock(lock_path, timeout=None):
    timeout = _default_timeout() if timeout is None else timeout
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    try:
        deadline = time.monotonic() + timeout
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
                        [f"LOCKED: could not acquire {lock_path} within {timeout}s"],
                    )
                time.sleep(LOCK_RETRY_INTERVAL)
        yield
    finally:
        # flock releases on close; the lock FILE is deliberately never removed (D-02).
        os.close(fd)


@contextlib.contextmanager
def _acquire_excl(lock_path, timeout=None):
    """Reproduces expertise-merge.py's create-and-delete O_EXCL lock exactly. This branch is
    NEVER selected at runtime — nothing sets USE_FLOCK to False except a test's mutated copy
    of this file — and it exists only to prove the flock branch is what survives a SIGKILLed
    holder: this branch leaves its lock file behind and every later acquire then times out."""
    timeout = _default_timeout() if timeout is None else timeout
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise MergeRefusal(
                    6,
                    [f"LOCKED: could not acquire {lock_path} within {timeout}s"],
                )
            time.sleep(LOCK_RETRY_INTERVAL)
    try:
        yield
    finally:
        try:
            os.remove(lock_path)
        except FileNotFoundError:
            pass


def acquire(lock_path, timeout=None):
    """A context manager guarding lock_path. See module docstring for the flock/O_EXCL split.

    `timeout` overrides LOCK_TIMEOUT_SECONDS for THIS acquire only. It exists because the same
    core serves two callers with opposite cost profiles: a file merge can afford to wait, but a
    HOOK cannot -- dispatch-guard.py runs on every spawn, and a 10s wait there is 10s of stall
    per dispatch buying nothing, because the registry write it is waiting on takes milliseconds.
    A lock still held after a second means the holder is STUCK, not busy, and the useful answer
    then is to give up and fail open loudly rather than hang. Default unchanged for everyone who
    does not pass it.
    """
    if USE_FLOCK:
        return _acquire_flock(lock_path, timeout)
    return _acquire_excl(lock_path, timeout)


def replace_bytes(path, data):
    """Atomically replace `path` with `data`: write a tempfile in the SAME directory as path,
    then os.replace it onto path. os.replace is what makes a mid-write read impossible: a reader
    sees the whole old file or the whole new one, never a prefix. The tempfile is removed on any
    exception, which is re-raised. No fsync. The caller must hold the lock that governs path."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(dir=directory)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.remove(tmp_path)
        except FileNotFoundError:
            pass
        raise


def _read_base(path):
    """`path`'s bytes, or None when it does not exist."""
    if os.path.exists(path):
        with open(path, "rb") as fh:
            return fh.read()
    return None


def _sha256(data):
    return None if data is None else hashlib.sha256(data).hexdigest()


def _journal_unreadable(journal_path, reason):
    return MergeRefusal(5, [f"JOURNAL UNREADABLE: {journal_path}: {reason}", _UNREADABLE_HINT])


def _is_sha256(value):
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX_DIGITS


def _is_bare_name(name):
    if not isinstance(name, str) or name in ("", ".", ".."):
        return False
    return os.sep not in name and (os.altsep is None or os.altsep not in name)


def _member_hashes(journal_path, name, member):
    before, after = member.get("before_sha256"), member.get("after_sha256")
    if not (before is None or _is_sha256(before)) or not _is_sha256(after):
        raise _journal_unreadable(journal_path, f"member {name}: a recorded sha256 is malformed")
    return before, after


def _member_image(journal_path, name, encoded, after):
    """The decoded after image, which must hash to the recorded after_sha256."""
    try:
        image = base64.b64decode(encoded, validate=True)
    except (TypeError, ValueError):
        raise _journal_unreadable(
            journal_path, f"member {name}: after_b64 is not standard base64") from None
    if hashlib.sha256(image).hexdigest() != after:
        raise _journal_unreadable(
            journal_path, f"member {name}: after_b64 does not hash to after_sha256")
    return image


def _journal_member(journal_path, member, seen):
    """One validated journal member, with its after image decoded; `seen` collects names."""
    if not isinstance(member, dict):
        raise _journal_unreadable(journal_path, "a member is not a mapping")
    name = member.get("name")
    if not _is_bare_name(name) or name in seen:
        raise _journal_unreadable(
            journal_path, f"member name {name!r} is not a distinct bare file name")
    seen.add(name)
    before, after = _member_hashes(journal_path, name, member)
    image = _member_image(journal_path, name, member.get("after_b64"), after)
    return {"name": name, "before_sha256": before, "after_sha256": after, "after": image}


def _journal_bytes(journal_path):
    """The journal's bytes. FileNotFoundError propagates (a journal can vanish between a
    lock-free listing and this read); any other read failure is the UNREADABLE refusal."""
    try:
        with open(journal_path, "rb") as fh:
            return fh.read()
    except FileNotFoundError:
        raise
    except OSError as exc:
        raise _journal_unreadable(journal_path, f"cannot be read ({exc})") from None


def _read_journal(journal_path):
    """The module's only parse of a journal: its members, each with its decoded after image.
    Anything but a well-formed harness-merge-journal/1 record is MergeRefusal(5) UNREADABLE."""
    raw = _journal_bytes(journal_path)
    try:
        record = json.loads(raw)
    except (ValueError, RecursionError) as exc:
        raise _journal_unreadable(journal_path, f"not JSON ({exc})") from None
    if not isinstance(record, dict) or record.get("schema") != JOURNAL_SCHEMA:
        raise _journal_unreadable(journal_path, f"schema is not {JOURNAL_SCHEMA}")
    members = record.get("members")
    if not isinstance(members, list) or not members:
        raise _journal_unreadable(journal_path, "members is not a non-empty list")
    seen = set()
    return [_journal_member(journal_path, member, seen) for member in members]


def _journal_names(journal_path, entry, name):
    """Whether the journal at journal_path (directory entry `entry`) names file `name`. An
    unreadable journal names every file (fail closed); a vanished one names none."""
    if entry == name + JOURNAL_SUFFIX:
        return True
    try:
        members = _read_journal(journal_path)
    except FileNotFoundError:
        return False
    except MergeRefusal:
        return True
    return any(member["name"] == name for member in members)


def _journals_naming(path):
    """Lock-free: the full paths of the journals in path's directory that name path. Only a
    HINT — nothing acts on it until _recover_journal re-reads the journal, membership included,
    under its primary's lock."""
    directory, name = os.path.split(os.path.abspath(path))
    try:
        entries = sorted(os.listdir(directory))
    except FileNotFoundError:
        return []
    return [os.path.join(directory, entry) for entry in entries
            if entry.endswith(JOURNAL_SUFFIX)
            and _journal_names(os.path.join(directory, entry), entry, name)]


def _replay_targets(journal_path, directory, members):
    """Every member's current state, computed before anything is written: the (path, after
    image) pairs still at their before state. A member in neither state refuses DIVERGED."""
    targets = []
    for member in members:
        member_path = os.path.join(directory, member["name"])
        current = _sha256(_read_base(member_path))
        if current not in (member["before_sha256"], member["after_sha256"]):
            raise MergeRefusal(5, [
                f"JOURNAL DIVERGED: {member_path} matches neither the before nor the after state "
                f"recorded in {journal_path}",
                "  nothing was changed; reconcile the file by hand, then remove the journal."])
        if current != member["after_sha256"]:
            targets.append((member_path, member["after"]))
    return targets


def _replay(journal_path, targets):
    """Roll the journal forward. Nothing runs after the unlink, so a completed replay never
    reports pending; the unlink is not followed by a directory fsync (a journal a crash
    resurrects names members already at after, a no-op, or refuses DIVERGED)."""
    try:
        for member_path, image in targets:
            replace_bytes(member_path, image)
        os.unlink(journal_path)
    except Exception as exc:
        raise JournalPending(journal_path, exc, replay=True) from exc


def _recover_journal(journal_path, path, timeout):
    """Roll one journal forward for a write naming `path`, acting only on the generation read
    under its primary's lock. Returns True when it replayed and removed the journal, False when
    the journal is gone or its current generation does not name path."""
    primary = journal_path[: -len(JOURNAL_SUFFIX)]
    directory, primary_name = os.path.split(primary)
    with contextlib.ExitStack() as stack:
        stack.enter_context(acquire(primary + ".lock", timeout))
        if not os.path.exists(journal_path):
            return False
        members = _read_journal(journal_path)
        if members[0]["name"] != primary_name:
            raise _journal_unreadable(journal_path, f"its first member is not {primary_name}")
        if not any(member["name"] == os.path.basename(path) for member in members):
            return False
        for member in members[1:]:
            stack.enter_context(acquire(os.path.join(directory, member["name"]) + ".lock", timeout))
        _replay(journal_path, _replay_targets(journal_path, directory, members))
        return True


def recover_journals(path, timeout=None):
    """The one recovery entry point for callers outside this module: roll forward every journal
    that names path. True when any journal was replayed and removed, else False."""
    recovered = False
    for journal_path in _journals_naming(path):
        recovered = _recover_journal(journal_path, path, timeout) or recovered
    return recovered


def locked_update(path, transform, timeout=None):
    """The whole read-modify-write, under acquire(path + ".lock").

    First recovers any journal naming path (recover_journals); a journal naming path that
    appears before the lock is taken sends it round again. Then reads `path` as bytes (None if
    it does not exist), calls transform(base_bytes) to get the new bytes, and writes them with
    replace_bytes. With no journal naming path, this is exactly the plain locked write.

    If transform raises MergeRefusal, nothing is written at all and the refusal is re-raised:
    the file is left byte-identical to what it was before this call.
    """
    lock_path = path + ".lock"
    while True:
        recover_journals(path, timeout)
        with acquire(lock_path, timeout):
            if _journals_naming(path):
                continue
            base = _read_base(path)
            new_bytes = transform(base)  # may raise MergeRefusal — nothing written in that case
            replace_bytes(path, new_bytes)
            return


def _pair_directory(primary, secondary):
    directory = os.path.dirname(os.path.abspath(primary))
    other = os.path.dirname(os.path.abspath(secondary))
    if os.path.realpath(directory) != os.path.realpath(other) or \
            os.path.basename(primary) == os.path.basename(secondary):
        raise ValueError(f"locked_pair_update needs two different files in one directory, "
                         f"got {primary!r} and {secondary!r}")
    return directory


def _publish_journal(journal_path, directory, members):
    """Write the journal for (path, before, after) members: temp file, fsync, os.replace. Any
    exception removes the temp file and propagates unchanged — nothing was written."""
    record = {"schema": JOURNAL_SCHEMA, "members": [
        {"name": os.path.basename(path), "before_sha256": _sha256(before),
         "after_sha256": _sha256(after), "after_b64": base64.b64encode(after).decode("ascii")}
        for path, before, after in members]}
    data = json.dumps(record, sort_keys=True).encode("utf-8")
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=_JOURNAL_TMP_PREFIX)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, journal_path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.remove(tmp_path)
        raise


def _commit_published(journal_path, directory, images):
    """After the journal's rename: fsync the directory, replace each member, unlink the
    journal. An Exception here is JournalPending with the journal left in place."""
    try:
        fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        for path, data in images:
            replace_bytes(path, data)
        os.unlink(journal_path)
    except Exception as exc:
        raise JournalPending(journal_path, exc) from exc


def locked_pair_update(primary, primary_transform, secondary, secondary_transform, timeout=None):
    """Write two different files in one directory all or nothing, through primary's journal.

    Recovers any journal naming either file, then takes primary's lock and then secondary's (a
    journal naming either that appears meanwhile sends it round again). Each transform gets its
    file's bytes (None if absent); a MergeRefusal or any other exception from either propagates
    with nothing written and no journal. Then the journal is published (see the module
    docstring) and both files replaced. Any Exception after the journal's rename raises
    JournalPending, journal kept; a BaseException that is not an Exception propagates unchanged,
    journal also kept. Raises ValueError unless the paths are two files in one directory.
    """
    directory = _pair_directory(primary, secondary)
    journal_path = primary + JOURNAL_SUFFIX
    while True:
        recover_journals(primary, timeout)
        recover_journals(secondary, timeout)
        with contextlib.ExitStack() as stack:
            stack.enter_context(acquire(primary + ".lock", timeout))
            stack.enter_context(acquire(secondary + ".lock", timeout))
            if _journals_naming(primary) or _journals_naming(secondary):
                continue
            base_primary, base_secondary = _read_base(primary), _read_base(secondary)
            new_primary = primary_transform(base_primary)
            new_secondary = secondary_transform(base_secondary)
            _publish_journal(journal_path, directory, ((primary, base_primary, new_primary),
                                                       (secondary, base_secondary, new_secondary)))
            _commit_published(journal_path, directory, ((primary, new_primary),
                                                        (secondary, new_secondary)))
            return


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
