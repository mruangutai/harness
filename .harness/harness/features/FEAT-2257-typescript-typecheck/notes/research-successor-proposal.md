decisions:
- id: D-01
  choice: Permit active typecheck detection of tests/manual sources solely for static checking while normal runners remain forbidden to execute manual probes
  because: Full tracked-source coverage must include manual TypeScript without treating nondeterministic credentialled probes as CI tests
  dec: DEC-213
