# Template: escalation and human-decision record

## Record

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
escalation_id: "esc-..."
decision_id: "dec-..."
decision_record_version: "..."
created_at: "..."
status: "pending" # pending | decided | applied | verified | closed | expired | revoked
lens_catalog_version: "1.0"

trigger:
  class: "..." # specification | evidence | residual-risk | review-waiver | policy-exception | operational | release | cancellation | evaluation-promotion-rollback
  source_component: "..."
  source_records:
    - record_type: "..."
      record_id: "..."
      record_sub_id: null
      schema_version: "1.0"
      logical_record_version: null
      record_sha256: "..."
      lifecycle_id: "life-..." # null only for an intentionally lifecycle-independent evaluation record
      role: "decision-trigger"
  input_contract_id: "..."
  classification_id: "..."
  review_ids: []
  finding_ids: []
  policy_rule_ids: []
  risk_tier: null
  summary: "..."

artifacts:
  authoritative_source_bundle:
    id: "..."
    schema_version: "1.0"
    version: "..."
    path: "..."
    sha256: "..."
  candidate_plan:
    path: "..."
    sha256: "..."
  evidence_manifest:
    path: "..."
    sha256: "..."
  finding_ledger:
    id: "..."
    version: "..."
    schema_version: "1.0"
    path: "..."
    sha256: "..."

decision_request:
  question: "..."
  deadline_or_event: "..."
  blocked_pipeline_stages: []
  facts: []
  inferences: []
  unknowns: []
  options:
    - id: "..."
      description: "..."
      benefits: []
      risks: []
      reversibility: "..."
      downstream_effects: []
  recommendation: "..."
  dissenting_evidence: []

authority:
  required_logical_roles: []
  assigned_decision_owner: "..."
  authority_matrix_id: "authority-matrix-..."
  authority_matrix_version: "..."
  authority_matrix_schema_version: "1.0"
  authority_matrix_sha256: "..."
  authority_rule_ids: []
  authority_entry_ids: []
  authority_verified_by: "..."
  separation_of_duties_required: false
  additional_approvers: []

decision:
  state: null # approved | approved_with_conditions | rejected | deferred | more_evidence_required | not_authorized
  selected_option: null
  rationale: null
  conditions: []
  residual_risks: []
  required_waiver_ids: []
  required_artifact_updates: []
  required_rereview_lenses: []
  required_human_gates: []
  decided_by: null
  decided_at: null
  signature_or_audit_reference: null

release_authorization:
  authorization_request_release_gate_record_id: null
  authorization_request_release_gate_record_version: null
  authorization_request_release_gate_record_schema_version: null
  authorization_request_release_gate_record_sha256: null
  implementation_revision: null
  rollout_configuration_sha256: null
  environments: []
  authorization_starts_at: null
  authorization_expires_at: null

evaluation_authorization:
  target_kind: null # evaluation-run-effect | evaluation-suite-activation
  evaluation_run_id: null
  evaluation_run_schema_version: null
  evaluation_run_sha256: null
  evaluation_suite_id: null
  evaluation_suite_version: null
  evaluation_suite_schema_version: null
  evaluation_suite_manifest_sha256: null
  candidate_component_id: null
  candidate_component_version: null
  authorized_effect: null # PROMOTE | SHADOW ONLY | BLOCK | ROLL BACK
  registry_or_environment_scope: []
  authorization_expires_at_or_event: null

supersession_authorization:
  parent_lifecycle_id: null
  expected_parent_head_state_record_id: null
  expected_parent_head_transition_number: null
  expected_parent_head_state_record_sha256: null
  reserved_successor_lifecycle_id: null
  successor_origin_kind: null # superseding-outcome | post-cancellation-successor

application:
  source_contract_version_after: null
  plan_version_after: null
  finding_ledger_version_after: null
  classifier_run_after: null
  rereview_ids: []
  applied_by: null
  applied_at: null

verification:
  conditions_verified: []
  final_plan_sha256: null
  final_closure_record_id: null
  final_closure_record_schema_version: null
  final_closure_record_sha256: null
  verified_by: null
  verified_at: null

lifecycle:
  expires_at_or_event: null
  invalidation_triggers: []
  revoked_at: null
  revocation_reason: null
  component_8_feedback_ids: []

integrity:
  hash_profile: "canonical-json-sha256-v1"
  decision_record_sha256: "..."
  supersedes_decision_id: null
  supersedes_decision_record_sha256: null
```

## Decision-ready checklist

- [ ] The decision class is an exact value from the shared component-7 catalog and resolves to an active authority-matrix rule of the same class.
- [ ] A decision authorizing an `emergency-authorization` waiver uses `trigger.class: operational` and resolves to an `operational` authority-matrix rule with all required emergency controls.
- [ ] The request asks one decision that a named authority can make.
- [ ] Source, plan, evidence, and ledger versions are frozen.
- [ ] Facts, inferences, unknowns, and opinions are separated.
- [ ] Consequence, reversibility, blast radius, and affected owners are clear.
- [ ] Credible options and downstream effects are presented.
- [ ] Dissenting material evidence is retained.
- [ ] The assigned person’s authority is independently verified.
- [ ] Authority resolves through the exact active authority-matrix ID, version, hash, rules, and entries recorded above.
- [ ] A release authorization references the exact ID/version/schema/hash of the accepted `awaiting-authority` release-gate head.
- [ ] An evaluation authorization references the completed evaluation-run ID/schema/hash and exact candidate component/version.
- [ ] An evaluation-suite activation references the candidate suite ID/version/schema/hash; the registry applies active status only after the later decision validates.
- [ ] A supersession authorization binds the expected parent head and one reserved, unused successor lifecycle ID.
- [ ] The decision state and conditions are explicit.
- [ ] Required source/plan changes and re-reviews are listed.
- [ ] Closure verifies the exact final-plan hash.

If the decision owner does not respond, leave the record `pending`; never infer approval.

Decision records are append-only versions. For release authorization, the decision hashes the accepted `awaiting-authority` release-gate ID/version head. The subsequent authorized gate version hashes this completed decision record and atomically supersedes the request gate; this ordered handshake avoids circular self-hashes.

For evaluation authorization, the completed evaluation run is hashed first and the later component-7 decision binds it. The component registry validates the run, decision, and authority matrix before applying the effect; the evaluation run never embeds the later decision hash.

When `trigger.class` is `evaluation-promotion-rollback`, exactly one evaluation target kind is populated. `evaluation-run-effect` requires the run fields, candidate component/version, and authorized effect; `evaluation-suite-activation` requires the suite fields. The decision’s selected option must equal the authorized effect or activation, and the authority rule must use the same shared class.

When a decision authorizes a waiver whose `waiver_type` is `emergency-authorization`, `trigger.class` MUST be `operational`. The linked waiver and matched authority-matrix rule must carry the same mapping; any other class is invalid.
