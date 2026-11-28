# T-01 fail-first record (BUG-2566)

Main session, main-session-direct (DEC-174), 2026-11-27. The base is the merge of `main` at 87efcd8a (BUG-2565 landed).

D-04 precondition: `.omp/extensions/digest-schema.ts` is absent, and `grep -c 'from "./digest-schema' .omp/extensions/harness-hooks.ts` printed 0.

## RED: new tests against the unchanged hook

Command: `bun test tests/unit/omp-hooks.test.ts`. Exit 1: 248 pass, 26 fail.

Failing tests:

- OMP task lifecycle adapter > BUG-2566 SC-02: a stale persona's read is refused before any policy call
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale persona's write is refused before any policy call
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale persona's edit is refused before any policy call
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale persona's bash is refused before any policy call
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale persona's task is refused before any policy call
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale persona's yield of a PASS object is refused before any policy call
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale persona's yield of an array is refused before any policy call
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale persona's yield of a PASS object's JSON text is refused before any policy call
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale persona's yield of malformed text is refused before any policy call
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale persona's data-less finalize is refused before any policy call
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale held persona's read is refused as stale, not as held
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale Main task is refused with the bare reason
- OMP task lifecycle adapter > BUG-2566 SC-02: a stale Main merge Bash is refused with the bare reason
- BUG-2566 stale hook fingerprint > BUG-2566 SC-01: an untouched loaded module is not stale
- BUG-2566 stale hook fingerprint > BUG-2566 SC-01: an appended comment line makes the module stale
- BUG-2566 stale hook fingerprint > BUG-2566 SC-01: a deleted module is stale
- BUG-2566 stale hook fingerprint > BUG-2566 SC-01: a same-size byte change with the load-time mtime restored is stale
- BUG-2566 stale hook fingerprint > BUG-2566 SC-01: a module replaced by a FIFO is stale and never blocks
- BUG-2566 stale hook fingerprint > BUG-2566 SC-04: a touched mtime with unchanged bytes is not stale
- BUG-2566 stale hook fingerprint > BUG-2566 SC-04: a rewrite with identical bytes is not stale
- BUG-2566 stale hook fingerprint > BUG-2566 SC-04: a change restored to the original bytes is not stale
- BUG-2566 stale hook fingerprint > BUG-2566 SC-04: a changed digest schema file is not fingerprinted
- BUG-2566 stale hook fingerprint > BUG-2566 SC-04: a removed digest schema file is not fingerprinted
- BUG-2566 stale hook fingerprint > BUG-2566 SC-04: a new extension module this process never loaded is not fingerprinted
- BUG-2566 stale hook fingerprint > BUG-2566 SC-04: edits to another checkout leave this one fresh
- BUG-2566 stale hook fingerprint > BUG-2566 SC-05: the check on the real module has a median under 5 ms

## Preserved, passing on the unchanged hook

Command: `bun test tests/unit/omp-hooks.test.ts -t "BUG-2566 SC-0(2: a stale persona's BLOCKED|3)"`. Exit 0: 8 pass.

- The four SC-02 carve-out cases: a stale persona's BLOCKED yield (ready run as an object and as JSON text; held run as an object and as JSON text). Each reaches validate-digest.py once.
- The four SC-03 cases: a stale Main's read, edit, write, and bash `git status` are not checked.

## GREEN

- `bun test tests/unit/omp-hooks.test.ts`: exit 0, 274 pass, 0 fail.
- `bun run typecheck`: exit 0.

## The SC-04 discrimination mutant

The implemented hook was saved to a mktemp path. Only `entryState`'s regular-file branch was changed, to `return String(fstatSync(fd).mtimeMs);`.

Command: `bun test tests/unit/omp-hooks.test.ts -t 'BUG-2566 stale hook fingerprint'`. Exit 1: 9 pass, 4 fail.

- BUG-2566 stale hook fingerprint > BUG-2566 SC-01: a same-size byte change with the load-time mtime restored is stale
- BUG-2566 stale hook fingerprint > BUG-2566 SC-04: a touched mtime with unchanged bytes is not stale
- BUG-2566 stale hook fingerprint > BUG-2566 SC-04: a rewrite with identical bytes is not stale
- BUG-2566 stale hook fingerprint > BUG-2566 SC-04: a change restored to the original bytes is not stale

The saved bytes were copied back, and `cmp` confirmed the file equals the saved copy before commit.
