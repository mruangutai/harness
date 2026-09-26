# FEAT-66 — build amendment (DEC-174 main-session-direct; the main session is the engineering lead of this build)

Recorded with `plan-merge.py record-amendments`. Ledger: notes/build-divergences.md D-04.

```yaml
VERDICT: PASS
DIGEST:
  amendments:
  - task: T-01
    field: files
    was:
    - .claude/skills/harness/bin/check-domain.py#shape_problems
    - .claude/skills/harness/bin/validate-digest.py#validate
    - .claude/skills/harness/bin/plan-merge.py#apply_merge
    - &id001
      path: tests/integration/test-check-domain.py
      quote: '#!/usr/bin/env python3'
    - &id002
      path: tests/integration/test-check-domain-artifact.py
      quote: '#!/usr/bin/env python3'
    - &id003
      path: tests/integration/test-check-domain-claims.py
      quote: '#!/usr/bin/env python3'
    - &id004
      path: tests/integration/test-check-domain-grant.py
      quote: '#!/usr/bin/env python3'
    - &id005
      path: tests/integration/test-check-domain-post.py
      quote: '#!/usr/bin/env python3'
    - &id006
      path: tests/integration/test-check-domain-worktree-parity.py
      quote: '#!/usr/bin/env python3'
    - &id007
      path: tests/integration/test-check-domain-worktree.py
      quote: '#!/usr/bin/env python3'
    - &id008
      path: tests/integration/test-check-domain-approval.py
      quote: '#!/usr/bin/env python3'
    - &id009
      path: tests/unit/test-config-shape-matrix.py
      quote: '#!/usr/bin/env python3'
    - &id010
      path: tests/integration/test-plan-merge.py
      quote: '#!/usr/bin/env python3'
    - &id011
      path: tests/integration/test-validate-digest.py
      quote: '#!/usr/bin/env python3'
    - tests/integration/test-validate-digest-shadows.py
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/clean-pin-byte-receipts.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/build-divergences.md
    now:
    - .claude/skills/harness/bin/check-domain.py#shape_problems
    - .claude/skills/harness/bin/validate-digest.py#validate
    - .claude/skills/harness/bin/plan-merge.py#apply_merge
    - *id001
    - *id002
    - *id003
    - *id004
    - *id005
    - *id006
    - *id007
    - *id008
    - *id009
    - *id010
    - *id011
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/clean-pin-byte-receipts.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/build-divergences.md
    reason: the suite exists only untracked in the operator's main checkout; it is on neither origin/main nor this branch (ledger D-04)
  - task: T-01
    field: verify
    was: 'python3 tests/integration/test-check-domain.py &&
  
      python3 tests/integration/test-check-domain-artifact.py &&
  
      python3 tests/integration/test-check-domain-claims.py &&
  
      python3 tests/integration/test-check-domain-grant.py &&
  
      python3 tests/integration/test-check-domain-post.py &&
  
      python3 tests/integration/test-check-domain-worktree-parity.py &&
  
      python3 tests/integration/test-check-domain-worktree.py &&
  
      python3 tests/integration/test-check-domain-approval.py &&
  
      python3 tests/unit/test-config-shape-matrix.py &&
  
      python3 tests/integration/test-plan-merge.py &&
  
      python3 tests/integration/test-validate-digest.py &&
  
      python3 tests/integration/test-validate-digest-shadows.py &&
  
      python3 -c ''import importlib.util,pathlib,subprocess,sys; root=pathlib.Path("."); spec=importlib.util.spec_from_file_location("feat66_code_grade",root/".claude/skills/harness/bin/code_grade.py"); grade=importlib.util.module_from_spec(spec); sys.modules[spec.name]=grade; spec.loader.exec_module(grade); pairs=[(".claude/skills/harness/bin/check-domain.py","shape_problems"),(".claude/skills/harness/bin/validate-digest.py","validate"),(".claude/skills/harness/bin/plan-merge.py","apply_merge")]; base={p:{r.qualname for r in grade.grade_source(subprocess.check_output(["git","show","cb6f80505721292c0c799cf03b0af6b180ba2970:"+p],text=True),p)} for p,d in pairs}; records=[(p,d,r) for p,d in pairs for r in grade.grade_source((root/p).read_text(),p) if r.qualname==d or r.qualname not in base[p]]; bad=[(p,r.qualname,r.grade) for p,d,r in records if r.grade<4 and r.grade!=2]; print("FEAT-66 grades",[(p,r.qualname,r.grade) for p,d,r in records]); sys.exit(1 if not records or bad else 0)''
  
      '
    now: 'python3 tests/integration/test-check-domain.py &&
  
      python3 tests/integration/test-check-domain-artifact.py &&
  
      python3 tests/integration/test-check-domain-claims.py &&
  
      python3 tests/integration/test-check-domain-grant.py &&
  
      python3 tests/integration/test-check-domain-post.py &&
  
      python3 tests/integration/test-check-domain-worktree-parity.py &&
  
      python3 tests/integration/test-check-domain-worktree.py &&
  
      python3 tests/integration/test-check-domain-approval.py &&
  
      python3 tests/unit/test-config-shape-matrix.py &&
  
      python3 tests/integration/test-plan-merge.py &&
  
      python3 tests/integration/test-validate-digest.py &&
  
      python3 -c ''import importlib.util,pathlib,subprocess,sys; root=pathlib.Path("."); spec=importlib.util.spec_from_file_location("feat66_code_grade",root/".claude/skills/harness/bin/code_grade.py"); grade=importlib.util.module_from_spec(spec); sys.modules[spec.name]=grade; spec.loader.exec_module(grade); pairs=[(".claude/skills/harness/bin/check-domain.py","shape_problems"),(".claude/skills/harness/bin/validate-digest.py","validate"),(".claude/skills/harness/bin/plan-merge.py","apply_merge")]; base={p:{r.qualname for r in grade.grade_source(subprocess.check_output(["git","show","cb6f80505721292c0c799cf03b0af6b180ba2970:"+p],text=True),p)} for p,d in pairs}; records=[(p,d,r) for p,d in pairs for r in grade.grade_source((root/p).read_text(),p) if r.qualname==d or r.qualname not in base[p]]; bad=[(p,r.qualname,r.grade) for p,d,r in records if r.grade<4 and r.grade!=2]; print("FEAT-66 grades",[(p,r.qualname,r.grade) for p,d,r in records]); sys.exit(1 if not records or bad else 0)''
  
      '
    reason: the suite exists only untracked in the operator's main checkout; it is on neither origin/main nor this branch (ledger D-04)
artifact: .harness/harness/features/FEAT-66-complex-function-drivers/notes/build-divergences.md
```
