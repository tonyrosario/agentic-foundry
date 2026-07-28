# Cold audit v6: eight-component review lifecycle

## Execution profile

- Auditor model: `gpt-5.6-sol`
- Reasoning effort: `high`
- Context mode: `cold / no conversation history`

## Scope and method

This audit read only the canonical files directly inside components 01 through 08 and `knowledgebase/templates/README.md`. It did not read earlier audits, adjudications, research notes, repository history, or files outside that scope.

The audit treated the documents as an integrated normative specification, not as eight independent prompts. It reconstructed the record graph and attempted the normal approval/release/closure path, revision, failed and not-established review handling, review waiver, blocking and re-entry, rollback, cancellation, outcome supersession, and material post-closure feedback. For each path, it tried to produce records that pass the written local gates while violating exact artifact identity, mandatory-review coverage, authority, terminality, or one-successor ownership. Configuration fields intentionally left for deployments were treated as deny-by-default rather than defects. No executable implementation was expected from this specification/template knowledgebase.

## Verdict

NOT COHESIVE

## Executive assessment

The intended lifecycle is unusually thorough. It cleanly separates raw reviewer observations from adjudication, preserves failed and `not-established` executions, distinguishes source-requirement defects from residual risk, keeps waived lenses selected and visible, requires exact-plan final review, separates conformance from release authorization, gives cancellation residual-obligation semantics, uses atomic state-head progression, and defines a sound non-circular handshake for material feedback discovered after closure.

Exact implementation nevertheless fails at two central seams. First, the integrity profile requires a parent to store and compare each referenced record's self-hash, while many canonical downstream schemas retain only an ID—or an ID without the version that is part of the record's primary identity. Review-execution hashes are also stored in unkeyed arrays separate from their `(review_id, review_execution_id)` identity. Consequently, two implementations can conform while resolving a mutable/versioned parent differently, and a locally gate-passing record can claim completion from one execution while presenting another execution's valid hash. Second, ordinary source-outcome supersession requires the successor lifecycle to exist before the parent enters `superseded`, while the successor is required to bind the parent's exact terminal-state hash. Neither record can be sealed first. The documents solve the analogous post-closure feedback problem with an ordered acknowledgment but do not provide such an order for supersession.

Two additional material inconsistencies affect implementability: lifecycle triggers require a logical `record_version` for records whose schemas define no such value, and the human-decision taxonomy cannot consistently represent evidence decisions or evaluation promotion/rollback authority even though the policy requires both.

These are semantic and schema defects, not requests for populated deployment configuration or executable code. Until corrected, competent implementations can accept incompatible histories or cannot construct required histories at all.

## Path analysis

### Normal approval, release, observation, and close

The intended ordering holds: `draft → input-frozen → classified → reviews-running → reviews-complete → adjudication-running → final-review-ready → final-review-running → plan-approved* → implementation-active → diff-classified → release-pending → release-authorized → released → observing → closed`. Component 5 prevents approval of an unmatched final-plan hash or unmet source criterion. Component 8 correctly makes conformance evidence only a prerequisite for an `awaiting-authority` release gate, and the ordered release handshake avoids a decision/gate self-hash cycle.

The path does not pass the stronger exact-lineage test. Review, ledger, conformance, and release records omit required version/hash bindings for several versioned parents, and the review hashes in ledger/closure/conformance/release records are not keyed to execution IDs. A validator can therefore accept a valid hash without establishing that it belongs to the execution credited as complete. Finding 1 applies.

### Revision loop

The lifecycle correctly returns `revision-required` to `input-frozen`, requires a new immutable contract, reclassification, affected reviews, a new ledger state, and final review of the exact revised candidate. Prior approval does not carry forward. The semantic ordering is sound, but exact identification of which manifest and executions governed each revision is affected by Finding 1, and state triggers are affected by Finding 3.

### Failed or not-established required review

