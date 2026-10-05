# Security-reviewer distillation recovery — FEAT-1928

**PASS — three repository-tier security invariants are durable, genuinely new, and proposed below; no Expertise file was mutated and no checker or review execution was run.**

## Sourced candidates and judgments

1. **Accept / add P-07.** `notes/review-harness-security-reviewer-final.md` establishes that privileged digest append authority is bound to hook-owned runtime identity, one open registered run, the manifest-authorized exact destination, and descriptor-relative anti-symlink/append checks. This is a durable repository trust-boundary invariant not covered by current repository Expertise.
2. **Accept / add P-08.** `notes/review-harness-security-reviewer-append.md` establishes that append safety includes successor visibility: the canonical historical reader must select the exact prospective suffix before any bytes are written, and refusal preserves existing prose and bytes. Existing Expertise covers strict invariants and structured routing generally, but not this repository's canonical append-selection invariant.
3. **Accept / add P-09.** `notes/review-harness-security-reviewer-finalmerge.md` establishes that cold-revival identity comes only from host-persisted initial assignment plus runtime lineage, never later messages or tool output, and an unreclaimable governed persona is held rather than silently treated as ungoverned. This trust-source rule is not covered by the existing cache-authorization pattern.

Rejected candidates: none among the three sourced candidates. The final-merge receipt's placement-cache mechanics were not split into a fourth candidate because craft P-15 already covers successful-only caching and per-operation authorization.

## Proposed operations (not applied)

```yaml
expertise_update:
  - op: add
    target: P-07
    section: Patterns
    entry: "WHEN auditing privileged digest append in this repository DO verify hook-owned child, parent, feature, and checkout identity resolves to one open registered run whose manifest grants the exact destination, then require descriptor-relative `O_NOFOLLOW`, a regular writable leaf, and `O_APPEND`."
    why: "Repository layer; durable authorization invariant sourced to notes/review-harness-security-reviewer-final.md."
  - op: add
    target: P-08
    section: Patterns
    entry: "WHEN auditing `validate-digest.py` append visibility DO require `digest_record.last_fenced_mapping` to select the exact safe-dumped object from existing bytes plus the would-be suffix before any write; refusal must leave human prose and all bytes unchanged."
    why: "Repository layer; durable canonical-reader invariant sourced to notes/review-harness-security-reviewer-append.md."
  - op: add
    target: P-09
    section: Patterns
    entry: "WHEN auditing cold revival in this repository DO accept identity only from host-persisted `session_init` assignment plus runtime lineage, never later messages or tool output; a known governed persona that cannot reclaim must be held rather than silently treated as ungoverned."
    why: "Repository layer; durable identity-source invariant sourced to notes/review-harness-security-reviewer-finalmerge.md."
```

Repository Patterns would move from 5 to 8 if applied; Gotchas remain 9, Outcomes 1, Open 0. Craft Expertise remains unchanged at Patterns 15, Gotchas 15, Outcomes 10, Open 0. All three named artifacts retain their historical PASS dispositions and their explicit closed/not-downgraded findings; no historical BLOCKED verdict appears in them, and none was invented or reclassified.

Open questions: none.
