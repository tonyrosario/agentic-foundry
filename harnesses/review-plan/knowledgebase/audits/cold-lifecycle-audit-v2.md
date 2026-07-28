# Cold audit v2: eight-component review lifecycle

- Audit type: cold, independent, read-only
- Reviewer: Terra, medium reasoning
- Date: 2026-07-22
- Scope: only the files directly inside lifecycle component folders `01` through `08`
- Boundary: canonical vendor-neutral specifications/templates; executable runtimes are separate; authority matrix is deployment-populated and deny-by-default

## Verdict

**COHESIVE WITH GAPS**

## Pipeline map

```text
frozen source, plan, and evidence
        ↓
input contract
        ↓
classification and manifest
        ↓
isolated raw reviews and findings
        ↓
canonical adjudication and remediation ledger
        ↓
final-plan re-review and closure
        ↓
implementation
        ↓
diff-time classification, reviews, and conformance
        ↓
exact-revision release gate and human authorization
        ↓
observation and feedback
        ↓
evaluated, versioned lifecycle improvements
```

## Findings

### Blocker: the input-contract primary key has two incompatible names

**Evidence:** `02-review-input-contract/review-input-contract.md` declares `contract_id`; `03-review-run-orchestrator/record-lineage-and-integrity.md` defines the primary ID as `input_contract_id`; every downstream template references `input_contract_id`.

**Consequence:** An implementation following component 2 exactly emits no field that downstream schemas require, so referential-integrity checks cannot be performed without inventing an alias.

**Smallest correction:** Rename component 2’s field to `input_contract_id` everywhere, or formally define `contract_id` as a deprecated exact alias and require both during migration.

### Major: no canonical record-hash algorithm makes the integrity chain interoperable

**Evidence:** `record_sha256`, `manifest_sha256`, `ledger_sha256`, `closure_record_sha256`, and equivalent fields appear throughout components 1–8. `03-review-run-orchestrator/record-lineage-and-integrity.md` requires them to agree but defines neither canonical serialization nor which fields are excluded from self-hashing.

**Consequence:** Two conforming implementations can calculate different hashes for the same logical record, or incorrectly hash the self-referential hash field. Artifact lineage and substitution detection then become implementation-specific.

**Smallest correction:** Add one shared integrity profile: canonical encoding, normalization rules, SHA-256 input definition, excluded/generated fields, and hash scope for referenced artifacts.

### Major: the lens namespace is not canonical despite cross-component use as a key

**Evidence:** `03-review-run-orchestrator/review-suite-selector.md` names `traceability`, `security/privacy`, and `SRE/operational readiness`; `03-review-run-orchestrator/review-manifest.md` uses unconstrained `lens_id`; `03-review-run-orchestrator/build-review-router-skill-prompt.md` uses divergent names such as `requirements/traceability`, `privacy/legal`, and `accessibility/product policy`. Components 4, 6, and 7 use lens IDs for re-review, evaluation, and waiver scope.

**Consequence:** A mandatory lens can be selected, waived, consolidated, evaluated, or checked under nonmatching identifiers. The pipeline could appear complete while a required specialist review was never actually satisfied.

**Smallest correction:** Publish one versioned lens catalog with stable IDs, definitions, allowed consolidation rules, and an explicit deprecated-alias mapping.

### Major: release-gate semantics do not explicitly verify valid plan closure or bind it to the approved-plan hash

**Evidence:** `08-post-implementation-feedback-loop/release-gate-record.md` stores `final_closure_record_id` and `approved_plan_sha256`, but its gates omit “final closure is approved/current and bound to this plan”; its transition rules require only technical/review gates and artifact agreement. `08-post-implementation-feedback-loop/post-implementation-conformance-review.md` says the release gate is created after conformance but does not repair this missing gate.

**Consequence:** A release-gate implementation can mark all listed booleans true and authorize an implementation whose referenced closure is blocked, revoked, superseded, or approves a different plan.

**Smallest correction:** Add a required gate such as `final_plan_closure_valid_and_bound`, require the closure-record hash/status and closure final-plan hash, and mandate equality with `approved_plan_sha256`.

### Moderate: lifecycle rollback and supersession are required narratively but lack complete state transitions