The invariant substantially holds. Component 1 requires an immutable raw review record even with no finding; component 3 permits `reviews-complete` without pretending sufficiency; component 4 creates one `unresolved_review_executions` entry keyed by both review and execution IDs; component 5 blocks unless a replacement completes or a low/moderate, non-source, non-policy item receives a fully bound nonblocking progression decision. High/critical unknowns remain blocking. This is one of the strongest parts of the design. The only material qualification is the general parent/execution-hash ambiguity in Finding 1.

### Review-waiver and residual-risk path

The intended invariant holds. `selected_lenses` is never reduced; only `execution_required_lens_ids` may omit a lens under an exact component-7 waiver. Closure rechecks authority, scope, conditions, expiry, revocation, and artifact binding. Source-requirement defects cannot be relabeled as residual risk. Review waivers and residual-risk acceptance remain distinct. Evidence/progression decisions encounter the decision-class mismatch in Finding 4.

### Block and re-entry

The state machine makes `blocked` nonterminal, retains `blocked_from_state`, reasons, and one resume target, and requires a fresh stage contract and resolution evidence. Plan-stage re-entry returns to `input-frozen`; implementation/release-stage re-entry returns to `diff-classified`. This prevents a jump directly to final or release gates. Trigger serialization remains ambiguous under Finding 3.

### Rollback and recovery

The path is coherent: `released|observing → rolled-back → implementation-active`, with an executed rollback/containment record, a feedback event, active feedback ownership, and a new implementation-stage contract before another release attempt. The old release gate cannot be reused. Exact upstream manifest/review bindings remain affected by Finding 1.

### Cancellation

Cancellation itself is well specified. It requires a decision and active cancellation record bound to the exact predecessor, authority matrix, and either durable destinations for all residual obligations or an evidence-backed verified assertion that none remain. Cancellation is terminal and cannot claim completion; later cancellation-record versions may track obligations without reopening state. Component 8 monitors loss and overdue obligations. A later `post-cancellation-successor` is named in the origin enum but its cross-lifecycle binding conflicts with the terminal-feedback-only exception described in Finding 2.

### Outcome supersession

This path does not hold. The `Any nonterminal state → superseded` row requires a linked successor lifecycle already to have been created, while lifecycle lineage requires the successor to bind the exact parent terminal state. The parent's terminal hash does not exist until the transition occurs. There is no reservation, intermediate state, transaction, or acknowledgment record equivalent to the feedback handshake. Implementations must violate one condition, invent an unstated placeholder, or deadlock. See Finding 2.

### Material post-closure feedback and successor remediation

This path is coherent and is the model the supersession path should follow. The initiating `required-pending` feedback event is sealed first; candidate successor genesis and first contract then bind that immutable event and the exact parent `closed` state; finally, a compare-and-swap appends one acknowledging event version containing both successor hashes. Only the acknowledged successor dispatches, the parent remains terminal, and no approval, waiver, or release authority is inherited. Feedback records also preserve exact historical decision and waiver versions instead of resolving “latest.” Finding 1 still applies to some older upstream record types, but the successor handshake itself avoids cycles, races, and multiple recognized successors.

## Findings

### Finding 1 — BLOCKER: the canonical schemas cannot enforce the integrity profile's exact parent-record and review-execution bindings

**Evidence.** `03-review-run-orchestrator/integrity-profile.md`, “Referenced-record validation” (lines 68–74), requires resolving by ID and schema version, recomputing the referenced record, and comparing it with “the parent's stored reference”; missing hashes must be rejected. `03-review-run-orchestrator/record-lineage-and-integrity.md`, “Identifier model” (lines 13–30), makes manifest version, review execution ID, ledger version, decision version, waiver version, and other identities part of the canonical graph. However:

