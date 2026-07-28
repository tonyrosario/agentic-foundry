# Template: post-implementation feedback event

## Record

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
feedback_event_id: "fdb-..."
feedback_event_version: "..."
event_class: "..."
status: "open" # open | analyzing | actioned | monitoring | closed | not-established
detected_at: "..."
detected_by: "..."
owner: "..."

lineage:
  input_contract_id: "..."
  input_contract_schema_version: "1.0"
  input_contract_sha256: "..."
  authoritative_source_bundle_id: "..."
  authoritative_source_bundle_schema_version: "1.0"
  authoritative_source_bundle_version: "..."
  authoritative_source_bundle_sha256: "..."
  approved_plan_sha256: "..."
  implementation_revision: "..."
  classifications:
    - classification_id: "..."
      classification_schema_version: "1.0"
      classification_record_sha256: "..."
      role: "plan-time" # plan-time | diff-time | final-rereview | implementation-conformance | successor-plan-time
  reviews:
    - review_id: "..."
      review_execution_id: "..."
      review_record_schema_version: "1.0"
      review_record_sha256: "..."
  findings:
    - finding_id: "..."
      finding_schema_version: "1.0"
      finding_sha256: "..."
  adjudication_ledger_id: "..."
  adjudication_ledger_version: "..."
  adjudication_ledger_schema_version: "1.0"
  adjudication_ledger_sha256: "..."
  final_closure_record_id: "..."
  final_closure_record_schema_version: "1.0"
  final_closure_record_sha256: "..."
  decisions:
    - decision_id: "..."
      decision_record_version: "..."
      decision_record_schema_version: "1.0"
      decision_record_sha256: "..."
      role: "..." # specification | risk-acceptance | release-authorization | cancellation | other
      governed_implicated_release: true
      comparison_only: false
  waivers:
    - waiver_id: "..."
      waiver_record_version: "..."
      waiver_record_schema_version: "1.0"
      waiver_record_sha256: "..."
      governed_implicated_release: true
      comparison_only: false
  conformance_review_id: "..."
  conformance_review_schema_version: "1.0"
  conformance_review_sha256: "..."
  release_gate_record_id: "..."
  release_gate_record_version: "..."
  release_gate_record_schema_version: "1.0"
  release_gate_record_sha256: "..."
  cancellation_record_id: null
  cancellation_record_version: null
  cancellation_record_schema_version: null
  cancellation_record_sha256: null
  residual_obligation_ids: []

response_lifecycle:
  state: "not-required" # not-required | required-pending | acknowledged
  successor_lifecycle_id: null
  successor_genesis_state_record_id: null
  successor_genesis_state_record_schema_version: null
  successor_genesis_state_record_sha256: null
  successor_input_contract_id: null
  successor_input_contract_schema_version: null
  successor_input_contract_sha256: null

observation:
  stage: "..."
  summary: "..."
  expected_outcome: "..."
  observed_outcome: "..."
  impact: "..."
  affected_users_services_data: []
  detection_signal: "..."
  evidence: []
  facts: []
  inferences: []
  unknowns: []

historical_reconstruction:
  evidence_available_at_plan_time: []
  evidence_available_at_review_time: []
  evidence_available_at_adjudication_time: []
  evidence_available_at_final_closure: []
  evidence_available_only_after_implementation: []

analysis:
  causal_contributors:
    - class: "..."
      evidence: []
      confidence: "..."
      counterfactual: "..."
      system_owner: "..."
  earliest_prevention_opportunity: "..."
  later_detection_or_containment_opportunities: []
  review_detectable: null
  review_detectability_rationale: "..."
  false_positive_established: null
  false_positive_rationale: "..."
  severity: "..."

containment:
  immediate_actions: []
  rollback_or_recovery: []
  active_monitoring: []
  human_decisions:
    - decision_id: "..."
      decision_record_version: "..."
      decision_record_schema_version: "1.0"
      decision_record_sha256: "..."

learning:
  generalized_failure_class: "..."
  proposed_action_ids: []
  evaluation_case_ids: []
  no_change_rationale: null

closure:
  closed_at: null
  closed_by: null
  outcome_evidence: []
  recurrence_monitoring_until: null
  related_event_ids: []

integrity:
  hash_profile: "canonical-json-sha256-v1"
  feedback_event_sha256: "..."
  supersedes_feedback_event_version: null
  supersedes_feedback_event_sha256: null
```

## Evidence checklist

- [ ] The event links to exact plan, implementation, review, decision, and waiver versions.
- [ ] Every versioned upstream record is referenced by ID, version where applicable, and verified self-hash.
- [ ] Governing decision and waiver versions match those bound by the implicated closure, conformance review, and release gate; later versions are marked comparison-only.
- [ ] Facts available at each historical stage are reconstructed separately.
- [ ] Impact and materiality are supported rather than inferred from outcome alone.
- [ ] Multiple contributors may be recorded.
- [ ] Review detectability is assessed against actual authority and evidence.
- [ ] A false-positive label has authoritative counterevidence.
- [ ] Unknown counterfactuals remain `not established`.
- [ ] Immediate containment is separated from long-term learning.
- [ ] A cancellation-related event binds the exact cancellation-record version and affected obligation IDs.
- [ ] Material post-closure feedback progresses from `required-pending` to one exact acknowledged successor genesis state and input contract.

## Lineage rules

- Resolve and recompute every referenced record hash; ID-only lookup, “latest version,” and mutable-path resolution are invalid.
- A decision or waiver with `governed_implicated_release: true` must be the exact version/hash bound by the implicated final closure, conformance review, or release gate. A later superseding version may be retained only as a separate `comparison_only: true` reference and never replaces the historical governing record.
- The final-closure and release-gate hashes must resolve to the exact records governing `approved_plan_sha256`, `implementation_revision`, and the observed rollout configuration.
- `not-required` is valid only when current policy establishes that no corrective lifecycle is required. A material event requiring corrective work uses `required-pending` with null successor fields until the ordered handoff completes.
- `acknowledged` requires all successor fields and they must resolve to a genesis record and first input contract that bind the initiating feedback-event version/hash and the parent terminal state.
- Use an ordered handshake to avoid circular self-hashes: first seal the initiating `required-pending` feedback-event version; next create candidate successor genesis and first-contract records referencing that sealed event; finally append an `acknowledged` event version with compare-and-swap against the initiating event head. Only the one successor named by the accepted acknowledgment is valid and dispatchable; competing acknowledgments and unacknowledged candidates are rejected. The successor never references the later acknowledgment version.
- Once acknowledged, the successor lifecycle and record hashes are immutable in all later event versions; the response cannot return to `required-pending` or name another successor.
- Feedback-event versions are append-only. A superseding version preserves historical lineage and may add evidence, status, actions, or the ordered successor acknowledgment; it cannot replace the historical governing records or delete prior evidence.
