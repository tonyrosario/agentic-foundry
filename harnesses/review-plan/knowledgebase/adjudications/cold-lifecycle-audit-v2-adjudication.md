# Adjudication of cold lifecycle audit v2

- Source audit: `cold-lifecycle-audit-v2.md`
- Adjudicated: 2026-07-22
- Result: all eight findings confirmed; finding 7 confirmed with a wording qualification

## Dispositions

| Finding | Disposition | Correction |
|---|---|---|
| `contract_id` versus `input_contract_id` | Confirmed | Standardized the component-2 primary key and all handoffs on `input_contract_id`. |
| Missing canonical record-hash algorithm | Confirmed | Added `canonical-json-sha256-v1`, canonical JSON/self-hash exclusion rules, exact-file and bundle hashing, validation, and profile versioning; schemas now declare the profile. |
| Noncanonical review-lens namespace | Confirmed | Added a versioned stable lens catalog, alias/expansion rules, consolidation rules, and catalog-version bindings; normalized emitted lens IDs. |
| Release gate did not validate final closure | Confirmed | Added closure record hash/status/currentness/final-plan binding and the mandatory `final_plan_closure_valid_and_bound` gate. |
| Rollback/supersession transitions incomplete | Confirmed | Added explicit blocking, recovery, rollback, supersession, cancellation, re-entry, authority, and terminal-state transitions. |
| “Reviewed plan hash” ambiguous | Confirmed | Bound closure to the exact final-review-manifest candidate hash and explicitly allowed a different pre-remediation plan after reclassification/re-review. |
| `not-established` progression underspecified | Confirmed with qualification | Severity already existed, but progression authority did not. Added default blocking plus materiality, basis, decision, owner, expiry, and re-review fields across classification, manifest, ledger, closure, state, and conformance. |
| Conformance lacked a machine-checkable record | Confirmed | Replaced mixed prose with a normative structured conformance record, self-hash, exact artifacts, status/verdict, hard gates, unknown handling, and release binding. |

## Verification

The revised templates passed checks for:

- exactly one H1 and balanced fenced blocks per component Markdown file;
- local Markdown-link resolution;
- trailing whitespace;
- absence of the deprecated bare `contract_id` field;
- required integrity-profile and self-hash fields;
- canonical lens-catalog references;
- explicit rollback/supersession recovery transitions;
- exact final-review candidate binding;
- final-closure and conformance release predicates;
- auditable progression fields for unresolved items.

## Current status

All v2 findings have written corrections. The revised pipeline has not yet received a third cold semantic audit.
