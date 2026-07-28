# Template: final closure record

## Record

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
final_closure_record_id: "closure-..."
input_contract_id: "review-input-..."
classification_id: "class-..."
review_manifest_id: "manifest-..."
finding_ledger_id: "ledger-..."
finding_ledger_version: "..."
policy_version: "..."
lens_catalog_version: "1.0"
status: "reviewing" # reviewing | approved | approved-with-residual-risk | revision-required | blocked | not-established | superseded | revoked
created_at: "..."

parent_records:
  - record_type: "review-input-contract"
    record_id: "review-input-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "final-review-input"
  - record_type: "classification-record"
    record_id: "class-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "final-classification"
  - record_type: "review-manifest"
    record_id: "manifest-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: "..."
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "final-review-manifest"
  - record_type: "finding-ledger"
    record_id: "ledger-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: "..."
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "closure-ledger"

artifacts:
  authoritative_source_bundle:
    id: "..."
    schema_version: "1.0"
    version: "..."
    path: "..."
    sha256: "..."
  previous_reviewed_plan:
    id: "..."
    version: "..."
    path: "..."
    sha256: "..."
  final_candidate_plan:
    id: "..."
    version: "..."
    path: "..."
    sha256: "..."
  final_review_manifest_sha256: "..."
  final_review_manifest_candidate_sha256: "..."
  finding_ledger_sha256: "..."
  changed_surface_manifest_sha256: "..."
  current_evidence_manifest_sha256: "..."

source_criteria:
  - criterion_id: "..."
    source_location:
      source_bundle_id: "source-bundle-..."
      source_artifact_id: "..."
      artifact_local_location: "..."
    status: "met" # met | not-met | not-established | source-contract-revised
    plan_locations: []
    verification: []
    superseding_source_decision_id: null

finding_closure:
  - ledger_finding_id: "lf-..."
    source_finding_ids: []
    finding_type: "..."
    disposition: "..."
    remediation_state: "..."
    resolution_evidence: []
    decision_records: []
    waiver_records: []
    required_rereview_ids: []
    closure_status: "..." # closed | accepted-residual-risk | open | not-established

decisions_and_waivers:
  - record_id: "..."
    record_version: "..."
    record_schema_version: "1.0"
    record_sha256: "..."
    lifecycle_id: "life-..."
    kind: "..."
    authority_matrix_id: "..."
    authority_matrix_version: "..."
    authority_matrix_schema_version: "1.0"
    authority_matrix_sha256: "..."
    authority_valid: false
    artifact_scope_valid: false
    conditions_satisfied: false
    not_expired_or_revoked: false
    verification_evidence: []

rereviews:
  selected_lens_ids: []
  execution_required_lens_ids: []
  waived_lens_ids: []
  waived_lenses:
    - lens_id: "..."
      waiver_id: "wvr-..."
      waiver_record_version: "..."
      waiver_record_schema_version: "1.0"
      waiver_record_sha256: "..."
  completed_lens_ids: []
  required_review_ids: []
  completed_review_executions:
    - review_id: "rev-..."
      review_execution_id: "revexec-..."
      schema_version: "1.0"
      logical_record_version: null
      review_record_sha256: "..."
      result: "established" # established | not-established | failed
      credited_lens_ids: []
  all_execution_required_lenses_complete: false

review_execution_closure:
  - review_id: "rev-..."
    review_execution_id: "revexec-..."
    review_record_schema_version: "1.0"
    review_record_sha256: "..."
    required_lens_ids: []
    execution_result: "established" # established | not-established | failed
    ledger_unresolved_review_id: null
    replacement_review_ids: []
    progression_basis: null
    progression_decision_id: null
    progression_decision_record_version: null
    progression_decision_record_schema_version: null
    progression_decision_record_sha256: null
    progression_owner: null
    expires_at_or_event: null
    required_rereview_lens_ids: []
    progression_record_valid: false
    closure_status: "established" # established | resolved-by-replacement | valid-nonblocking-progression | blocking

unresolved_items:
  - ledger_finding_id: "lf-..."
    materiality: "moderate"
    progression_basis: "..."
    progression_decision_id: "dec-..."
    progression_decision_record_version: "..."
    progression_decision_record_schema_version: "1.0"
    progression_decision_record_sha256: "..."
    progression_owner: "..."
    expires_at_or_event: "..."
    required_rereview_lenses: []
    progression_record_valid: false

verdict:
  value: "..."
  rationale: "..."
  residual_risk_waiver_ids: []
  implementation_revalidation_requirements: []

authority:
  final_reviewer_identity_and_version: "..."
  human_approval_required: false
  human_decision_id: null
  human_decision_record_version: null
  human_decision_record_schema_version: null
  human_decision_record_sha256: null
  authority_matrix_id: null
  authority_matrix_version: null
  authority_matrix_schema_version: null
  authority_matrix_sha256: null

integrity:
  hash_profile: "canonical-json-sha256-v1"
  closure_record_sha256: "..."
  supersedes_closure_record_id: null
  supersedes_closure_record_sha256: null
```

## Hard gates

An approval status is invalid when any of these is true:

- A top-level parent ID/version/hash or final-review manifest hash differs from its canonical `parent_records` tuple.
- A source criterion is `not-met` or `not-established`.
- A historical criterion is `source-contract-revised` but the superseding authoritative source contract was not reclassified/re-reviewed or its replacement criterion is not `met`.
- A source-requirement defect is open, deferred, or represented only by a waiver.
- A raw finding lacks a canonical ledger mapping.
- A confirmed finding lacks required remediation, decision evidence, or re-review.
- A mandatory review is missing.
- A required or credited review lacks one keyed `(review_id, review_execution_id, schema_version, review_record_sha256)` tuple, or the tuple result differs from `review_execution_closure`.
- A classifier-selected lens is absent from the final manifest, a waived lens is not preserved with a valid waiver, or an unwaived selected lens is absent from `execution_required_lens_ids`.
- `all_execution_required_lenses_complete` is false.
- A required failed or `not-established` review execution lacks a canonical unresolved-review ledger item.
- A required failed or `not-established` review remains unresolved without a completed replacement review or a valid nonblocking progression record.
- A `review_execution_closure` entry marked `valid-nonblocking-progression` lacks an evidence-backed progression basis; exact component-7 decision ID/version/schema/hash; owner; unexpired review event; required re-review lenses; `progression_record_valid: true`; or an exact match to the bound ledger’s unresolved item for the same review execution.
- A decision or waiver has invalid authority, scope, conditions, expiry, revocation, or artifact binding.
- `final_candidate_plan.sha256` differs from the exact candidate hash in the final-review manifest (`final_review_manifest_candidate_sha256`).
- A material change was not reclassified and routed through affected reviews.
- A high-impact fact remains unknown.
- Any unresolved item lacks a valid nonblocking progression record, or its decision, owner, expiry, artifact scope, or required re-review is invalid.

Approval is version-specific. Any material source, plan, ledger, policy, evidence, decision, or waiver change supersedes or revokes the closure record and returns the lifecycle to the applicable state.

The previous ledger-reviewed plan may differ from the final candidate after remediation. That difference is valid only when the final candidate was reclassified, routed through every affected review, and bound as the candidate in the final-review manifest.
