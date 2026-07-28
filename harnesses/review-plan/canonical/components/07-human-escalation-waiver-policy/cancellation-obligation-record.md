# Template: cancellation and residual-obligation record

## Purpose

Authorize termination of a lifecycle without claiming its outcome was achieved, while preserving every cleanup, containment, communication, expiry, recovery, contractual, or follow-up obligation that survives cancellation.

## Record

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
cancellation_record_id: "cancel-..."
cancellation_record_version: "..."
input_contract_id: "review-input-..."
status: "proposed" # proposed | active | superseded | revoked
created_at: "..."
effective_at: null

parent_records:
  - record_type: "review-input-contract"
    record_id: "review-input-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "cancellation-input"

cancelled_from_state:
  state_record_id: "state-..."
  transition_number: 0
  state_record_schema_version: "1.0"
  state_record_sha256: "..."

decision:
  decision_id: "dec-..."
  decision_record_version: "..."
  decision_record_schema_version: "1.0"
  decision_record_sha256: "..."
  reason: "..."
  outcome_not_claimed_complete: true

authority:
  authority_matrix_id: "authority-matrix-..."
  authority_matrix_version: "..."
  authority_matrix_schema_version: "1.0"
  authority_matrix_sha256: "..."
  authority_rule_ids: []
  authority_entry_ids: []
  verified_by: "..."

residual_obligations:
  - obligation_id: "obligation-..."
    category: "cleanup" # cleanup | containment | customer-communication | waiver-expiry | data-handling | contractual | operational | follow-up
    description: "..."
    source_requirement_policy_or_finding_ids: []
    owner: "..."
    due_at_or_event: "..."
    transfer_destination:
      kind: "work-record" # work-record | incident | successor-lifecycle | operational-register
      id: "..."
      record_sha256: "..."
    verification_criteria: []
    state: "open" # open | transferred | fulfilled
    verification_evidence: []
    verified_by: null
    verified_at: null

no_residual_obligations:
  asserted: false
  basis: null
  verified_by: null

post_terminal_correction:
  established: false
  correction_decision_id: null
  correction_decision_record_version: null
  correction_decision_record_sha256: null
  feedback_event_id: null
  feedback_event_version: null
  feedback_event_sha256: null
  response_successor_lifecycle_id: null
  terminal_state_remains_immutable: true

integrity:
  hash_profile: "canonical-json-sha256-v1"
  cancellation_record_sha256: "..."
  supersedes_cancellation_record_id: null
  supersedes_cancellation_record_sha256: null
```

## Activation rules

- The top-level input contract ID must equal the canonical `cancellation-input` parent tuple. An ID alone is invalid.
- `status: active` requires a valid cancellation decision and authority-matrix binding for the exact lifecycle and predecessor state hash.
- Every known residual obligation has a stable ID, owner, due date/event, verification criteria, and durable transfer destination before the lifecycle enters `cancelled`.
- If no obligations remain, `no_residual_obligations.asserted` must be true with evidence-backed basis and independent verification appropriate to the risk tier.
- Cancellation cannot waive an obligation. A separate authorized source, policy, or risk decision must explicitly change or accept it and remain linked.
- An unassigned, untracked, or hash-invalid obligation blocks the `cancelled` transition.
- `status: revoked` is valid only before the lifecycle enters `cancelled`; a revoked record cannot authorize the transition.
- At activation, `transfer_destination.kind: successor-lifecycle` is valid only for an already existing, hash-resolvable lifecycle record. It cannot name the future `post-cancellation-successor`, whose genesis requires the not-yet-created terminal cancellation hash. Transfer to a post-cancellation successor occurs only in a later cancellation-record version after that successor exists.

## Post-cancellation tracking

The lifecycle state remains terminal after cancellation, but this record may receive append-only superseding versions as obligations are transferred or fulfilled. Component 8 tracks outcomes and opens feedback events for overdue, failed, or lost obligations.

No version may delete an obligation. Later versions preserve all IDs and history, change state only with evidence, and retain the original cancellation decision and predecessor-state binding.

Cancellation-record versions use atomic compare-and-swap against the exact current `(cancellation_record_id, cancellation_record_version, cancellation_record_sha256)` head. Competing versions are rejected and must be rebased on the accepted obligation state.

After the lifecycle is terminal, later revocation of the human decision or discovery of an authorization/recording error does not erase or reopen the `cancelled` state and does not permit `status: revoked` on the current cancellation head. Record the correction in `post_terminal_correction`, open the exact feedback event, preserve every obligation, and create a separately authorized successor response if corrective work is required. The correction changes future reliance and learning; it does not rewrite the historical transition.
