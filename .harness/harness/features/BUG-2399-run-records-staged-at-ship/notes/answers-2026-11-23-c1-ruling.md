# Operator ruling — BUG-2399 after validate c1 (2026-11-23)

Answers Q1 from run 2026-11-23-02-validate-validator.

- **SC-03, the clause "the manual force-add is removed": accepted as vacuously satisfied.**
  - Base `9eb07b4f:.omp/commands/harness-ship.md` never contained a force-add instruction. The hand step was undocumented practice, and the grilling assumed the text existed without checking it.
  - At the pin, the file documents the automatic staging, which is what the clause was for.
  - SC-03 is graded on its remaining clauses. No pm amendment and no re-approval.
- **MF-1** (os.walk silently skips unreadable subtrees) is fixed main-session-direct inside the signed ruling, 1 round / 45 min.
