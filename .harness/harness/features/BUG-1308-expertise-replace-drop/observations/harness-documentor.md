# Observations - harness-documentor

- 2026-09-05 (BUG-1308 T-04): dispatch said regenerating DECISIONS-INDEX.md was mandatory because appending an entry "shifts every later row source anchor" - false for an EOF append: the index diff was one added line, no earlier @line moved. Regeneration is still mandatory, but because the generator is the only thing that emits the new row and its RULING PENDING sentinel.
- 2026-09-05 (BUG-1308 T-04): the bash-write-guard blocks a shell redirect into a mktemp -d path (reported the target as "xx"); scratch fixtures for a smoke run had to be created with a python3 heredoc writing an explicit /tmp path instead.
