# Canonical lifecycle state machine

## Purpose

Define when a review lifecycle may advance, re-enter an earlier stage, block, roll back, or terminate. The orchestrator enforces transitions; reviewer prose does not change lifecycle state by itself.

## Lifecycle state record

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
state_record_id: "state-..."
transition_number: 0
from_state: null
state: "draft"
stage: "plan-time" # plan-time | final-review | implementation | release | observation
entered_at: "..."

lifecycle_origin:
  kind: "independent" # independent | terminal-feedback-remediation | superseding-outcome | post-cancellation-successor
  parent_lifecycle_id: null
  parent_terminal_state_record_id: null
  parent_terminal_state_record_schema_version: null
  parent_terminal_state_record_sha256: null
  initiating_feedback_event_id: null
  initiating_feedback_event_version: null
  initiating_feedback_event_schema_version: null
  initiating_feedback_event_sha256: null
  initiating_decision_id: null
  initiating_decision_record_version: null
  initiating_decision_record_schema_version: null
  initiating_decision_record_sha256: null
  parent_cancellation_record_id: null
  parent_cancellation_record_version: null
  parent_cancellation_record_schema_version: null
  parent_cancellation_record_sha256: null

previous_state:
  state_record_id: null
  transition_number: null
  state_record_schema_version: null
  state_record_sha256: null

trigger_records:
  - record_type: "input-contract" # lifecycle-state | input-contract | source-bundle | classification | review-manifest | review-record | finding-ledger | final-closure | human-decision | waiver | conformance | release-gate | feedback-event | cancellation-obligation
    record_id: "..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "prerequisite"

transition_authority:
  mode: "orchestrator" # orchestrator | human | system
  actor_identity: "..."
  decision_id: null
  decision_record_version: null
  decision_record_schema_version: null
  decision_record_sha256: null
  authority_matrix_id: null
  authority_matrix_version: null
  authority_matrix_schema_version: null
  authority_matrix_sha256: null
  authority_rule_ids: []
  authority_entry_ids: []

preconditions_verified: []
blocking_reasons: []
blocked_from_state: null
resume_target_state: null
active_input_contract_id: "..."
active_input_contract_sha256: "..."
active_artifact_hashes: {}

cancellation:
  cancellation_record_id: null
  cancellation_record_version: null
  cancellation_record_schema_version: null
  cancellation_record_sha256: null
  residual_obligation_ids: []

terminal_handoff:
  reserved_successor_lifecycle_id: null
  successor_origin_kind: null

integrity:
  hash_profile: "canonical-json-sha256-v1"
  state_record_sha256: "..."