- `01-common-finding-schema/review-record.md`, “Record” (lines 12–19), stores only `input_contract_id`, `classification_id`, and `review_manifest_id`; it stores neither parent self-hashes nor the manifest version.
- `04-adjudication-remediation-ledger/finding-ledger.md`, “Ledger” (lines 12–17), repeats the same ID-only parents. Its `inputs` (lines 35–37) keeps `raw_review_ids` and `raw_review_record_hashes` as unrelated arrays, without `review_execution_id` or a normative positional mapping.
- `05-final-closure-gate/final-closure-record.md`, `rereviews` and `review_execution_closure` (lines 78–98), separates `review_record_hashes` from the review/execution tuples credited with an outcome.
- `08-post-implementation-feedback-loop/post-implementation-conformance-review.md`, top-level parent fields and `diff_time_reviews` (lines 12–17 and 73–77), identifies the diff manifest only by ID and again separates completed review IDs from record hashes.
- `08-post-implementation-feedback-loop/release-gate-record.md`, top-level lineage and `reviews` (lines 10–17 and 54–58), binds conformance by hash but identifies the diff-time classification and versioned review manifest only by ID; review hashes are again unkeyed.

**Gate-passing counterexample.** A diff-time manifest `manifest-7/v1` requires only review `rev-A`. A superseding `manifest-7/v2`, on the same implementation artifacts, adds a mandatory security lens and review `rev-S`. `rev-A` has two executions: `exec-1` failed and `exec-2` completed. A release gate names `manifest-7` without version/hash, lists `rev-A` as completed, and supplies the valid record hash for `exec-1` in the unkeyed hash list while a separate closure row credits `exec-2` as established. All supplied IDs and hashes can resolve, artifact hashes can agree, and local booleans can be true. One conforming validator resolves the latest manifest and blocks for missing `rev-S`; another resolves the dispatch-time version and releases. Neither the schema nor the integrity algorithm can prove which execution hash supports the credited result. This permits both a mandatory-review bypass and incompatible conforming outcomes.

**Smallest correction.** Replace every downstream parent reference with an explicit typed tuple containing the parent's full logical identity, schema version, and self-hash. In particular, use keyed entries such as `{review_id, review_execution_id, schema_version, review_record_sha256, result}` rather than parallel ID/hash arrays, and `{review_manifest_id, review_manifest_version, schema_version, manifest_sha256}` wherever a manifest governs behavior. Do the same for input contracts, classifications, ledgers, closure records, and other versioned parents as required by the integrity profile. State explicitly that validation never resolves “active” or “latest” in place of the stored tuple.

### Finding 2 — BLOCKER: ordinary supersession has a circular creation requirement, and non-feedback terminal successors lack an admissible cross-lifecycle binding

**Evidence.** `03-review-run-orchestrator/lifecycle-state-machine.md`, “Exception and recovery transitions” (line 133), requires a linked successor lifecycle to be created before the parent may enter `superseded`. The same file says terminal states have no outgoing transitions and a new effort receives a linked lifecycle (line 136), while `record-lineage-and-integrity.md`, “Identifier model” and “Integrity rules” (lines 14 and 62), require a linked lifecycle to name the exact parent terminal-state ID/hash. Thus the successor needs the parent's not-yet-created `superseded` record hash, while the parent transition needs the successor already created. In addition, the state-machine trigger rule (line 91) rejects foreign-lifecycle records except the parent state/event pair for `terminal-feedback-remediation`, although the origin enum also offers `superseding-outcome` and `post-cancellation-successor` and the terminal rules require linked new lifecycles after supersession/cancellation.

**Gate-passing counterexample or incompatible outcome.** Implementation A treats reserving a successor lifecycle ID as “created,” transitions the parent, then creates a genesis binding the terminal hash. Implementation B requires a hash-valid genesis before accepting the parent transition and deadlocks. Implementation C creates the successor against the parent's pre-terminal state, allowing the parent transition, but violates the exact-terminal binding. For a post-cancellation successor, one validator admits the exact foreign parent cancellation state because the origin enum implies it; another rejects it under the explicit terminal-feedback-only exception. All are reasonable readings of different normative clauses.

