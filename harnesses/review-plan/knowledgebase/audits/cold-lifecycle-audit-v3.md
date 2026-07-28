# Cold audit v3: eight-component review lifecycle

- Audit type: cold, independent, read-only
- Reviewer: Terra, medium reasoning
- Date: 2026-07-22
- Scope: only the files directly inside lifecycle component folders `01` through `08`
- Boundary: canonical vendor-neutral specifications/templates; executable runtimes are separate; authority matrix is deployment-populated and deny-by-default

## Verdict

**COHESIVE WITH GAPS**

## Pipeline map

```text
frozen input contract
      ↓
risk classification and lens manifest
      ↓
immutable raw reviews and findings
      ↓
adjudicated remediation ledger
      ↓
exact-plan final closure
      ↓
implementation diff classification and conformance
      ↓
exact-revision human release authorization
      ↓
outcome observation and feedback
      ↓
evaluated pipeline improvements
```

The intended ownership boundaries are generally clear: component 2 freezes inputs; component 3 routes and transitions; component 4 adjudicates and remediates; component 5 closes plans; component 7 authorizes human exceptions and releases; component 8 verifies implementation and outcomes; component 6 controls changes to the pipeline.

## Findings

### Major: a required review can be `not-established` yet still allow plan closure

**Evidence:**

- `03-review-run-orchestrator/lifecycle-state-machine.md`, “Normal transitions”: `reviews-running → reviews-complete` permits every assignment to be “completed, validly waived, or permitted `not-established`.”
- `03-review-run-orchestrator/review-manifest.md`, “Validation rules,” similarly permits `not-established` while saying unresolved items default to blocking.
- `04-adjudication-remediation-ledger/finding-ledger.md` requires mapping raw `finding_id` values but does not require a ledger unresolved item for a required review execution that produced no finding because it was `not-established`.
- `05-final-closure-gate/final-closure-record.md` blocks a missing mandatory review but does not expressly treat a present `not-established` review as incomplete.

**Consequence:** A reviewer may lack essential evidence or isolation, emit no findings, and be counted as a completed required review. With no mandated ledger item, the ledger can reach `ready-for-final-review` and closure can approve despite the required lens never establishing its result.

**Smallest correction:** Require every required `not-established` review execution to create a canonical unresolved ledger item keyed to its `review_id` and `review_execution_id`. Final closure must treat it as blocking unless it has the same fully populated, valid nonblocking progression decision required for unresolved findings.

### Major: multi-artifact authoritative intent is lost in downstream schemas

**Evidence:**

- `02-review-input-contract/review-input-contract.md` models `artifacts.source_contract` as an array and requires every artifact defining outcomes to be identified.
- `01-common-finding-schema/review-record.md`, `03-review-run-orchestrator/classification-record.md`, `03-review-run-orchestrator/review-manifest.md`, `04-adjudication-remediation-ledger/finding-ledger.md`, `05-final-closure-gate/final-closure-record.md`, and `08-post-implementation-feedback-loop/post-implementation-conformance-review.md` each model a singular `source_contract` reference or hash.

**Consequence:** A lifecycle whose intent consists of a ticket plus an ADR plus an approved decision cannot be completely and consistently bound by downstream records. An implementation could hash only one source artifact and still satisfy their schemas, losing authority, requirements, or conflict provenance.

**Smallest correction:** Define a canonical authoritative-source bundle/manifest with its own hash and enumerated artifact references, then require every downstream record to bind that bundle hash—or use the component-2 source-artifact array consistently.

### Major: human authority decisions and release authorization are not hash-bound to the authority configuration or gate record

**Evidence:**

- `07-human-escalation-waiver-policy/authority-matrix.md` says the matrix must be populated and versioned and its changes require revalidation. Its template has no matrix ID, version, or self-hash fields.
- `07-human-escalation-waiver-policy/escalation-and-decision-record.md` and `risk-waiver-record.md` include an `authority_source` string but do not bind an authority-matrix version or hash.
- `08-post-implementation-feedback-loop/release-gate-record.md` stores `authority.release_decision_id` but not the decision-record hash.
- `07-human-escalation-waiver-policy/escalation-and-decision-record.md` stores `release_gate_record_id` but not that release gate’s hash.

**Consequence:** The system cannot prove which versioned delegation authorized a decision or immutably bind a release decision to one exact release-gate record. A stale, altered, or ambiguously resolved authority/decision record can be accepted while superficially matching IDs and revision fields.

**Smallest correction:** Version and self-hash the authority matrix; add `authority_matrix_id`, version, and SHA-256 to decision and waiver records. Add reciprocal decision-record and release-gate-record hashes to release authorization references and require exact resolution under the integrity profile.

### Moderate: the router-build prompt contradicts the canonical manifest’s waived-lens semantics

**Evidence:**

- `03-review-run-orchestrator/build-review-router-skill-prompt.md` states “required lenses = … − explicit valid waivers.”
- `03-review-run-orchestrator/review-manifest.md` says a waived lens remains in `required_lenses`.
- `07-human-escalation-waiver-policy/human-escalation-and-waiver-policy.md` says a review waiver cannot delete the lens from the manifest.

**Consequence:** An engineer following the router-build prompt exactly may remove waived mandatory lenses from `required_lenses`, contrary to the canonical manifest and feedback/evaluation requirement to preserve waived coverage. This weakens auditability and waiver-outcome measurement.

**Smallest correction:** Define two sets: `selected_lenses` as the union without subtraction and `execution_required_lenses` as selected lenses minus valid waivers. Require the manifest to retain all selected lenses with waiver status.

## Component status

| Component | Status | Reason |
|---|---|---|
| 1. Common finding schema | Partial | Strong immutable finding/review model, but singular source binding conflicts with component 2’s multi-source contract. |
| 2. Review input contract | Partial | Comprehensive and enforceable at intake; downstream cannot fully preserve its authoritative source set. |
| 3. Review orchestrator | Partial | Excellent lineage, state, routing, and recovery rules; `not-established` review handling and waiver-set semantics are incomplete or contradictory. |
| 4. Adjudication/remediation ledger | Partial | Clear ownership and type-specific closure; it does not require recording failed-to-establish required reviews as unresolved items. |
| 5. Final closure gate | Partial | Strong exact-plan and requirement-versus-risk gates; it relies on missing upstream representation of `not-established` required reviews. |
| 6. Evaluation/drift harness | Complete | Covers deterministic integrity, semantic evaluation, isolation, adapters, regressions, holdouts, promotion, and rollback. |
| 7. Human escalation/waiver policy | Partial | Good deny-by-default policy and waiver rules, but authority configuration and decisions lack versioned cryptographic bindings. |
| 8. Post-implementation feedback loop | Complete | Coherent diff-time, conformance, release, outcome, feedback, and learning cycle, subject to upstream authority and review-state gaps. |

## Remaining implementer questions

1. Is an authoritative source set intended to be a generated immutable bundle, or must every downstream record repeat every source artifact?
2. Which entity must create and own a ledger item when a required reviewer returns `not-established` without a finding?
3. Are decision and waiver records append-only versions? If so, what are their supersession links, and how do consumers resolve the exact authoritative version?
4. What is the canonical authority-matrix identity, version, and hash, and how is it attached to every authorization?
5. Should a waived lens remain selected but non-executing, as components 3 and 7 say, or be removed from the required set, as the router-build prompt says?

## Most consequential issue

A required review that returns `not-established` can be treated as complete without a mandatory unresolved ledger item, allowing final approval even though the required lens never established whether the plan is safe or sufficient.
