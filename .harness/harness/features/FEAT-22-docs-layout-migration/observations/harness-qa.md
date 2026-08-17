# Observations — harness-qa — FEAT-22

- 2026-08-16: run 13 (extension probe, pinned e26e628). test-check-domain.py's ROOT
  constant is hardcoded (`os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))`,
  no env-var escape like `CHECK_DOMAIN_BIN` provides for the binary), so the live-tree
  resolve assertion can never be re-pointed at a mutated team-config.yaml without editing
  the test file itself — a structural reason the live refused-direction case has stayed
  unprobed across four review rounds, not just an oversight.
