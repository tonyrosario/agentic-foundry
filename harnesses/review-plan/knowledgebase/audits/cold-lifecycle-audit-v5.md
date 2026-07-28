# Cold audit v5: eight-component review lifecycle

**Audit date:** 2026-07-22<br>
**Scope:** The template index and canonical files directly within components 01 through 08 only. This is a cold semantic review of the written contracts, not an implementation, deployment-configuration, or historical-record audit. Blank deployment-owned authority/threshold values were treated as intentional deny-by-default configuration, not defects.

## Verdict

COHESIVE WITH GAPS

## Executive assessment

The specifications define a notably complete lifecycle: immutable, hash-addressed source/plan inputs; add-only classification; selected-versus-executed lens semantics; preservation of failed and not-established reviews; ledger-owned disposition; exact-hash final closure; exact-revision conformance and release authorization; append-only, CAS-protected lifecycle state; and an evaluation suite that explicitly tests the major bypass classes. Competent conforming implementations can implement the normal plan-to-release path consistently.

Two material handoff gaps remain. First, feedback records do not bind version/hash identity for several versioned human authority artifacts, so a later reader can resolve a feedback event to incompatible decision or waiver versions. Second, the lifecycle provides no explicit route when material feedback arrives after the lifecycle has entered terminal `closed`, despite the feedback component requiring long-tail observation and learning from later evidence. These gaps do not undermine the main release gate, but they prevent fully closed-loop, exact-lineage behavior across the entire stated lifecycle.

## Findings

### M1 — Feedback lineage is ambiguous for versioned decisions and waivers

**Severity:** major

**Evidence:** [08-post-implementation-feedback-loop/feedback-event-record.md](08-post-implementation-feedback-loop/feedback-event-record.md), `lineage`, records `decision_ids` and `waiver_ids` only; its evidence checklist says the event links to exact decision and waiver *versions*. In contrast, [07-human-escalation-waiver-policy/escalation-and-decision-record.md](07-human-escalation-waiver-policy/escalation-and-decision-record.md), `Record`, defines a decision as `decision_id` plus `decision_record_version`, and [07-human-escalation-waiver-policy/risk-waiver-record.md](07-human-escalation-waiver-policy/risk-waiver-record.md), `Record`, defines `waiver_id` plus `waiver_record_version`; both records may be superseded. [03-review-run-orchestrator/record-lineage-and-integrity.md](03-review-run-orchestrator/record-lineage-and-integrity.md), `Integrity rules` 8, requires enough provenance to reconstruct the complete upstream chain without conversational context.

**Incompatible/unsafe outcome:** One implementation can interpret `decision_ids: [dec-1]` as the decision version active when release occurred; another can resolve it to its current superseding version. The feedback analysis may consequently attribute an outcome to the wrong accepted conditions, authority scope, or waiver controls. The feedback event’s own hash does not remove that ambiguity.

**Smallest correction:** Replace the ID-only decision and waiver arrays with typed references containing ID, record version, and self-hash (and do the same for any other versioned upstream record that is intentionally referenced). Require validation that the referenced version matches the closure/conformance/release record implicated by the event.

### M2 — No defined closed-lifecycle recovery or successor handoff for late material feedback

**Severity:** major

**Evidence:** [03-review-run-orchestrator/lifecycle-state-machine.md](03-review-run-orchestrator/lifecycle-state-machine.md), `Terminal states`, makes `closed` terminal with no outgoing transitions and says new effort after a terminal state receives a new linked lifecycle, but does not define when or how feedback creates that successor. [08-post-implementation-feedback-loop/post-implementation-feedback-loop.md](08-post-implementation-feedback-loop/post-implementation-feedback-loop.md), `Observation stages` includes a long-tail review, and `Cadence and triggers` requires feedback for later incidents, waiver/control failures, and drift; its pipeline then requires learning actions and potentially implementation/release-control changes.

**Incompatible/unsafe outcome:** After `closed`, one conforming implementation may record a late feedback event but leave the affected delivery lifecycle terminal, while another may reopen it informally or create a successor. The former has no state-authorized route for material remediation, reclassification, containment, or a replacement release; the latter invents lineage/authority semantics. This is particularly consequential for delayed retention, consistency, cost, or waived-risk failures.

**Smallest correction:** Define one explicit rule: a material post-closure feedback event either (a) creates a new linked remediation lifecycle with a prescribed parent/successor reference and initial state/contract, or (b) permits a narrowly authorized `closed -> observing`/`blocked` reopen transition. Bind the triggering feedback-event ID/hash, define who may initiate it, and require source/implementation identity and reclassification before remediation or release.

### Optional editorial hardening (not material findings)

- [03-review-run-orchestrator/lifecycle-state-machine.md](03-review-run-orchestrator/lifecycle-state-machine.md), `reviews-running -> reviews-complete`, says a waived execution may satisfy the transition, while the manifest models a valid waiver as removal from the execution-required set rather than an execution record. Say explicitly that “waived” means a valid manifest waiver for an assignment/lens, not a synthetic raw review record.
- [08-post-implementation-feedback-loop/feedback-event-record.md](08-post-implementation-feedback-loop/feedback-event-record.md) could also carry self-hashes for final closure and release-gate records. Their IDs are less intrinsically ambiguous than decision/waiver versioned records, but hashes would make feedback validation uniformly mechanical.

## Component status

| Component | Status | Assessment |
|---|---|---|
| 01 common finding schema | Sound | Immutable raw findings/reviews, explicit provenance, and required preservation of inconclusive executions align with adjudication. |
| 02 review input contract | Sound | Freezes source/plan/evidence identity and stage contracts; deny-by-default permissions and conflict handling are implementable. |
| 03 review-run orchestrator | Gap | Strong hash, concurrency, state, routing, and waiver semantics; it needs the explicit post-`closed` feedback successor/recovery handoff in M2. |
| 04 adjudication/remediation ledger | Sound | Sole disposition authority; exhaustively preserves raw mappings and failed/not-established execution obligations. |
| 05 final closure gate | Sound | Independently rechecks source criteria, ledger, selected lenses, waivers, and exact final-plan identity. |
| 06 evaluation/drift harness | Sound | Covers the material bypass modes, including lineage substitution, state conflicts, cancellation loss, release bypass, inconclusive-review loss, and waived-lens visibility. |
| 07 human escalation/waiver policy | Sound | Exact authority, scope, expiry, cancellation, and release handshake contracts are coherent; unpopulated matrix fields correctly deny by default. |
| 08 post-implementation feedback loop | Gap | Conformance/release handoff is robust, but feedback lineage needs version/hash references (M1) and late feedback needs the lifecycle handoff in M2. |

## Remaining implementer questions

1. Which canonical successor relationship and initial state should govern a material feedback event discovered after `closed`: a new remediation lifecycle, or an explicit reopening transition?
2. Must every feedback event reference the exact decision/waiver versions active at the implicated release, or can it reference later superseding versions as separate comparative evidence? The record should represent both unambiguously if both are useful.

## Most consequential issue

M1 is the most consequential issue: without version/hash-bound decision and waiver references, the feedback loop cannot reliably learn from the exact human risk and authority conditions that governed the released change.
