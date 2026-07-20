# Example lifecycle model — L5 · manage-dev-env

*A worked lifecycle model. Keep the shape; swap in this repo's tools. One repo's illustrative instantiation.*

## Purpose

The dev machine itself is a resource: disk, compute, the toolchain, the container-runtime VM. L5 manages
its health — responding to disk and compute pressure, installing dev dependencies, keeping the VM sized.

## Healthy baseline

- Disk and compute have headroom; dispatch isn't being refused on a resource floor.
- Under compute pressure the load-shed is *expected behaviour*, not a bug — heavy work backs off at RED.
- The toolchain is present; the container-runtime VM is sized for the heaviest local build.

## Symptom classes → resolving docs (Part B fills the doc column)

| Symptom class (what you observe) | Resolving doc / action (yours) |
|---|---|
| Dispatch refused on a low-disk floor | *your* reclaim procedure (see `runbook-reclaim-a-full-disk.md`) — TRIM before prune |
| Host under RED compute pressure — heavy work shed | at YELLOW dispatch fewer heavy agents; RED shed is expected, not a failure |
| A host tool vanished mid-session | re-establish the binary per your host notes |
| The VM rootfs is too small for a local build | recreate with the larger root disk (mind the right sizing flag) |

## Owned runbooks

- **respond-to-disk-pressure** — reclaim disk when dispatch refuses (see the runbook).
- **respond-to-compute-pressure** — the load-shed dynamics (RED → shed heavy work).
- **respond-to-new-dep-need** — install a dev dependency into the venv/image (persist it in the manifest).

## Observability surface

The host disk (on the 2–3 sites that grow) + the compute-pressure probe (GREEN/YELLOW/RED) + the VM's own
status. A refusal signal that doesn't say *which* resource is low is itself a gap — make it name the floor.
