# Template: canonical review manifest

## Purpose

Bind one classification decision to exact artifacts, required review lenses, concrete reviewer assignments, evidence projections, human gates, waivers, and re-review triggers. This is the orchestrator’s authoritative dispatch contract.

This folder defines canonical, vendor-neutral orchestration behavior. Executable dispatchers, validators, storage, and Claude/Codex adapters are separate implementations that must preserve these semantics.

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
review_manifest_id: "manifest-..."
review_manifest_version: "..."
input_contract_id: "review-input-..."
classification_id: "class-..."
mode: "plan-time" # plan-time | diff-time | final-rereview | implementation-conformance
status: "draft" # draft | validated | dispatching | reviews-complete | superseded | blocked
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
    role: "dispatch-input"
  - record_type: "classification-record"
    record_id: "class-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "governing-classification"

artifacts:
  authoritative_source_bundle:
    id: "..."
    schema_version: "1.0"
    version: "..."
    path: "..."
    sha256: "..."
  candidate_artifact:
    id: "..."
    kind: "plan" # plan | implementation-diff | final-plan
    path: "..."
    sha256: "..."
  repository_revision: null
  evidence_manifest_sha256: "..."

risk:
  tier: 1
  consequence: "medium"
  reversibility: "bounded"
  novelty: "adapted"
  coupling: "boundary"
  evidence_quality: "cited"
  surfaces: []
  unknowns:
    - unknown_id: "..."
      materiality: "high"
      blocks_progression: true
      progression_decision_id: null
      progression_decision_record_version: null
      progression_decision_record_schema_version: null
      progression_decision_record_sha256: null

selected_lenses:
  - lens_id: "independent-outcome"
    source: "baseline" # baseline | deterministic | semantic | human
    trigger_id: "..."
    reason: "..."
    evidence_needed: []
    independence_required: true
    exit_criteria: []
    waiver_id: null

execution_required_lens_ids:
  - "independent-outcome"

execution_portfolio:
  - review_id: "rev-..."
    lens_ids: []
    reviewer_capability: "strong" # standard | strong | domain-expert | human
    isolation: "fresh" # fresh | inherited | not-applicable
    evidence_projection_id: "projection-..."
    prompt_or_skill_id: "..."
    prompt_or_skill_version: "..."
    adapter: "canonical" # canonical | claude-code | codex
    status: "scheduled" # scheduled | running | completed | failed | not-established
    review_execution_ids: []

not_selected:
  - lens_id: "..."
    reason: "..."
    policy_rule_id: "..."

human_gates:
  - gate_id: "..."
    decision_class: "..."
    required_authority: "..."
    decision_id: null
    decision_record_version: null
    decision_record_schema_version: null
    decision_record_sha256: null
    state: "pending"

waivers:
  - waiver_id: "..."
    waiver_record_version: "..."
    waiver_record_schema_version: "1.0"
    waiver_record_sha256: "..."
    authority_matrix_id: "..."
    authority_matrix_version: "..."
    authority_matrix_schema_version: "1.0"
    authority_matrix_sha256: "..."
    lens_id: "..."
    validity_checked: false
    selected_lens_preserved: true

rereview_triggers: []

provenance:
  deterministic_policy_version: "..."
  semantic_classifier_prompt_version: "..."
  semantic_classifier_model: null
  adapter_version: "..."
  tools: []

integrity:
  hash_profile: "canonical-json-sha256-v1"
  manifest_sha256: "..."
  supersedes_review_manifest_id: null
  supersedes_manifest_sha256: null
```

## Validation rules

- All IDs and hashes must satisfy [the record-lineage contract](record-lineage-and-integrity.md).
- Top-level `input_contract_id` and `classification_id` are non-authoritative indexes and must equal the complete `parent_records` tuples; no active/latest resolution is permitted.
- Every lens ID must exist in the declared [canonical lens catalog](review-lens-catalog.md); deprecated labels must be normalized before validation.
- Baseline and deterministic lenses cannot be removed by semantic classification.
- `selected_lenses` is the union of baseline, deterministic, semantic, and human additions before waivers.
- A waived lens remains in `selected_lenses`, carries an exact component-7 waiver ID/version/hash and authority-matrix binding, and is absent from `execution_required_lens_ids` only while that waiver remains valid.
- Every unwaived selected lens appears in `execution_required_lens_ids`, maps to at least one `review_id`, and retains its own exit criteria even when executions are consolidated.
- `execution_required_lens_ids` cannot contain a lens absent from `selected_lenses`.
- Every reviewer execution references its assigned `review_id`; retries receive new `review_execution_id` values.
- Evidence projections obey component-2 permissions and staged disclosure.
- Any change to artifacts, selected lenses, assignments, waivers, or policy creates a new manifest version.
- `reviews-complete` is an execution state, not proof that every lens established a conclusion. Every execution-required assignment must have an immutable review record whose `status` corresponds to its authoritative `completion.result` under the component-1 review-record rules; every selected lens omitted from execution must have the exact valid manifest waiver. Each required `failed` or `not-established` result must be routed to component 4 as a canonical unresolved-review item. Every unresolved item defaults to blocking; a nonblocking item requires the component-4 progression fields and valid component-7 decision described by the lifecycle state machine.
