# Template: risk, review, or policy waiver record

## Record

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
waiver_id: "wvr-..."
waiver_record_version: "..."
waiver_type: "..." # residual-risk | review | policy-exception | emergency-authorization
status: "proposed" # proposed | active | rejected | expired | revoked | superseded
created_at: "..."

parent_records:
  - record_type: "review-input-contract"
    record_id: "review-input-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "waiver-scope"
  - record_type: "classification-record"
    record_id: "class-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "waiver-classification"
  - record_type: "human-decision"
    record_id: "dec-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: "..."
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "waiver-authorization"

scope:
  input_contract_id: "..."
  decision_id: "..."
  decision_record_version: "..."
  decision_record_schema_version: "1.0"
  decision_record_sha256: "..."
  classification_id: "..."
  finding_ids: []
  finding_refs:
    - finding_id: "find-..."
      finding_schema_version: "1.0"
      finding_sha256: "..."
  policy_rule_ids: []
  review_lens_ids: []
  lens_catalog_version: "1.0"
  authoritative_source_bundle_id: "..."
  authoritative_source_bundle_schema_version: "1.0"
  authoritative_source_bundle_version: "..."
  authoritative_source_bundle_sha256: "..."
  plan_sha256: "..."
  repository_revision: "..."
  environments: []
  users_services_or_data: []
  actions_authorized: []
  actions_not_authorized: []

risk:
  statement: "If ..., then ..., causing ..."
  consequence: "..."
  likelihood_basis: "..."
  blast_radius: "..."
  reversibility: "..."
  detection: "..."
  unknowns: []

rationale:
  why_resolution_or_review_is_not_currently_practical: "..."
  alternatives_considered: []
  why_benefit_exceeds_residual_risk: "..."
  dissenting_evidence: []

controls:
  compensating_controls:
    - control: "..."
      owner: "..."
      verification: "..."
  monitoring:
    - signal: "..."
      threshold: "..."
      owner: "..."
      action: "..."
  rollback_or_containment: []
  required_follow_up_work: []

authority:
  required_logical_role: "..."
  accepted_by: "..."
  authority_matrix_id: "authority-matrix-..."
  authority_matrix_version: "..."
  authority_matrix_schema_version: "1.0"
  authority_matrix_sha256: "..."
  authority_rule_ids: []
  authority_entry_ids: []
  authority_verified_by: "..."
  additional_approvals: []
  accepted_at: "..."
  signature_or_audit_reference: "..."

lifecycle:
  effective_at: "..."
  expires_at_or_event: "..."
  review_at_or_event: "..."
  invalidation_triggers: []
  revocation_triggers: []
  required_rereview_lenses: []
  component_8_feedback_ids: []

closure:
  closed_at: null
  closure_reason: null
  permanent_resolution_reference: null
  outcome_evidence: []

integrity:
  hash_profile: "canonical-json-sha256-v1"
  waiver_record_sha256: "..."
  supersedes_waiver_id: null
  supersedes_waiver_record_sha256: null
```

## Additional fields for review waivers

```yaml
review_waiver:
  deterministic_trigger: "..."
  selected_lens_preserved_in_manifest: true
  requested_change: "omit" # omit | delay | consolidate
  equivalent_evidence: []
  failure_modes_that_may_be_missed: []
  restored_coverage_plan: []
```

## Additional fields for emergency authorization

```yaml
emergency:
  authorizing_decision_class: "operational"
  incident_or_event_id: "..."
  imminent_harm: "..."
  normal_process_harm_or_delay: "..."
  start_time: "..."
  hard_stop_time: "..."
  executing_operator: "..."
  second_controller: null
  dual_control_exception_basis: null
  action_log: "..."
  retrospective_due_at: "..."
```

## Validity checklist

- [ ] Input-contract, classification, decision, source-bundle, and finding references use complete keyed identity/version/hash tuples.
- [ ] The waiver applies to exact versioned artifacts and bounded environments/actions.
- [ ] The risk describes a trigger, consequence, and affected surface.
- [ ] Alternatives and dissenting evidence are preserved.
- [ ] Controls, monitoring, containment, and owners are concrete.
- [ ] The acceptor has verified authority for this risk and magnitude.
- [ ] Authority resolves through the exact active authority-matrix ID, version, hash, rules, and entries recorded above.
- [ ] Expiry, invalidation, revocation, and re-review are explicit.
- [ ] Review waivers retain the waived lens in the classifier manifest.
- [ ] An emergency authorization binds a human decision and matched authority-matrix rule whose canonical class is exactly `operational`.
- [ ] Emergency authorizations have a hard stop, monitoring and rollback/containment, a second controller or a documented infeasibility basis, and retrospective review.
- [ ] The final closure gate can verify every active condition.

An incomplete, expired, revoked, authority-invalid, or artifact-mismatched waiver is treated as absent.
