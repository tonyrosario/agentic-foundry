# Template: implementation release-gate record

## Purpose

Bind conformance, diff-time review, human release authority, and actual execution to one exact implementation revision and rollout configuration. A conformance verdict alone cannot authorize release.

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
release_gate_record_id: "release-gate-..."
release_gate_record_version: "..."
input_contract_id: "review-input-..."
final_closure_record_id: "closure-..."
conformance_review_id: "conf-..."
conformance_review_sha256: "..."
classification_id_diff_time: "class-..."
review_manifest_id_diff_time: "manifest-..."
policy_version: "..."
state: "blocked" # blocked | awaiting-authority | authorized | released | revoked | rolled-back | superseded
created_at: "..."

parent_records:
  - record_type: "review-input-contract"
    record_id: "review-input-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "release-input"
  - record_type: "final-closure"
    record_id: "closure-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "approved-plan-closure"
  - record_type: "conformance-review"
    record_id: "conf-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "release-conformance"
  - record_type: "classification-record"
    record_id: "class-..."
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

artifacts:
  approved_plan_sha256: "..."
  implementation_base_revision: "..."
  implementation_head_revision: "..."
  changed_surface_manifest_sha256: "..."
  rollout_configuration_sha256: "..."
  evidence_manifest_sha256: "..."

plan_closure:
  final_closure_record_sha256: "..."
  final_closure_status: "approved" # approved | approved-with-residual-risk
  final_closure_final_plan_sha256: "..."
  current_not_revoked_or_superseded: false

conformance:
  status: "conforms" # conforms | conforms-with-accepted-risk
  implementation_head_revision: "..."
  approved_plan_sha256: "..."
  rollout_configuration_sha256: "..."
  current_not_revoked_or_superseded: false

gates:
  final_plan_closure_valid_and_bound: false
  conformance_record_valid_and_bound: false
  implementation_conforms: false
  material_deviations_authorized: false
  all_required_diff_reviews_complete: false
  diff_adjudication_complete: false
  high_impact_unknowns_resolved: false
  decisions_and_waivers_valid: false
  rollout_monitoring_and_rollback_ready: false
  required_human_gates_complete: false

reviews:
  required_review_ids: []
  completed_review_executions:
    - review_id: "rev-..."
      review_execution_id: "revexec-..."
      schema_version: "1.0"
      logical_record_version: null
      review_record_sha256: "..."
      result: "established" # established | not-established | failed
      credited_lens_ids: []
  finding_ledger_id: "..."
  finding_ledger_version: "..."
  finding_ledger_schema_version: "1.0"
  finding_ledger_sha256: "..."

authority:
  required_logical_role: "release-authority"
  release_decision_id: null
  release_decision_record_version: null
  release_decision_record_schema_version: null
  release_decision_record_sha256: null
  authority_matrix_id: null
  authority_matrix_version: null
  authority_matrix_schema_version: null
  authority_matrix_sha256: null
  authority_verified: false
  authorized_revision: null
  authorized_rollout_configuration_sha256: null

execution:
  release_id: null
  released_revision: null
  released_rollout_configuration_sha256: null
  executed_by: null
  executed_at: null

integrity:
  hash_profile: "canonical-json-sha256-v1"
  record_sha256: "..."
  supersedes_release_gate_record_id: null
  supersedes_release_gate_record_version: null
  supersedes_release_gate_record_sha256: null
```

## Transition rules

- Release-gate records are append-only versions under one `release_gate_record_id`. Every append uses compare-and-swap against the exact current `(ID, version, hash)` head; only one successor version is accepted. A competing or unacknowledged candidate is an orphan and has no gate authority.
- `blocked → awaiting-authority`: every gate is true and exact artifact hashes agree. `final_plan_closure_valid_and_bound` requires the referenced closure record to resolve by hash, have current status `approved` or `approved-with-residual-risk`, be neither revoked nor superseded, and satisfy `final_closure_final_plan_sha256 == artifacts.approved_plan_sha256`. `conformance_record_valid_and_bound` requires the referenced conformance record to resolve by `conformance_review_sha256`, have current status `conforms` or `conforms-with-accepted-risk`, and match the release gate’s approved-plan hash, implementation head revision, and rollout-configuration hash.
- `awaiting-authority → authorized`: component 7 supplies a valid decision record that references the ID/version/schema/hash of the accepted `awaiting-authority` gate head, the new authorized gate version references the decision-record and authority-matrix ID/version/schema/hash tuples, and the gate supersedes the exact request-gate ID/version/hash by atomic compare-and-swap.
- `authorized → released`: the recorded operator/system executes exactly the authorized revision and configuration.
- Any material artifact change, waiver invalidation, new high-impact evidence, or authority revocation moves the gate to `blocked` or `revoked` and requires diff-time reclassification.
- A rollback records `rolled-back`, opens a component-8 feedback event, and cannot be reused for another release attempt.

There is no implicit approval. A closure, conformance, decision, or authority-matrix ID without a verified record hash, current valid status, and exact artifact binding is invalid. Missing reviews, decisions, hashes, or unknown-resolution evidence keep the gate blocked.

Top-level lineage IDs and review-ID lists are non-authoritative indexes. Parent records and completed review executions must validate through their keyed canonical tuples, and release authority applies only to the accepted gate-version head.