**Evidence:** `03-review-run-orchestrator/lifecycle-state-machine.md` says a rollback “moves to `rolled-back`” and replacement outcome moves to `superseded`; neither is in the normal-transition table. It also says `rolled-back` is nonterminal and needs a new implementation-stage contract but gives no `rolled-back → …` transition.

**Consequence:** State-manager implementations must invent legal origins, authorities, and re-entry targets for rollback or supersession, risking incompatible recovery behavior.

**Smallest correction:** Add explicit transitions to and from `blocked`, `rolled-back`, and `superseded`, including authority and required new contract/classification records.

### Moderate: final closure ambiguously compares the final plan to “the reviewed plan”

**Evidence:** `05-final-closure-gate/final-closure-record.md` separately records `previous_reviewed_plan` and `final_candidate_plan`, then makes approval invalid if “the final candidate hash differs from the reviewed plan hash.” `05-final-closure-gate/final-plan-rereview.md` correctly expects final-plan changes after remediation.

**Consequence:** A literal implementation can make remediation impossible to approve because the final candidate necessarily differs from the previous reviewed plan; another implementation may silently choose a different meaning.

**Smallest correction:** Replace “reviewed plan hash” with “the exact final-review manifest candidate hash”; explicitly allow a prior-ledger plan hash to differ when the final candidate has been reclassified and re-reviewed.

### Moderate: progression after `not-established` is under-specified for non-high-impact unknowns

**Evidence:** `03-review-run-orchestrator/lifecycle-state-machine.md` permits review completion with permitted `not-established` and says lower-impact progression requires policy to record why it is safe. `04-adjudication-remediation-ledger/finding-ledger.md` only explicitly blocks high-impact evidence gaps; no record field captures impact, progression rationale, or required authority for a lower-impact unresolved item.

**Consequence:** A material uncertainty can be marked `not-established`, omitted from confirmed-finding remediation, and pass onward without an auditable safety decision.

**Smallest correction:** Add impact/materiality plus an explicit `progression_basis`, owner/decision ID, and expiry/re-review requirement for every unresolved finding or unknown that does not block.

### Minor: the conformance review lacks a machine-checkable integrity/verdict record

**Evidence:** `08-post-implementation-feedback-loop/post-implementation-conformance-review.md` has prose identity fields and a selectable textual verdict but no `conformance_review_sha256`, artifact-hash schema, or structured verdict/status field. `08-post-implementation-feedback-loop/release-gate-record.md` depends on its `conformance_review_id`.

**Consequence:** Release-gate validators must parse or independently invent conformance validity semantics.

**Smallest correction:** Convert the identity, artifacts, verdict, required-review status, and integrity hash into a normative structured record.

## Component status

| Component | Status | Notes |
|---|---|---|
| 1. Common finding schema | Partial | Strong raw-finding immutability; shares the missing hash profile. |
| 2. Review input contract | Partial | Broadly complete, but its primary-key field breaks downstream compatibility. |
| 3. Orchestrator | Partial | Strong routing and lineage design; missing canonical hash/lens contracts and complete recovery transitions. |
| 4. Adjudication/remediation ledger | Complete | Clear ownership, raw-to-ledger mapping, and requirement-versus-risk semantics. |
| 5. Final closure gate | Partial | Strong hard gates; one material hash-comparison ambiguity. |
| 6. Evaluation/drift harness | Complete | Covers routing, lifecycle integrity, release bypasses, drift, and holdouts well. |
| 7. Human escalation/waiver policy | Complete | Deny-by-default blank authority matrix is appropriate under the stated deployment assumption. |
| 8. Feedback/release loop | Partial | Strong diff-time and learning loop; release binding and conformance structure need tightening. |

## Remaining implementer questions

1. What canonical byte representation and self-hash exclusion rules apply to every record?
2. What is the authoritative, versioned lens-ID registry and alias policy?
3. Exactly which state transitions recover from rollback, revoke approval, or supersede an outcome?
4. What evidence and authority permit a non-high-impact `not-established` item to progress?
5. Must a release gate verify an approved, nonrevoked closure whose final-plan hash equals `approved_plan_sha256`? It should.
6. Is “reviewed plan” in component 5 the prior ledger-reviewed plan or the final-review-manifest candidate? It should be the latter.

## Most consequential issue

The `contract_id` versus `input_contract_id` mismatch is the most consequential issue. It breaks the fundamental foreign key linking every downstream record to the frozen input contract.