**Smallest correction.** Define one ordered non-circular handoff for ordinary supersession, for example: seal the authorized source decision with a reserved successor ID; atomically append the parent's `superseded` record binding that decision and reserved ID; then create exactly one successor genesis binding the terminal parent hash and decision, enforced by a uniqueness/CAS rule. Alternatively add a nonterminal `supersession-pending` and a final acknowledgment transaction. Explicitly admit and define the required cross-lifecycle trigger bindings for `superseding-outcome` and `post-cancellation-successor`, including the exact cancellation record/obligations when applicable.

### Finding 3 — MAJOR: lifecycle transitions require a `record_version` that many canonical trigger records do not define

**Evidence.** `03-review-run-orchestrator/lifecycle-state-machine.md`, “Lifecycle state record” (lines 33–38), makes each trigger contain `record_version`, and “Trigger and authority binding” (line 87) says every transition-row evidence item must carry its canonical type, ID, version, and hash. Yet input contracts, classification records, raw review records, final closure records, conformance reviews, and release-gate records define `schema_version` and an ID but no logical record-version field. Several use a new ID plus `supersedes_*` for correction; that is not defined as the value to serialize into `trigger_records.record_version`.

**Gate-passing counterexample or incompatible outcome.** A `release-pending → release-authorized` state transition includes a release-gate trigger. Validator A puts the release gate's `schema_version: 1.0` in `record_version`; validator B requires an unstated logical version and rejects it; validator C uses the supersession depth. All can verify the same ID and hash, but exact schema conformance differs, and a strict producer cannot construct a canonical value from the release-gate record itself.

**Smallest correction.** Either add a logical `record_version` to every triggerable canonical record and include it in that record's self-hash, or rename the trigger field to `schema_version` and make a separate nullable `logical_record_version` whose requiredness is defined per record type. If ID-plus-hash is the complete identity for some record types, explicitly allow `logical_record_version: null` for those types.

### Finding 4 — MAJOR: component-7 authority cannot represent all decision classes required by components 4 and 6, and evaluation promotion lacks a hash-bound authority handoff

**Evidence.** `07-human-escalation-waiver-policy/human-escalation-and-waiver-policy.md`, “Escalation classes” (line 74), defines an evidence decision, and “Roles and authority” (line 96) assigns evaluation promotion/rollback to the evaluation owner. It also states that every decision binds the exact authority-matrix ID/version/hash and matched rules/entries (line 99). But `07-human-escalation-waiver-policy/authority-matrix.md`, `decision_rules.decision_class` (line 23), includes `evaluation-promotion-rollback` but omits `evidence`; `07-human-escalation-waiver-policy/escalation-and-decision-record.md`, `trigger.class` (line 16), includes `evidence` but omits `evaluation-promotion-rollback`. Finally, `06-evaluation-drift-harness/evaluation-run-record.md`, “Release decision” (lines 148–170), records only a free-text authorized owner, not a decision ID/version/hash or authority-matrix binding, despite the harness requiring a signed run record.

**Gate-passing counterexample.** A candidate review-router fails a high-risk segment but is marked `PROMOTE`; the run record names “evaluation-owner” and hashes the run. No component-7 decision or authority-matrix record is referenced. Component 6's local template is complete and self-hash-valid, so a registry can promote it, while component 7's global rule says the authority is unproved. Conversely, a strict component-7 implementation cannot create a conforming evaluation decision because its decision-record trigger enum lacks that class. A lower-impact unresolved evidence item has the inverse problem: the decision record accepts `evidence`, but no authority-matrix rule can canonically match it.

**Smallest correction.** Use one shared decision-class catalog in the authority matrix, decision record, policy tables, and consumers; include both `evidence` and `evaluation-promotion-rollback`. Add an exact component-7 decision ID/version/hash and authority-matrix ID/version/hash to the evaluation run's release-decision block (or define and reference a separate signed decision envelope) and require the component registry to validate it before promote, shadow, or rollback effects.

