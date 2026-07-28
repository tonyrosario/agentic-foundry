# Cold audit: eight-component review lifecycle

- Audit type: cold, independent, read-only
- Reviewer: Terra, medium reasoning
- Date: 2026-07-22
- Scope: only the files directly inside lifecycle component folders `01` through `08`

## Verdict

**NOT COHESIVE**

## Pipeline map

```text
input contract
      ↓
classify and select review lenses
      ↓
review records
      ↓
adjudicate and remediate
      ↓
final-plan re-review
      ↓
implementation and diff-time conformance
      ↓
feedback events
      ↓
evaluation and promotion
```

Components 2 and 6–8 describe this well, but components 3–5 do not provide the authoritative records and enforceable transitions needed to join it.

## Findings

### Blocker: no canonical lifecycle records connect review, adjudication, and closure

Component 2 requires every output to trace to a contract and says to store the contract ID in every review record and ledger (`02-review-input-contract/review-input-contract.md`, “Assembly procedure,” lines 262–273). The component-1 review record has no `input_contract_id`, schema version, policy version, classification ID, or review-manifest ID (`01-common-finding-schema/review-record.md`, lines 3–68).

Component 4 only lists ledger fields in an adjudicator prompt, with no ledger record/schema, ledger ID, artifact hash, version, or state transitions (`04-adjudication-remediation-ledger/finding-adjudicator.md`, “Canonical ledger fields,” lines 25–39). Component 8 nevertheless requires `adjudication_ledger_id` and `final_closure_record_id` (`08-post-implementation-feedback-loop/feedback-event-record.md`, lines 14–26).

**Consequence:** Implementations must invent identity, versioning, and referential-integrity semantics; later stages cannot prove they closed findings from the reviewed artifacts.

**Smallest correction:** Define versioned machine-readable `review_record`, `finding_ledger`, and `final_closure_record` schemas, all carrying `input_contract_id`, artifact hashes, policy/classifier IDs, stable finding IDs, ownership, and permitted state transitions.

### Blocker: the final gate contradicts the waiver/specification policy and can approve an unmet requirement

The final-review template allows every confirmed finding to be “resolved or explicitly accepted/deferred” (`05-final-closure-gate/final-plan-rereview.md`, line 18) and offers `FINAL PLAN APPROVED WITH ACCEPTED RISKS` (lines 27–32).

Component 7 explicitly says a specification decision changes the source contract and “a deferral does not make a mandatory requirement complete” (`07-human-escalation-waiver-policy/human-escalation-and-waiver-policy.md`, line 81); it also forbids using a waiver to relabel an unmet requirement as complete (line 273).

**Consequence:** A plan can pass closure by accepting or deferring a finding that represents an unmet source requirement, defeating the stated purpose.

**Smallest correction:** Require closure to distinguish residual-risk acceptance from source-requirement change. Block approval whenever an authoritative criterion is unmet unless the source contract is separately versioned and re-reviewed.

### Blocker: component 3 is not an orchestrator; it is mostly a prompt to build one

`03-review-run-orchestrator/build-review-router-skill-prompt.md` directs another agent to create and validate a future skill (lines 1–32 and 274–401). `03-review-run-orchestrator/review-suite-selector.md` is a short manual template (lines 1–57).

Neither is a canonical router, policy implementation, manifest validator, dispatcher, projection generator, or state manager.

**Consequence:** Critical behavior—policy application, waiver validation, cold-context enforcement, lens execution, and manifest persistence—is left to a future implementer.

**Smallest correction:** Supply the promised canonical routing artifact/schema, deterministic policy table, validation/dispatch contract, and runtime adapters—or rename this component as a build specification and make implementation an explicit prerequisite.

### Major: component 5 lacks the record and inputs required for exact-artifact closure

Component 2 mandates prior/final hashes, revision summary, changed-surface manifest, waivers, and current evidence for final re-review (`02-review-input-contract/review-input-contract.md`, lines 233–235). Component 5 accepts only path/version placeholders and a generic evidence manifest (`05-final-closure-gate/final-plan-rereview.md`, lines 7–14); it emits prose, no closure record ID, bound hashes, decision authority, waiver-condition validation, or state.

**Consequence:** Closure cannot reliably reject a mismatched or expired waiver or supply the `final_closure_record_id` demanded downstream.

**Smallest correction:** Add a closure-record schema and make hash-pinned prior/final plan, ledger, waivers, changed-surface manifest, authority decision, and condition results mandatory inputs.

### Major: finding ownership is duplicated and ambiguous

Review records contain an “Adjudication” table and “Outcome tracking” (`01-common-finding-schema/review-record.md`, lines 53–68), while component 4 calls for a separate canonical ledger (`04-adjudication-remediation-ledger/finding-adjudicator.md`, lines 25–47). No authority rule says which record is authoritative or how duplicate/merged review finding IDs map to ledger IDs.

**Consequence:** Reviewers can appear to adjudicate their own findings, and final closure or feedback can follow incompatible dispositions.

**Smallest correction:** Make review records immutable raw observations. Make component 4’s versioned ledger the sole disposition/remediation authority, with a required source-review/finding mapping.

### Major: post-implementation release control is described but not enforceably joined to release authority

