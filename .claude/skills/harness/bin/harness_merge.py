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
member's name, the sha256 of its bytes before the write (null when the file was absent — the
key is required, so only an explicit null records an absence) and of its bytes after, and the
after image itself in base64; _read_journal is its only parser. There is exactly one legal
pair, JOURNAL_PAIR: plan.yaml then feature.json, the amendment pair. locked_pair_update writes
no other, and _read_journal accepts no other: exactly those two members, in that order.

The protocol: under both locks, read both bases and run both transforms; write the journal to a
temp file, fsync it, os.replace it into place and fsync the directory; then replace the primary,
replace the secondary and unlink the journal. fsync is performed on the journal file and its
directory ONLY — never on an ordinary locked_update write, and never on a member replacement —
so the guarantee is against a killed process, and an OS crash or power loss is not warranted.

The JournalPending boundary: any failure up to and including the journal's rename wrote nothing
and propagates unchanged. An OSError after it — the directory fsync, either member replace or
the unlink, whose bodies are os calls only — leaves the transaction committed-pending: the
journal stays on disk and the call raises JournalPending, and the next write naming a member
rolls it forward. A replay whose replace or unlink raises OSError part-way is committed-pending
too and raises JournalPending with replay=True; the calling write's own change was then never
attempted. Any other exception after the rename propagates unchanged as itself (a traceback),
the journal also kept, so the next write still rolls it forward: the handlers name the
boundary's real error class, never Exception (FEAT-63's broad-catch census, ceiling 0). There
is no compensation path.

Recovery lives here and nowhere else: recover_journals(path) is the one entry point, and it runs
before every locked_update and locked_pair_update that names a journal member. Discovery looks up
ONE name, the only one a producer writes: JOURNAL_PAIR's primary plus JOURNAL_SUFFIX
(plan.yaml.harness-merge.journal), as a path in the directory (validate c3 MF-12). Any other
*.harness-merge.journal entry is never read, never blocks a write and is never replayed, however
it arrived: the discovery set equals the producer set. Discovering the journal is lock-free and
only a hint; it is acted on only as re-read, membership included, under its primary's lock. A
member at its after state is left alone, one at its before state is replaced with its after
image, and a member in neither state refuses (JOURNAL DIVERGED, exit 5) with every file and the
journal untouched. A journal that cannot be parsed refuses (JOURNAL UNREADABLE, exit 5) for every
write in its directory, because it cannot say which files it names; a readable one blocks only
its own members' writers. The journal entry is examined with lstat, and the descriptor opened for
it with fstat before a byte is read: a symlink (dangling or not), a FIFO or a directory refuses
UNREADABLE naming the journal, even one swapped in after the lstat, so no writer blocks on or
reads from a FIFO or spins on an entry that lists as present and reads as absent.

Lock order: a pair takes its primary's lock before its secondary's, which for the amendment pair
is plan.yaml.lock then feature.json.lock. sign-approval's signed_task_hashes write takes the same
order, and its nested feature.json write finds no journal because its outer locked_update on the
plan already recovered and still holds the plan lock, so no journal naming the plan can appear.
approval's rework write takes feature.json.lock before, never while holding, the plan lock. A
journal named for feature.json — which would lock feature.json then plan.yaml — is never
discovered. No path acquires them reversed.

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
import stat
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
# The one pair a journal may record, primary first (validate c0 MF-2): the amendment pair.
JOURNAL_PAIR = ("plan.yaml", "feature.json")
# The one journal name any producer writes, and so the one name discovery looks up (MF-12).
_JOURNAL_NAME = JOURNAL_PAIR[0] + JOURNAL_SUFFIX
# A refusal echoes journal contents to the operator's terminal: repr (escaped), cut to this.
_ECHO_LIMIT = 80
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


def _echo(value):
    """A journal value as a refusal may print it: repr, so control characters arrive escaped,
    cut to _ECHO_LIMIT characters, so a crafted journal cannot flood the operator's terminal."""
    text = repr(value)
    return text if len(text) <= _ECHO_LIMIT else text[:_ECHO_LIMIT] + "...(truncated)"


def _is_sha256(value):
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX_DIGITS


def _is_bare_name(name):
    if not isinstance(name, str) or name in ("", ".", ".."):
        return False
    return os.sep not in name and (os.altsep is None or os.altsep not in name)