### Optional hardening (not material findings)

- Add explicit evaluation cases for the ordinary supersession handshake, post-cancellation successor binding, rollback re-entry, and keyed retry/execution substitution. The current `invalid-transition`, `lineage-substitution`, `state-stream-conflict`, `authority-substitution`, and late-feedback classes can host such cases, but naming them prevents these specific seams from being lost in suite curation.
- Define release-gate version-head CAS semantics directly, even though the lifecycle state head ultimately chooses the effective release authorization. This would make orphan authorized-gate candidates easier to classify and audit.
- Clarify whether a later `revoked` cancellation-record version can exist after the terminal state and, if so, whether it invalidates only future reliance or denotes a recording correction. The current obligation-preservation rules prevent silent loss, so this is not by itself a gate bypass.

## Component status

1. **Common finding schema — PARTIALLY COHESIVE.** Raw findings and raw reviews are immutable, execution-aware, and correctly keep adjudication authority out of the reviewer. The review record's ID-only contract/classification/manifest parents do not meet the stated exact-reference profile.
2. **Review input contract — COHESIVE IN ISOLATION.** It strongly binds source bundles, plans, revisions, evidence, permissions, stage contracts, and terminal-feedback parent delivery. Its downstream guarantees are weakened because consumers do not consistently carry contract self-hashes, and it does not close the non-feedback terminal-successor ambiguity.
3. **Review-run orchestrator — NOT COHESIVE.** Lens selection, waiver visibility, atomic state-head ordering, recovery, and the feedback-successor handshake are strong. Exact parent tuples, trigger-version semantics, and ordinary supersession are materially defective.
4. **Adjudication and remediation ledger — PARTIALLY COHESIVE.** It correctly preserves every raw finding and required inconclusive execution, uses type-specific closure rules, and defaults unresolved work to blocking. Parent references and raw-review hashes are not keyed to complete execution identity.
5. **Final closure gate — PARTIALLY COHESIVE.** Its hard gates correctly distinguish requirements, risk, waivers, revisions, and inconclusive reviews. The separate review-ID/hash collections cannot prove which immutable execution supports each closure row, and some parents remain ID-only.
6. **Evaluation and drift harness — PARTIALLY COHESIVE.** It covers the important bypass families, including lineage substitution, forks, cancellation loss, feedback lineage, waived-lens visibility, inconclusive escape, and release bypass. Its own promotion/rollback authority is not represented with the component-7 bindings required by the policy.
7. **Human escalation and waiver policy — PARTIALLY COHESIVE.** Deny-by-default authority, bounded waivers, release authorization, emergency controls, and cancellation obligations are strong. The authority-matrix and decision-record decision-class vocabularies are incompatible for evidence and evaluation decisions.
8. **Post-implementation feedback loop — PARTIALLY COHESIVE.** Conformance/release separation, historical decision/waiver lineage, rollback, observation, cancellation monitoring, and the one-successor late-feedback handshake are strong. Diff manifest and review execution bindings inherit Finding 1; non-feedback terminal successors inherit Finding 2.

## Remaining implementer questions

1. What exact ID/version/self-hash tuple must each downstream record store for every parent, especially a versioned review manifest and a retried review execution?
2. What is `trigger_records.record_version` for canonical records that have no logical record-version field?
3. What is the authoritative non-circular order and uniqueness mechanism for ordinary outcome supersession, and what cross-lifecycle records are admissible for `superseding-outcome` and `post-cancellation-successor` genesis?
4. Which shared decision-class value and exact component-7 record authorize evidence-threshold progression and evaluation promotion, shadow, block, or rollback?

## Most consequential issue

The most consequential issue is Finding 1: exact-hash integrity is declared as a lifecycle-wide invariant but is not representable in several canonical parent and execution references. That gap reaches ordinary review completion, adjudication, final closure, conformance, and release, allowing materially different implementations to accept different governing versions or credit the wrong execution while all supplied hashes are individually valid.