Component 8 has diff-time classification and conformance review before release (`08-post-implementation-feedback-loop/post-implementation-feedback-loop.md`, “Workflow,” steps 2–3), but conformance only says to re-run lenses “or mark them as required before release” (`08-post-implementation-feedback-loop/post-implementation-conformance-review.md`, method step 8). It produces no release-decision record or required invocation of component 7’s release authority.

**Consequence:** Undeclared implementation risk can be observed without an unambiguous hard stop.

**Smallest correction:** Define a release-gate transition: material diff deviation or a new high-risk lens blocks release until required reviews and an exact-revision release decision are recorded.

### Moderate: cross-schema identifiers are not consistently modeled

The router manifest’s schema has `classification_id` but no `input_contract_id`, no output review IDs, and only loosely typed `source.contract` and `source.plan` (`03-review-run-orchestrator/build-review-router-skill-prompt.md`, manifest example lines 224–270). Component 2 expects `classification_id` and `review_manifest_id` (`02-review-input-contract/review-input-contract.md`, lines 128–136); components 7–8 expect decision, waiver, ledger, closure, and classification IDs.

**Consequence:** Implementers must decide identifier cardinality and binding rules, risking stale decisions being attached to the wrong run.

**Smallest correction:** Publish one referential-integrity matrix and add required foreign keys and hash bindings to all record schemas.

### Moderate: there is no single authoritative lifecycle/state-transition policy

Individual records define unrelated statuses—waivers (`07-human-escalation-waiver-policy/risk-waiver-record.md`, lines 6–10), escalations (`07-human-escalation-waiver-policy/escalation-and-decision-record.md`, lines 6–10), feedback (`08-post-implementation-feedback-loop/feedback-event-record.md`, lines 6–10), and learning actions (`08-post-implementation-feedback-loop/learning-action-record.md`, lines 6–10)—but not the review case’s overall state, terminal outcomes, re-entry rules, or rollback linkage.

**Consequence:** It is unclear when a review is blocked, superseded, closed, revoked, or eligible to progress.

**Smallest correction:** Define a case-level state machine with transition authority, preconditions, and re-entry rules for revisions, waiver expiry/revocation, implementation deviation, and rollback.

### Moderate: evaluation is a thorough specification, not an operational harness

Component 6 supplies policy and templates, but no actual validator, grader interface, registry, sealed-oracle custody mechanism, or runtime implementation despite calling itself a harness (`06-evaluation-drift-harness/evaluation-and-drift-harness.md`, lines 1–17 and completion criteria lines 284–299).

**Consequence:** Promotion gates can be interpreted differently or bypassed.

**Smallest correction:** Provide executable/schema-validation contracts and a release-registry interface, or explicitly designate the folder as a harness design.

### Minor: authority policy is intentionally unconfigured, but that prevents consequential use

Component 7 requires organizations to map logical roles to named people or groups (`07-human-escalation-waiver-policy/human-escalation-and-waiver-policy.md`, lines 83–98); the provided matrix is blank (`07-human-escalation-waiver-policy/authority-matrix.md`, lines 7–21).

**Consequence:** No real decision can be verified until an organization-specific matrix is supplied.

**Smallest correction:** Make a populated, versioned authority matrix a required deployment configuration and reject Tier 2/3 dispatch without it.

## Component status

| Component | Status | Basis |
|---|---|---|
| 01 Common finding schema | Partial | Useful review-record outline, but not a versioned/common finding schema and lacks required lineage. |
| 02 Review input contract | Complete | Strong, versioned input/provenance contract and validation policy. |
| 03 Review-run orchestrator | Partial | Build prompt and selector only; no actual orchestrator or canonical output implementation. |
| 04 Adjudication/remediation ledger | Partial | Adjudicator prompt defines fields but no canonical ledger artifact, lifecycle, or validation. |
| 05 Final closure gate | Partial | Re-review prompt only; no closure record/gate enforcement and policy contradiction. |
| 06 Evaluation/drift harness | Partial | Comprehensive design and templates, but not an operational harness. |
| 07 Human escalation/waiver policy | Partial | Strong policy/records, but authority mapping is blank deployment configuration. |
| 08 Post-implementation feedback loop | Partial | Comprehensive records/process; depends on absent closure/ledger records and lacks binding release gate. |

## Specification questions an implementer must still answer

1. What is the canonical case/review lifecycle state machine, and which actor may transition each state?
2. What exact schema and ID mapping joins raw review findings to deduplicated ledger findings, remediation, re-review, and closure?
3. What artifact is the authoritative final-closure record, and which release authority signs it?
4. Can a waived or deferred finding ever represent an unmet source requirement? If so, what mandatory source-contract versioning and re-review occurs?
5. How are plan-time, adjudication, final, diff-time, conformance, and release contracts related: one immutable contract per stage or a supersession chain?
6. Which mandatory gates are hard enforcement points versus instructions for a human or agent?
7. What constitutes a material implementation deviation, and who can permit a release while required re-reviews are pending?
8. What exact interfaces, storage, access controls, and authority boundaries implement sealed evaluation oracles and raw traces?

## Most consequential issue

The pipeline has no canonical, hash-bound record chain from findings through adjudication and final closure. Therefore it cannot prove that the exact reviewed plan, decisions, waivers, and implementation/release outcome belong to the same lifecycle instance.