def _member_hashes(journal_path, name, member):
    """The recorded (before, after) digests. before_sha256 must be PRESENT: an explicit null
    records an absent file, and a missing key is a malformed record, never an absence."""
    if "before_sha256" not in member:
        raise _journal_unreadable(
            journal_path, f"member {_echo(name)}: before_sha256 is missing (only an explicit "
                          "null records an absent file)")
    before, after = member["before_sha256"], member.get("after_sha256")
    if not (before is None or _is_sha256(before)) or not _is_sha256(after):
        raise _journal_unreadable(
            journal_path, f"member {_echo(name)}: a recorded sha256 is malformed (before "
                          f"{_echo(before)}, after {_echo(after)})")
    return before, after


def _member_image(journal_path, name, encoded, after):
    """The decoded after image, which must hash to the recorded after_sha256."""
    try:
        image = base64.b64decode(encoded, validate=True)
    except (TypeError, ValueError):
        raise _journal_unreadable(
            journal_path, f"member {_echo(name)}: after_b64 is not standard base64") from None
    if hashlib.sha256(image).hexdigest() != after:
        raise _journal_unreadable(
            journal_path, f"member {_echo(name)}: after_b64 does not hash to after_sha256")
    return image


def _journal_member(journal_path, member, seen):
    """One validated journal member, with its after image decoded; `seen` collects names."""
    if not isinstance(member, dict):
        raise _journal_unreadable(journal_path, "a member is not a mapping")
    name = member.get("name")
    if not _is_bare_name(name) or name in seen:
        raise _journal_unreadable(
            journal_path, f"member name {_echo(name)} is not a distinct bare file name")
    seen.add(name)
    before, after = _member_hashes(journal_path, name, member)
    image = _member_image(journal_path, name, member.get("after_b64"), after)
    return {"name": name, "before_sha256": before, "after_sha256": after, "after": image}


def _require_regular(journal_path):
    """lstat the journal entry without following it. FileNotFoundError propagates (a journal
    can vanish between a lock-free listing and this look); anything but a regular file — a
    symlink, dangling or not, a FIFO, a directory — is the UNREADABLE refusal, decided before
    any open, so a FIFO standing at the name is never opened and a dangling entry never reads
    as absent. An entry swapped in after this look is _journal_bytes' fstat's to refuse."""
    try:
        mode = os.lstat(journal_path).st_mode
    except FileNotFoundError:
        raise
    except OSError as exc:
        raise _journal_unreadable(journal_path, f"cannot be examined ({exc})") from None
    if not stat.S_ISREG(mode):
        raise _journal_unreadable(
            journal_path, "is not a regular file (a symlink, FIFO, directory or device)")


def _regular_fd_bytes(fd):
    """The bytes behind an open descriptor when it is a regular file, else None — decided by
    fstat before a single byte is read."""
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        return None
    with os.fdopen(fd, "rb", closefd=False) as fh:
        return fh.read()


