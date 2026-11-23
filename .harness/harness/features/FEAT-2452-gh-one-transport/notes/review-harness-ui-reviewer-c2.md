# Mode B UI scope check — FEAT-2452-gh-one-transport

**Out of scope:** neither range changes a rendered or interactive design surface. The Python changes affect GitHub transport, caller failure policy, and operator-facing terminal diagnostics, not UI rendering or controls.

Changed-path census at `e282689dd01a1a45eb22f08be67b1e2a9b437fb1`:

| Range to pin | Total | Feature records and evidence | Production Python | Test and support files | Policy and reference Markdown |
|---|---:|---:|---:|---:|---:|
| Fix (`64102016`) | 41 | 33 | 3 | 4 | 1 |
| Whole (`b788e9dac342ee112106a3bc5aa7430d4467cbcb`) | 169 | 139 | 8 | 19 | 3 |

The census found no changed HTML, stylesheet, frontend component, template, or image asset. A direct Git object check found no feature `DESIGN.md` or prototype at the pin. Visual fidelity, accessibility, and light/dark parity are not applicable; no rendered checks were run. No UI findings or open questions.
