# Observations — harness-backend-dev — FEAT-30

- 2026-08-20: T-06 cycle 2 (send-back). `bash-write-guard.sh` denies `cp -R src "$T/bin"` when `$T`
  is a bash variable holding a mktemp path outside the repo — its static parser never expands `$T`,
  treats the literal string `$T/bin` as a repo-relative path, and denies it as "outside your
  domain" even though the real runtime target is legitimately outside every domain. A prior spawn
  on this same task returned PASS with an artifact path that was never written — most plausibly
  because it hit this exact denial repeatedly on the task's own `verify:` block and never got far
  enough to write the receipt, yet still certified success. Lesson for next time a `verify:` uses a
  bash variable for a temp/scratch path: substitute the mktemp'd path as a literal string in the
  command instead of referencing it by variable, and confirm the write actually happened (`ls` the
  target) before trusting a script's own exit code — a guard denial inside a multi-line Bash script
  can still let later `echo`/`exit 0` lines make the block look clean.
