# Template: immutable review record

## Purpose

Record one reviewer execution as an immutable raw observation. This record contains what the reviewer saw, did, found, and concluded. It does not adjudicate findings, track remediation, accept risk, or certify later outcomes.

Component 4’s canonical finding ledger is the sole authority for dispositions and remediation. Component 5 owns final-plan closure. Component 8 owns implementation and outcome feedback.

## Record

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
review_id: "rev-..."
review_execution_id: "revexec-..."
input_contract_id: "review-input-..."
classification_id: "class-..."
review_manifest_id: "manifest-..."
policy_version: "..."
status: "completed" # completed | failed | not-established | superseded
started_at: "..."
completed_at: "..."

parent_records:
  - record_type: "review-input-contract"
    record_id: "review-input-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "review-input"
  - record_type: "classification-record"
    record_id: "class-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "governing-classification"
  - record_type: "review-manifest"
    record_id: "manifest-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: "..."
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "governing-assignment"

assignment:
  reviewer_id: "..."
  assigned_lens_ids: []
  lens_catalog_version: "1.0"
  authorized_decision: "..."
  output_schema_version: "..."
  human_owner: "..."

artifacts:
  authoritative_source_bundle:
    id: "..."
    schema_version: "1.0"
    version: "..."
    path: "..."
    sha256: "..."
  candidate_plan:
    id: "..."
    path: "..."
    sha256: "..."
  inherited_documents: []
  repository_revision: null
  evidence_manifest_sha256: "..."
  excluded_context: []

execution:
  prompt_or_skill_id: "..."
  prompt_or_skill_version: "..."
  model_provider_version: "..."
  reasoning_configuration: "..."
  adapter_version: "..."
  context_mode: "fresh" # fresh | inherited | forked
  repository_guidance_loaded: []
  ambient_memory_allowed: false
  tools_used: []
  tool_and_permission_policy_version: "..."
  information_flow_exceptions: []

completion:
  result: "established" # established | not-established | failed
  not_established_reason: null
  affected_lens_ids: []
  missing_evidence_or_capability: []
  estimated_materiality: null # low | moderate | high | critical

independent_analysis:
  recorded_before_prior_reviews_visible: true
  success_criteria_or_threat_model: []
  facts: []
  inferences: []
  unknowns: []

findings:
  - finding_id: "find-..."
    finding_schema_version: "1.0"
    finding_sha256: "..."

verdict:
  value: "..."
  most_consequential_finding_id: null
  facts_not_established: []
  human_decisions_required: []

operations:
  cost: null
  latency: null
  raw_output_reference: "..."
  trace_reference: null

integrity:
  hash_profile: "canonical-json-sha256-v1"
  record_sha256: "..."
  supersedes_review_id: null
  supersedes_review_execution_id: null
  supersedes_review_record_schema_version: null
  supersedes_review_record_sha256: null
```

## Integrity rules

- `lifecycle_id`, `input_contract_id`, `classification_id`, and `review_manifest_id` MUST match the canonical parent tuples and resolve to the same lifecycle instance.
- `completion.result` is the authoritative downstream routing key. For a current, non-superseded record, `status: completed` requires `completion.result: established`, `status: failed` requires `completion.result: failed`, and `status: not-established` requires `completion.result: not-established`; every other pairing is invalid. A `superseded` record preserves its historical `completion.result` but cannot satisfy a current execution requirement.
- A review execution is credited only through `(review_id, review_execution_id, schema_version, record_sha256)`. Neither `review_id` alone nor another execution’s hash may stand in for it.
- Source and plan hashes MUST match the input contract and review manifest.
- Every `finding_id` MUST be unique within the lifecycle and conform to [the common finding schema](finding-record.md).
- Findings are sealed before the review record. Each tuple must carry this record’s exact `review_id` and `review_execution_id`; the review record then owns the association by hashing the finding ID/schema/hash tuple.
- A completed raw review record is immutable. Correct factual recording errors by issuing a superseding record while preserving the original.
- A reviewer MAY propose a disposition but MUST NOT set the canonical adjudication disposition.
- A required execution with `completion.result: not-established` MUST retain its reason, affected lens IDs, missing evidence/capability, and estimated materiality even when it produces no findings. Component 4 must convert it into a canonical unresolved-review ledger item.
- Other reviewers’ conclusions MUST remain unavailable until the reviewer’s independent analysis is recorded when independence is required.
- `not-established` is a valid terminal execution status when required evidence or isolation cannot be established.

## Output boundary

The review record may flow only to:

1. Component 4 for adjudication.
2. Component 6 for evaluation.
3. Component 8 for retrospective outcome analysis.

Revisers and final reviewers should consume the canonical component-4 ledger rather than treating raw reviewer recommendations as accepted work.
