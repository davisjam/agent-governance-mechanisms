# Example lifecycle model — L4 · manage-deploy

*A worked lifecycle model. Keep the shape; swap in this repo's tools. One repo's illustrative instantiation.*

## Purpose

Shipping is the resource L4 manages: the staged path from local → staging → prod, hotfix discipline,
triaging a prod bug report, and monitoring the running system. Not every step here converts to a
runnable — RCA correctly stays judgment.

## Healthy baseline

- A staged deploy reaches green through its gates (build, tests, smoke, canary, promote) without hand-holding.
- Hotfixes are cherry-picked onto a branch from the *deployed tag* — never a deploy of HEAD.
- Prod is monitored; a bug report has a reproduce-first, test-first path (reproduce locally before a remote
  redeploy).

## Symptom classes → resolving docs (Part B fills the doc column)

| Symptom class (what you observe) | Resolving doc / action (yours) |
|---|---|
| Driving a deploy to green (local / staging / prod) | *your* deploy runbook (separate agents per stage; confirm the pre-launch gate) |
| Deploy smoke hangs on ONE case, others passed | re-send that one case at the live deployment; don't re-run the whole deploy |
| A prod/staging bug report from a user | reproduce-before-fix, test-first; reproduce *locally* first (faster; a non-repro is itself a clue) |
| Hotfixing prod (must not ship HEAD) | cherry-pick onto a branch from the deployed *tag* |

## Owned runbooks

- **local→staging→prod** — the staged deploy (often already runnable).
- **hotfix-from-tag** — cherry-pick onto a tag-branch; never deploy HEAD.
- **triage-new-issue** — prod bug → RCA (judgment) → routed fix.

## Observability surface

The deploy log's heartbeat / phase markers + the build system + post-deploy smoke; for a bug report, the
reliably-distinct signal *before* naming a cause (RCA is judgment-heavy — give it your strongest model).