def _journal_bytes(journal_path):
    """The journal's bytes, read only from a regular file. _require_regular checks the name;
    O_NOFOLLOW|O_NONBLOCK and an fstat of the OPENED descriptor hold that against an entry
    swapped after the lstat: a symlink fails to open, a FIFO (even one already holding a
    record) opens without blocking and is refused before any read, as is a directory or
    device. FileNotFoundError propagates; any other failure is UNREADABLE."""
    _require_regular(journal_path)
    try:
        fd = os.open(journal_path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            data = _regular_fd_bytes(fd)
        finally:
            os.close(fd)
    except FileNotFoundError:
        raise
    except OSError as exc:
        raise _journal_unreadable(journal_path, f"cannot be read ({exc})") from None
    if data is None:
        raise _journal_unreadable(
            journal_path, "is not a regular file once opened (replaced after it was examined)")
    return data


def _pair_members(journal_path, members):
    """The record's members, validated and decoded: exactly JOURNAL_PAIR's two, in order, or
    the UNREADABLE refusal. A stricter parse of the one schema, whose only producer
    (locked_pair_update) writes exactly that pair."""
    if not isinstance(members, list) or len(members) != len(JOURNAL_PAIR):
        raise _journal_unreadable(
            journal_path, f"members is not a list of exactly {len(JOURNAL_PAIR)} "
                          f"({' then '.join(JOURNAL_PAIR)})")
    seen = set()
    parsed = [_journal_member(journal_path, member, seen) for member in members]
    names = tuple(member["name"] for member in parsed)
    if names != JOURNAL_PAIR:
        raise _journal_unreadable(
            journal_path, f"its members are {_echo(names)}, not {' then '.join(JOURNAL_PAIR)}")
    return parsed


def _read_journal(journal_path):
    """The module's only parse of a journal: its members, each with its decoded after image.
    Anything but a well-formed harness-merge-journal/1 record of exactly JOURNAL_PAIR's two
    members, in order, is MergeRefusal(5) UNREADABLE."""
    raw = _journal_bytes(journal_path)
    try:
        record = json.loads(raw)
    except (ValueError, RecursionError) as exc:
        raise _journal_unreadable(journal_path, f"not JSON ({exc})") from None
    if not isinstance(record, dict) or record.get("schema") != JOURNAL_SCHEMA:
        raise _journal_unreadable(journal_path, f"schema is not {JOURNAL_SCHEMA}")
    return _pair_members(journal_path, record.get("members"))


def _journal_names(journal_path, name):
    """Whether the pair's journal at journal_path names file `name`. It always names its
    primary; an unreadable one names every file (fail closed); a vanished one names none."""
    if name == JOURNAL_PAIR[0]:
        return True
    try:
        members = _read_journal(journal_path)
    except FileNotFoundError:
        return False
    except MergeRefusal:
        return True
    return any(member["name"] == name for member in members)


def _journals_naming(path):
    """Lock-free: [the pair's journal] when it is present in path's directory and names path,
    else []. Only the one name a producer writes is looked up (validate c3 MF-12), so any other
    *.harness-merge.journal is never read. It is looked up as a PATH, never matched against
    listed spellings: where the filesystem folds case, the producer's os.replace onto an
    existing case variant keeps the variant's spelling, and that entry is the producer's file.
    Only a HINT — nothing acts on it until _recover_journal re-reads the journal, membership
    included, under its primary's lock."""
    directory, name = os.path.split(os.path.abspath(path))
    journal_path = os.path.join(directory, _JOURNAL_NAME)
    try:
        os.lstat(journal_path)
    except FileNotFoundError:
        return []
    return [journal_path] if _journal_names(journal_path, name) else []


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
    resurrects names members already at after, a no-op, or refuses DIVERGED). The body is
    replace_bytes and os.unlink, so OSError is its whole failure class."""
    try:
        for member_path, image in targets:
            replace_bytes(member_path, image)
        os.unlink(journal_path)
    except OSError as exc:
        raise JournalPending(journal_path, exc, replay=True) from exc


def _recover_journal(journal_path, path, timeout):
    """Roll the pair's journal forward for a write naming `path`, acting only on the generation
    read under its primary's lock. Discovery hands over only JOURNAL_PAIR's primary's journal,
    so no journal can take feature.json.lock before plan.yaml.lock, or a lock on a file outside
    the pair. Before ANY lock, the entry must be a regular file, else UNREADABLE. Returns True
    when it replayed and removed the journal, False when the journal is gone or its current
    generation does not name path."""
    directory = os.path.dirname(journal_path)
    try:
        _require_regular(journal_path)
    except FileNotFoundError:
        return False
    primary, secondary = (os.path.join(directory, name) for name in JOURNAL_PAIR)
    with contextlib.ExitStack() as stack:
        stack.enter_context(acquire(primary + ".lock", timeout))
        try:
            members = _read_journal(journal_path)
        except FileNotFoundError:
            return False
        if not any(member["name"] == os.path.basename(path) for member in members):
            return False
        stack.enter_context(acquire(secondary + ".lock", timeout))
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
    """The pair's one directory. Only JOURNAL_PAIR, in order, is a pair: the recovery side
    refuses any other journal, so the write side never publishes one."""
    directory = os.path.dirname(os.path.abspath(primary))
    other = os.path.dirname(os.path.abspath(secondary))
    if os.path.realpath(directory) != os.path.realpath(other) or \
            (os.path.basename(primary), os.path.basename(secondary)) != JOURNAL_PAIR:
        raise ValueError(f"locked_pair_update writes only {' then '.join(JOURNAL_PAIR)} in one "
                         f"directory, got {primary!r} and {secondary!r}")
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
    journal. An OSError here — the body's whole failure class: os.open, os.fsync, os.close,
    replace_bytes, os.unlink — is JournalPending with the journal left in place."""
    try:
        fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        for path, data in images:
            replace_bytes(path, data)
        os.unlink(journal_path)
    except OSError as exc:
        raise JournalPending(journal_path, exc) from exc


def locked_pair_update(primary, primary_transform, secondary, secondary_transform, timeout=None):
    """Write the amendment pair all or nothing, through primary's journal.

    Recovers any journal naming either file, then takes primary's lock and then secondary's (a
    journal naming either that appears meanwhile sends it round again). Each transform gets its
    file's bytes (None if absent); a MergeRefusal or any other exception from either propagates
    with nothing written and no journal. Then the journal is published (see the module
    docstring) and both files replaced. An OSError after the journal's rename raises
    JournalPending, journal kept; any other exception propagates unchanged, journal also kept.
    Raises ValueError unless primary and secondary are JOURNAL_PAIR's two files, in that order,
    in one directory.
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
