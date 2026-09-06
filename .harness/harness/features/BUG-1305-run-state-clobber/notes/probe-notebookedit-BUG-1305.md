# NotebookEdit route probe — BUG-1305

route_reachable: no
guard_fires: n_a

## Observation

The active OMP host exposes no `NotebookEdit` tool in its tool inventory, so no NotebookEdit payload can be issued against `/tmp/bug1305-probe/state.yaml`. The route is refused before a notebook path or payload can reach Harness. Consequently this host cannot address a run `state.yaml` through NotebookEdit, and there is no guard invocation to grade.

No probe file or run directory was created.
