# Ruling: canonical-reader inventory relocation before the PR — FEAT-2452 — 2026-11-23

Ruled by fable-advisor (AdvisorD7Inventory), which holds the operator's delegated approval. Full text: agent://AdvisorD7Inventory.

- **Finding:** CI's `Canonical-reader audit` step exited 2 at e20e6f67 and 0 at base b788e9da. T-02 moved three gh-sync reads into helpers (`_feature_doc`, `_merged_pull_requests`, `_replacement_number`). T-04 moved wayfind's decode into `factory_gh._decode_gh_json`, which already has a canonical row.
- **Ruling:** APPROVE as a pre-PR conformance fix. No `--kind amendment` judgement: adding the file to T-02/T-04 `files` would falsify provenance, since no builder edited it. Validate is not reopened: no gate validate ran failed, and no executable line changes.
- **Edit:** three rows relocated (id and symbol only) and the wayfind `gh_json` row deleted. Disposition, remedy, category and `task` provenance are unchanged.
- **Receipts:**
  - `notes/ci-canonical-reader-audit.txt`: exit 0, "0 unresolved reader site(s) across 101 Python file(s)";
  - `notes/ci-test-check-plan-routes.txt`: ALL PASS.
- **Host-only reds in the local CI run:**
  - pip PEP 668: Homebrew's externally-managed macOS Python versus the ubuntu-latest system python. CI deliberately has no setup-python (tests.yml:80).
  - check-state INV-29: the standing Kaya worktree on this host.
