# Template: post-implementation conformance review

## Purpose

Produce a machine-checkable record comparing the authoritative outcome and approved plan with the exact implementation revision, verification, rollout configuration, controls, decisions, and waivers. Conformance is evidence for the release gate; it is not release authorization.

## Record

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
conformance_review_id: "conf-..."
input_contract_id: "review-input-..."
classification_id_plan_time: "class-..."
classification_id_diff_time: "class-..."
review_manifest_id_diff_time: "manifest-..."
final_closure_record_id: "closure-..."
finding_ledger_id_diff_time: "ledger-..."
policy_version: "..."
lens_catalog_version: "1.0"
status: "reviewing" # reviewing | conforms | conforms-with-accepted-risk | review-required | nonconforming | not-established | superseded | revoked
reviewer_identity_and_version: "..."
reviewed_at: "..."

parent_records:
  - record_type: "review-input-contract"
    record_id: "review-input-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "conformance-input"
  - record_type: "classification-record"
    record_id: "class-plan-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "plan-time-classification"
  - record_type: "classification-record"
    record_id: "class-diff-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "diff-time-classification"
  - record_type: "review-manifest"
    record_id: "manifest-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: "..."
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "diff-time-review-manifest"
  - record_type: "final-closure"
    record_id: "closure-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "approved-plan-closure"
  - record_type: "finding-ledger"
    record_id: "ledger-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: "..."
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "diff-time-ledger"

artifacts:
  authoritative_source_bundle:
    id: "..."
    schema_version: "1.0"
    version: "..."
    path: "..."
    sha256: "..."
  approved_final_plan:
    path: "..."
    sha256: "..."
  final_closure_record_sha256: "..."
  finding_ledger_sha256: "..."
  implementation_base_revision: "..."
  implementation_head_revision: "..."
  changed_surface_manifest_sha256: "..."
  test_and_verification_manifest_sha256: "..."
  rollout_configuration_sha256: "..."
  monitoring_and_operations_manifest_sha256: "..."

requirement_conformance:
  - criterion_id: "..."
    approved_plan_commitment: "..."
    implementation_evidence: []
    verification_evidence: []
    status: "met" # met | partial | not-met | not-established

surfaces_and_deviations:
  - surface_id: "..."
    planned: true
    implemented: true
    deviation: null
    materiality: "low"
    authorization_decision_id: null
    authorization_decision_record_version: null
    authorization_decision_record_schema_version: null
    authorization_decision_record_sha256: null
    classification_id: "class-..."
    classification_schema_version: "1.0"
    classification_record_sha256: "..."
    required_review_ids: []
    completed_review_executions:
      - review_id: "rev-..."
        review_execution_id: "revexec-..."
        review_record_schema_version: "1.0"
        review_record_sha256: "..."
    risk_effect: "..."

finding_decision_and_waiver_closure:
  - record_id: "..."
    record_version: "..."
    record_schema_version: "1.0"
    record_sha256: "..."
    lifecycle_id: "life-..."
    kind: "finding" # finding | decision | waiver
    required_effect_or_condition: "..."
    implementation_evidence: []
    authority_and_scope_valid: false
    conditions_satisfied: false
    status: "..."

diff_time_reviews:
  required_review_ids: []
  completed_review_executions:
    - review_id: "rev-..."
      review_execution_id: "revexec-..."
      schema_version: "1.0"
      logical_record_version: null
      review_record_sha256: "..."
      result: "established" # established | not-established | failed
      credited_lens_ids: []
  adjudication_ledger_id: "ledger-..."
  adjudication_ledger_version: "..."
  adjudication_ledger_schema_version: "1.0"
  adjudication_ledger_sha256: "..."
  all_required_reviews_complete: false

controls:
  expected_observable_outcomes: []
  observation_windows: []
  leading_indicators: []
  failure_and_degradation_signals: []
  stop_and_rollback_thresholds: []
  containment_and_recovery_owners: []
  rollout_monitoring_and_rollback_ready: false

unresolved_items:
  - unknown_id: "..."
    statement: "..."
    materiality: "moderate"
    blocks_progression: true
    progression_basis: null
    progression_decision_id: null
    progression_decision_record_version: null
    progression_decision_record_schema_version: null
    progression_decision_record_sha256: null
    progression_owner: null
    expires_at_or_event: null
    required_rereview_lenses: []

verdict:
  value: "review-required" # conforms | conforms-with-accepted-risk | review-required | nonconforming | not-established
  rationale: "..."
  material_deviation_ids: []
  newly_triggered_review_ids: []
  human_gate_ids: []
  active_residual_risk_waivers:
    - waiver_id: "wvr-..."
      waiver_record_version: "..."
      waiver_record_schema_version: "1.0"
      waiver_record_sha256: "..."
  feedback_events:
    - feedback_event_id: "fdb-..."
      feedback_event_version: "..."
      feedback_event_schema_version: "1.0"
      feedback_event_sha256: "..."

integrity:
  hash_profile: "canonical-json-sha256-v1"
  conformance_review_sha256: "..."
  supersedes_conformance_review_id: null
  supersedes_conformance_review_sha256: null
```

## Method

1. Reconstruct source-contract success criteria without relying on the implementation summary.
2. Verify the approved plan and final closure resolve by hash and belong to this lifecycle.
3. Compare planned and actual files, interfaces, schemas, dependencies, permissions, infrastructure, tests, and rollout effects.
4. Identify every material deviation and verify that it was classified, authorized, and reviewed against the exact implementation revision.
5. Verify every confirmed finding’s required implementation consequence.
6. Verify active decisions and waivers against scope, assumptions, conditions, controls, authority, expiry, and revocation.
7. Judge whether tests and operational signals discriminate intended success from important plausible failures.
8. Confirm rollback, containment, ownership, and observation windows exist where required.
9. Complete every triggered implementation lens; a required lens may not remain merely marked or pending at release.
10. Record every unknown using the canonical nonblocking-progression fields; unresolved items default to blocking.
11. Bind the verdict and self-hash to the exact implementation revision and rollout configuration.
12. Credit reviews, manifests, ledgers, decisions, and waivers only through keyed canonical identity/version/hash tuples; top-level IDs are non-authoritative indexes.

## Hard gates

The record cannot have status `conforms` or `conforms-with-accepted-risk` when:

- A source criterion is partial, not met, or not established.
- The approved-plan hash differs from the final closure’s final-plan hash.
- The closure is not currently approved or has been revoked/superseded.
- A material implementation deviation lacks classification, authority, completed reviews, or adjudication.
- A required diff-time review is missing or bound to another implementation revision.
- A finding, decision, waiver, or control condition is unsatisfied or invalid.
- Rollout monitoring, containment, ownership, or rollback is required but not ready.
- A high/critical-impact unknown remains, or a lower-impact unresolved item lacks a valid progression decision, owner, expiry, and re-review requirement.
- Any identity, record hash, artifact hash, or policy/lens-catalog version fails validation.

## Release handoff

Only `conforms` and `conforms-with-accepted-risk` may satisfy the release gate’s conformance predicate. The release gate must validate this record’s ID, self-hash, status, implementation head revision, approved-plan hash, and rollout-configuration hash.

Even a valid conformance record moves the release gate only to `awaiting-authority`. Component 7’s named release authority must issue an exact-revision decision. Any material change creates a new conformance record and revokes the prior release binding.
