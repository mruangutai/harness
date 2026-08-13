# Observations — harness-backend-dev — FEAT-16

- 2026-08-12 (T-08): restoring a mutant in a dirty working tree — `git checkout -- <path>`
  reverts the WHOLE file to HEAD, wiping uncommitted GREEN work along with the mutation, not just
  the mutant edit. Caught via a hash mismatch (P-09 says record and check the hash; this is the
  how-not-to-restore lesson it doesn't spell out on its own). Correct approach: swap content back
  by hand from the recorded pre-mutation bytes/diff, or re-apply the known-good edits, never
  `git checkout --` on a file with uncommitted changes still in it.
