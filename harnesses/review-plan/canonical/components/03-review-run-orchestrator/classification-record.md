# Template: canonical classification record

## Purpose

Record the classifier’s risk and routing decision before it is converted into concrete reviewer assignments. The classification record explains why lenses and human gates are required; the review manifest defines how they will be executed.

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
classification_id: "class-..."
input_contract_id: "review-input-..."
mode: "plan-time" # plan-time | diff-time | final-rereview | implementation-conformance
status: "completed" # completed | not-established | superseded | blocked
policy_version: "..."
lens_catalog_version: "1.0"
created_at: "..."

parent_records:
  - record_type: "review-input-contract"
    record_id: "review-input-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "classification-input"

artifacts:
  authoritative_source_bundle:
    id: "..."
    schema_version: "1.0"
    version: "..."
    path: "..."
    sha256: "..."
  candidate_artifact:
    id: "..."
    kind: "plan"
    path: "..."
    sha256: "..."
  repository_revision: null
  declared_surface_manifest_sha256: "..."
  observed_surface_manifest_sha256: null
  evidence_manifest_sha256: "..."

risk:
  tier: 1
  consequence: "medium"
  reversibility: "bounded"
  novelty: "adapted"
  coupling: "boundary"
  evidence_quality: "cited"

surfaces:
  - surface_id: "..."
    kind: "..."
    observed_or_declared: "declared"
    evidence: []
    risk_effect: "..."

triggers:
  deterministic:
    - trigger_id: "..."
      policy_rule_id: "..."
      evidence: []
      selected_lens_ids: []
      required_human_gates: []
  semantic_additions:
    - trigger_id: "..."
      rationale: "..."
      evidence: []
      added_lens_ids: []
      added_human_gates: []

selected_lenses:
  - lens_id: "..."
    sources: []
    reason: "..."
    independence_required: false
    evidence_needed: []

not_selected:
  - lens_id: "..."
    reason: "..."
    policy_rule_id: "..."

unknowns:
  - unknown_id: "..."
    statement: "..."
    materiality: "high" # low | moderate | high | critical
    evidence_needed: []
    blocks_progression: true
    progression_decision_id: null
    progression_decision_record_version: null
    progression_decision_record_schema_version: null
    progression_decision_record_sha256: null
human_gates: []
rereview_triggers: []

provenance:
  deterministic_classifier_version: "..."
  semantic_classifier_prompt_version: null
  semantic_classifier_model: null
  adapter_version: "..."
  tools: []

integrity:
  hash_profile: "canonical-json-sha256-v1"
  classification_record_sha256: "..."
  supersedes_classification_id: null
  supersedes_classification_record_sha256: null
```

`input_contract_id` is a convenience index and MUST equal the `classification-input` parent tuple. Classification is invalid without that tuple or when any tuple identity/hash/artifact binding differs.

## Authority rules

- Deterministic baseline and mandatory triggers are authoritative and cannot be removed by semantic classification.
- Semantic classification may add lenses, gates, evidence needs, risk, or unknowns; it cannot subtract deterministic requirements.
- A human may add selected lenses. A component-7 waiver may waive execution but cannot remove a selected lens from the downstream manifest.
- `not-established` is required when a high-impact classification fact lacks evidence. Such a record cannot authorize a low-risk route.
- Any artifact, policy, or material-surface change creates a new classification record.
