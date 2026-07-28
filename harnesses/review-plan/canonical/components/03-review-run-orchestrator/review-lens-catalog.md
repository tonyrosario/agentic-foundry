# Canonical review-lens catalog

## Catalog identity

```yaml
lens_catalog_id: "canonical-plan-review-lenses"
lens_catalog_version: "1.0"
```

Machine-readable lifecycle records MUST use the stable IDs in this catalog. Human-readable labels may vary, but they cannot serve as keys.

## Stable lens IDs

| Stable ID | Purpose | Typical evidence |
|---|---|---|
| `independent-outcome` | Judge whether the plan achieves the authoritative source outcome without inheriting the drafter’s framing | Source contract first, then exact plan and declared dependencies |
| `grounded-feasibility` | Verify repository, API, dependency, environment, and implementation assumptions | Pinned repository, authoritative docs, build/test evidence |
| `requirements-traceability` | Map every authoritative criterion through plan commitment and verification | Source criteria, plan locations, acceptance checks |
| `adversarial-falsification` | Construct plausible executions that pass stated checkpoints while missing the intended result | Source, plan, checkpoints, failure models |
| `verification-quality` | Judge whether tests and checks discriminate success from important failures | Test plan, executable checks, oracles, negative cases |
| `security` | Review authentication, authorization, secrets, tenancy, untrusted input, and trust boundaries | Threat model, permission model, interfaces, code/config |
| `privacy-legal` | Review sensitive data, retention, consent, legal, contractual, and policy obligations | Data maps, policies, counsel/owner decisions, controls |
| `data-migration` | Review schemas, state transitions, backfills, reconciliation, invariants, and recovery | Schemas, migration sequence, data volumes, rehearsal evidence |
| `interface-compatibility` | Review public/cross-team APIs, schemas, queues, protocols, versioning, and mixed-version behavior | Contracts, consumers, compatibility tests, rollout windows |
| `sequencing-reversibility` | Review dependencies, ordering, hold points, rollback, recovery, and irreversibility | Phase graph, preconditions, rollback/recovery evidence |
| `operational-readiness` | Review deployment, observability, SLOs, capacity, degradation, ownership, and incident response | Runbooks, metrics, alerts, capacity model, rollout controls |
| `performance-cost` | Review workload assumptions, latency, throughput, resource use, and spend | Workload model, benchmarks, budgets, capacity/cost evidence |
| `accessibility-product-policy` | Review accessibility, user-segment effects, and product-policy obligations | UX behavior, accessibility criteria, policy and user evidence |
| `prototype-rehearsal` | Determine whether uncertainty requires a prototype, migration rehearsal, load test, or failure drill | Risk hypothesis, experiment plan, rehearsal results |
| `final-plan-rereview` | Re-review the exact revised plan, finding closure, and newly introduced risks | Final plan, prior plan, ledger, decisions, current evidence |
| `implementation-conformance` | Compare actual implementation and rollout with the approved plan and source outcome | Exact diff, plan, closure, tests, rollout/monitoring evidence |

## Alias migration

Aliases are accepted only at ingestion and MUST be normalized before classification or manifest validation.

| Deprecated/human label | Canonical result |
|---|---|
| `independent outcome` | `independent-outcome` |
| `grounded feasibility` | `grounded-feasibility` |
| `traceability` | `requirements-traceability` |
| `requirements/traceability` | `requirements-traceability` |
| `adversarial falsification` | `adversarial-falsification` |
| `verification quality` or `verification-quality` | `verification-quality` |
| `security/privacy` | Expand to both `security` and `privacy-legal`; never choose one silently |
| `privacy/legal` | `privacy-legal` |
| `data/migration` | `data-migration` |
| `interface/compatibility` | `interface-compatibility` |
| `sequencing/reversibility` | `sequencing-reversibility` |
| `SRE/operational readiness` | `operational-readiness` |
| `performance/cost` | `performance-cost` |
| `accessibility/product policy` | `accessibility-product-policy` |
| `prototype/rehearsal` | `prototype-rehearsal` |
| `final re-review` or `final-plan re-review` | `final-plan-rereview` |
| `post-implementation conformance` | `implementation-conformance` |

Unknown aliases are invalid. Do not perform fuzzy matching in decision-critical records.

## Consolidation rules

Several lens IDs may share one reviewer execution only when the review manifest preserves every ID, evidence need, exit criterion, and finding attribution separately.

Default compatible execution groups are:

- `independent-outcome` plus `requirements-traceability` for low/normal risk when independence is preserved.
- `grounded-feasibility` plus `verification-quality` when both use the same repository and test evidence.
- `sequencing-reversibility` plus `operational-readiness` for bounded deployment plans.

Do not consolidate away required specialist independence for Tier 2/3 `security`, `privacy-legal`, `data-migration`, payments-related policy, or another policy-designated domain. `security/privacy` always expands to two lens requirements even if one authorized specialist execution later covers both.

## Versioning and removal

- Stable IDs are never silently renamed or reused for a different purpose.
- Additive lenses require a new minor catalog version.
- Meaning changes, splits, merges, or removals require a new major version plus explicit migration mappings.
- Manifests, findings, waivers, ledgers, evaluation cases, and feedback records retain the catalog version used when they were created.
- A deprecated alias cannot appear in a newly validated machine-readable record.

