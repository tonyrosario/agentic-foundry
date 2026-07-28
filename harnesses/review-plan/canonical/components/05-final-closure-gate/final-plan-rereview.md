# Template: final-plan re-review

## Role

Review the exact final candidate plan after adjudicated feedback has been integrated. Approval of an earlier version does not carry forward. Produce a [versioned final-closure record](final-closure-record.md); prose alone cannot approve a plan.

## Required inputs

- Lifecycle ID and final-review input-contract ID.
- Authoritative-source-bundle ID, version, path, and hash.
- Previous reviewed-plan path, version, and hash.
- Final candidate-plan path, version, and hash.
- Canonical finding-ledger ID, version, and hash.
- Classification and review-manifest IDs for the final candidate.
- Semantic changed-surface/revision manifest.
- Completed required re-review IDs and hashes.
- Exact human decision and waiver record IDs, versions, hashes, authority-matrix bindings, conditions, scope, and expiry.
- Current evidence manifest: repository SHA, authoritative documents, tests, rehearsals, and external evidence.

Reject dispatch if artifacts do not resolve to one lifecycle or if required hashes, ledger mappings, or authority records are missing.

## Closure distinction

Do not conflate an unmet source requirement with accepted residual risk.

- A mandatory source criterion must be `met` by the final plan.
- If intent changes, the authorized owner must update and version the source contract; the revised source and plan must then be reclassified and re-reviewed.
- A source-requirement defect cannot be waived, accepted as residual risk, or deferred while still receiving approval.
- A genuine residual risk may remain only under a valid, scoped component-7 risk acceptance whose conditions are satisfied.
- A non-material follow-up may be deferred only when it is not required for a source criterion, policy gate, or claimed plan outcome.

## Method

1. Reconstruct every authoritative source-contract success criterion.
2. Verify the authoritative-source-bundle hash and identify any authorized source revision since initial review.
3. Inspect semantic changes between the previously reviewed and final plans.
4. Re-run traceability across the complete final plan.
5. Verify every raw finding maps into the canonical ledger and every required failed or `not-established` review execution maps to an unresolved-review ledger item.
6. Verify each confirmed ledger finding and unresolved-review execution under its type-specific closure rule.
7. Validate every decision and waiver against exact scope, artifacts, authority, conditions, expiry, and invalidation triggers.
8. Confirm all changed or newly triggered specialist lenses ran against the final candidate.
9. Verify every classifier-selected lens remains visible, every validly waived lens retains its waiver, and every unwaived selected lens appears in and completes the execution-required set.
10. Attempt at least one new counterexample against the combined revision.
11. Confirm commands, source locations, assumptions, repository state, and external facts remain current.
12. Bind the verdict to the exact source bundle, final-plan, ledger, evidence, policy, classifier, and review-manifest hashes.

## Output

Select one verdict:

- `FINAL PLAN APPROVED`
- `FINAL PLAN APPROVED WITH ACCEPTED RESIDUAL RISKS`
- `FINAL PLAN REQUIRES REVISION`
- `FINAL PLAN BLOCKED`
- `FINAL PLAN NOT ESTABLISHED`

`APPROVED WITH ACCEPTED RESIDUAL RISKS` is allowed only when every source criterion is met and each remaining risk has a valid risk-acceptance record. It cannot cover an unmet criterion, missing mandatory review, invalid waiver, or high-impact unknown.

Produce:

1. A completed `final-closure-record.md`.
2. Source-criteria status matrix.
3. Finding-closure matrix with raw-to-ledger mapping.
4. New regressions or contradictions.
5. Remaining residual risks, owners, controls, expiry, and monitoring.
6. Facts and evidence that must be revalidated at implementation time.