```

State records are append-only and hash-linked. The current state is the unique verified head selected by the ordering rules below; timestamps never determine state precedence.

## State-stream ordering and concurrency

1. The initial `draft` record has `transition_number: 0`, `from_state: null`, and null previous-state fields. For an independent lifecycle, first reserve the unused `lifecycle_id`, freeze its initial component-2 input contract under that ID, and then compare-and-create the genesis `draft` with `active_input_contract_id` and `active_input_contract_sha256` equal to that exact contract. Placeholder or null genesis contract bindings are invalid. The later `draft → input-frozen` transition validates the already frozen contract; it does not first create or attach it.
2. Every successor sets `transition_number = previous.transition_number + 1`, `from_state = previous.state`, and repeats the exact predecessor ID, transition number, and self-hash.
3. Appending a successor uses an atomic compare-and-swap against the expected head tuple `(lifecycle_id, state_record_id, transition_number, state_record_sha256)`.
4. Exactly one successor may consume a predecessor hash. A competing append is rejected, must reload the current head, re-evaluate all preconditions, and create a new candidate transition.
5. A fork, duplicate transition number, skipped number, predecessor mismatch, backdated record, or second successor makes the candidate invalid and blocks automatic progression. Do not resolve conflicts using `entered_at`, storage order, or actor priority.
6. The authoritative current state is the terminal record of the one genesis-linked, consecutively numbered, hash-valid chain accepted by the atomic head store.
7. Every record repeats the genesis `lifecycle_origin` unchanged. An independent lifecycle has null cross-lifecycle fields. A terminal successor binds the exact parent terminal state and the origin-specific trigger records described below.

A deployment may implement the atomic head with a single writer, transaction, compare-and-swap key, or consensus system. The observable semantics above are mandatory.

## Trigger and authority binding

- Every evidence item named in a transition row appears in `trigger_records` using the canonical reference tuple: type, full primary/composite identity, schema version, nullable logical record version, verified self-hash, lifecycle, and role.
- `logical_record_version` is required for source bundles, review manifests, finding ledgers, human decisions, waivers, release-gate records, feedback events, cancellation records, and any later schema that defines a logical version. It is explicitly `null` for lifecycle states, input contracts, classifications, raw review records, final closures, and conformance reviews unless their schemas are versioned in a later revision.
- `record_sub_id` is the `review_execution_id` for review records and `null` for the other currently defined trigger types.
- The predecessor state record is always validated independently through `previous_state`; it is not represented only as a trigger.
- Human-authorized transitions bind the exact decision-record and authority-matrix IDs, versions, and hashes in `transition_authority`.
- Orchestrator or system authority is allowed only for transitions that policy explicitly delegates to that mode; the validating policy/version remains among active artifact hashes or trigger records.
- A stale, revoked, superseded, hash-invalid, or artifact-mismatched trigger or authority record invalidates the transition. Foreign-lifecycle records are invalid except for the exact origin-specific bindings admitted in “Terminal successor handoffs”; those must match `lifecycle_origin` exactly.

## Normal transitions

| From | To | Required evidence | Transition authority |
|---|---|---|---|
| `draft` | `input-frozen` | Valid component-2 contract and artifact hashes | Orchestrator validation |
| `input-frozen` | `classified` | Valid classification and review manifest | Orchestrator validation |
| `classified` | `reviews-running` | All unwaived required assignments dispatchable | Orchestrator |
| `reviews-running` | `reviews-complete` | Every execution-required assignment has an immutable completed, failed, or `not-established` execution record, and every selected lens omitted from execution has a valid manifest waiver; this state does not imply lens sufficiency | Orchestrator validation |
| `reviews-complete` | `adjudication-running` | Immutable raw review/finding records plus unresolved-review inputs for every required failed or `not-established` execution | Orchestrator |
| `adjudication-running` | `revision-required` | Canonical ledger has unresolved confirmed findings | Ledger state |
| `adjudication-running` | `final-review-ready` | Ledger is `ready-for-final-review`; required decisions/reviews complete | Orchestrator validation |
| `revision-required` | `input-frozen` | Revised plan and new input contract in same lifecycle | Change owner plus orchestrator |
| `final-review-ready` | `final-review-running` | Final-review contract, manifest, and reviewer assigned | Orchestrator |
| `final-review-running` | `plan-approved` | Valid component-5 approval bound to exact plan | Final-closure record and required human authority |
| `final-review-running` | `plan-approved-with-residual-risk` | All criteria met plus valid residual-risk records | Closure record and component-7 authority |
| `final-review-running` | `revision-required` | Closure requires revision | Final-closure record |
| `final-review-running` | `blocked` | Missing authority/evidence, unmet criterion, or invalid waiver | Final-closure record |
| `plan-approved*` | `implementation-active` | Implementation authorized against approved plan hash | Change/release policy |
| `implementation-active` | `diff-classified` | Exact base/head diff contract and classification | Orchestrator validation |
| `diff-classified` | `implementation-reviews-required` | New/changed required lenses or human gates | Review manifest |
| `diff-classified` | `release-pending` | No new material lens; conformance evidence ready | Orchestrator validation |
| `implementation-reviews-required` | `release-pending` | Required diff reviews/adjudication complete and implementation conforms | Orchestrator validation |
| `release-pending` | `release-authorized` | Exact-revision component-7 release decision and valid release-gate record | Release authority |
| `release-authorized` | `released` | Authorized release execution recorded | Release operator/system |
| `released` | `observing` | Outcome windows and monitoring active | Orchestrator/operations |
| `observing` | `closed` | Required windows complete, no unresolved feedback action or active blocking condition | Accountable owner |

`plan-approved*` means either `plan-approved` or `plan-approved-with-residual-risk`.

## Exception and recovery transitions

| From | To | Required evidence | Transition authority |
|---|---|---|---|
| Any nonterminal active state | `blocked` | Failed prerequisite, invalid lineage/authority/waiver, high-impact unknown, or mandatory gate failure; record `blocked_from_state` and reasons | Orchestrator validation or governing policy authority |
| `blocked` | `input-frozen` | Plan-stage blocking reasons resolved; new immutable input contract pins corrected source/plan/evidence | Change owner plus orchestrator validation |
| `blocked` | `diff-classified` | Implementation/release-stage blocking reasons resolved; new diff-time contract and classification bind the exact implementation | Orchestrator validation |
| `plan-approved*` | `input-frozen` | Material source or plan change; prior closure revoked/superseded; new input contract | Change owner plus orchestrator validation |
| `release-authorized` | `blocked` | Authorization revoked/expired or artifact/configuration changed before execution | Release authority plus orchestrator validation |
| `released` or `observing` | `rolled-back` | Executed rollback/containment record bound to released revision; feedback event opened | Release/incident authority |
| `rolled-back` | `implementation-active` | Approved recovery or replacement implementation, new implementation-stage input contract, and active feedback ownership | Change/release authority plus orchestrator validation |
| Any nonterminal state | `superseded` | Authorized source decision replaces the outcome and reserves one unused successor lifecycle ID in `terminal_handoff`; no successor hash is required yet | Product/requirement owner |
| Any nonterminal state | `cancelled` | Active component-7 cancellation record binds the exact predecessor state and authorized decision; every residual obligation is assigned to a durable destination or an evidence-backed no-obligation assertion is verified | Accountable human owner |

`closed`, `superseded`, and `cancelled` have no outgoing state transitions. A new effort after one of those states receives a new linked lifecycle. Append-only cancellation-record versions may continue tracking transferred or fulfilled obligations without changing the terminal lifecycle state.

`rolled-back` is the canonical post-release recovery state name for both a completed rollback and bounded containment. The linked execution and feedback records state which action occurred; the state name does not assert that the original revision was fully restored.

## Terminal successor handoffs

Terminal parent state is immutable. Successors use these non-circular, origin-specific creation rules:

### Superseding outcome

For a nonterminal parent:

1. Component 7 seals a `specification` decision that binds the parent lifecycle’s expected current-head ID/number/hash and reserves one previously unused `successor_lifecycle_id`.
2. The orchestrator atomically appends the parent’s `superseded` state against that expected head. The state hash-binds the decision and stores the reserved ID plus `successor_origin_kind: superseding-outcome`; it does not require a successor genesis hash.
3. After the terminal parent hash exists, compare-and-create exactly one `draft` genesis under the reserved lifecycle ID. Its `lifecycle_origin` binds the parent `superseded` ID/hash and initiating decision ID/version/hash.
4. The successor is dispatchable only when its first input contract carries the same bindings. If creation is interrupted, retry only the same reserved ID; another ID requires a new authorized decision but cannot replace the ID already sealed into the terminal parent.

If the parent is already `closed`, a later specification decision may reserve one unused successor ID and directly compare-and-create a `superseding-outcome` genesis bound to the exact existing `closed` state and that decision. The closed parent is not mutated. A parent already `superseded` uses the ID sealed in its terminal handoff; it cannot receive another replacement ID.

### Post-cancellation successor

After `cancelled` exists, an accountable component-7 decision may compare-and-create one new lifecycle whose genesis uses `post-cancellation-successor` and binds the exact parent terminal ID/hash plus the current cancellation-record ID/version/hash. A successor does not inherit or discharge residual obligations merely by existing. Any obligation transferred to it requires a later append-only cancellation-record version that names the successor and transfer evidence.

### Terminal-feedback remediation

The material-feedback handshake below governs this origin.

For all three origins, compare-and-create of the lifecycle ID is atomic: an existing genesis or competing creation rejects the candidate. The admissible foreign-lifecycle trigger set is limited to the exact parent terminal state plus: the initiating specification decision for `superseding-outcome`; the current cancellation record and initiating decision for `post-cancellation-successor`; or the sealed initiating feedback event for `terminal-feedback-remediation`.

## Material feedback after closure

A `closed` lifecycle never reopens. When a feedback event created after closure establishes a material need for corrective implementation, containment follow-up, source/plan revision, or replacement release, the response is owned by one new linked lifecycle:

1. The policy-designated accountable owner or incident/release authority initiates the successor; the orchestrator verifies the authority and the material-feedback trigger.
2. The successor starts with a compare-and-created `draft` genesis record at `transition_number: 0`. Its `lifecycle_origin.kind` is `terminal-feedback-remediation` and it hash-binds the parent lifecycle’s exact `closed` state record and the initiating feedback event.
3. The successor’s first component-2 contract binds the parent lifecycle and terminal-state hash, initiating feedback-event ID/version/hash, original source bundle and approved plan, implicated implementation revision, final closure, release gate, and proposed remediation plan.
4. After those candidate successor records are sealed, atomically append a superseding feedback-event version that acknowledges the successor lifecycle, genesis-state ID/hash, and first input-contract ID/hash. Compare-and-swap against the initiating event head admits only one successor; this ordered acknowledgment preserves the initiating event hash and avoids circular self-hashes.
5. Only the acknowledged successor is valid and dispatchable. It follows the normal `draft → input-frozen → classified` path, and the `draft → input-frozen` transition verifies the acknowledgment. It must reclassify the remediation against current policy and complete every resulting review, authority, implementation, and release gate; no parent approval is inherited.

Materiality is established by the active feedback policy. Nonmaterial observations may remain records on the closed lifecycle without a successor. Immediate emergency containment need not wait for the successor review path, but it requires component-7 emergency authorization and must be linked into the successor contract and feedback evidence.

## Blocking and re-entry

- `blocked` is nonterminal. Its state record must preserve `blocked_from_state`, all blocking reasons, and one permitted `resume_target_state`. Re-entry requires a new stage input contract and evidence that every blocking reason is resolved.
- A material source or plan change before implementation revokes/supersedes closure and returns to `input-frozen` for reclassification.
- A material revision during remediation always returns to `input-frozen`; it never jumps directly back to final review.
- Waiver expiry, revocation, scope mismatch, or failed condition before release moves the lifecycle to `blocked`.
- An implementation deviation or newly observed surface moves the lifecycle to `diff-classified`; release remains blocked until all added gates complete.
- Every final-review or conformance `not-established` result defaults to `blocked`. Progression is allowed only for a low/moderate item that is not an unmet source criterion or policy gate and whose ledger records materiality, evidence-backed progression basis, authorized component-7 decision ID, owner, expiry/review event, and required re-review lenses.
- A release rollback follows the explicit `released/observing → rolled-back → implementation-active` path, opens component-8 feedback, and requires a new implementation-stage contract before another release attempt.
- If a source-contract change replaces the authorized outcome rather than clarifying it, mark the old lifecycle `superseded` and create a linked new lifecycle.

## Terminal states

- `closed`: implementation/release outcome observation is complete and no required action remains.
- `superseded`: a different lifecycle owns the replaced outcome.
- `cancelled`: accountable authority ended the lifecycle without claiming successful completion; the state record hash-binds an active component-7 cancellation record and all residual-obligation IDs.

`blocked` and `rolled-back` are not terminal. They require one of the explicit recovery, cancellation, or supersession transitions. Approval, release, and closure statuses are always bound to exact hashes.

## Hard transition rules

- No stage can self-certify its own prerequisite record.
- No transition may rely only on natural-language claims when a canonical record is required.
- Missing mandatory reviews, invalid lineage, unmet source criteria, unauthorized decisions, expired waivers, high/critical-impact unknowns, and unresolved items without a valid progression record block advancement.
- Human decisions can authorize only transitions within the authority matrix and exact recorded scope.
- A `cancelled` transition is invalid without an exact cancellation-record ID/version/hash, exact cancellation-decision and authority-matrix bindings, and complete residual-obligation assignment or verified no-obligation evidence.
- Every re-entry issues new contract, classification/manifest, review, ledger, or closure versions as applicable; prior approval never carries forward automatically.
