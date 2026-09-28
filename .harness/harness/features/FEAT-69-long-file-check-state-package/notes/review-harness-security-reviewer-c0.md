# FEAT-69 security review — implementation pin

BLUF: PASS. The pinned refactor has a security-relevant repository-input and process boundary, but introduces no exploitable security regression.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned range a726bad8..db488aa7c78e392c788bd5839a43ebf4ba562ea1 at SHA db488aa7c78e392c788bd5839a43ebf4ba562ea1 preserves the checker trust boundaries; no exploitable security regression found."
  in_scope: true
  scope_reason: "The 42-file (+6178/-5065) pinned delta moves a gate that consumes repository-controlled YAML/JSON/Markdown, git/gh output, paths, and environment-selected tooling, and extends two scanners over a new package; those are input, subprocess, repository-path, and diagnostic-output surfaces. Audit covered the 16 production enforcement files, the full changed-path secret sweep, and the committed clean-pin byte receipt. The surface has prior security controls in harness_boundary and the checker, while this delta itself required fresh review because package loading and scanner reach changed."
  severity_max: low
  findings: []
  must_fix: []
  threat_model:
    - boundary: "Repository-controlled state and git/gh output -> check_state invariant evaluation and terminal diagnostics"
      stride: "T|I|D"
      mitigated: true
    - boundary: "Checker-controlled argv -> subprocesses"
      stride: "T|E"
      mitigated: true
    - boundary: "Repository source tree -> check-plan-routes/check-skill-refs AST and invariant scanners"
      stride: "T|D"
      mitigated: true
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-69-long-file-check-state-package/.harness/harness/features/FEAT-69-long-file-check-state-package/notes/review-harness-security-reviewer-c0.md
```

## Evidence

- `.claude/skills/harness/bin/check-state.py:31-105` fixes import precedence to the entry's own bin directory, resolves the harness root through `harness_boundary`, reconstructs the established argv shape, and imports `check_state` only after that fixed-path bootstrap; the split does not add a user-selected import path.
- `.claude/skills/harness/bin/check_state/ctx.py:239-252` retains the single list-form `subprocess.run(argv, **options)` boundary. The reviewed package contains no `shell=True`, `os.system`, `eval`, or `exec` execution path.
- `.claude/skills/harness/bin/check-plan-routes.py:1899-1944` enumerates only the fixed `check_state/*.py` directory below the supplied repository root, reads source as data, and records unreadable or unparsable members as findings. `.claude/skills/harness/bin/check-skill-refs.py:32-40,95-97` likewise expands only the fixed package path. Neither scanner turns repository text into a command, query, redirect, export, or template.
- The changed-tree credential sweep found no credential material in the production package or feature records; matches outside that surface were synthetic secret-detector fixtures and an environment-variable name in an unrelated manual probe.
- `notes/clean-pin-byte-receipts.md` records 12/13 measurements byte-identical between baseline and pin after root-only normalization; `notes/build-divergences.md` accounts for the five full-table lines as the new feature record and its gitignored run directory, not changed checker behavior. This is identity evidence for the moved input, diagnostic, and subprocess behavior, not merely a green suite claim.
- STRIDE disposition: a contributor able to tamper with these checked repository files already has the ability to alter the checker and its scanners; the delta grants no new privilege. Fixed-root paths and list-form argv prevent path traversal and shell interpretation, diagnostics expose repository paths/errors already emitted by the baseline, and no auth, credential, deserialization-to-code, network-target, redirect, export, or cross-user data boundary was added.
