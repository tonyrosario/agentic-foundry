# Template: review-pipeline learning action

## Record

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
learning_action_id: "learn-..."
status: "proposed" # proposed | evaluating | shadow | canary | promoted | rejected | rolled-back | monitoring | closed
created_at: "..."
owner: "..."

evidence:
  feedback_events:
    - feedback_event_id: "fdb-..."
      feedback_event_version: "..."
      feedback_event_schema_version: "1.0"
      feedback_event_sha256: "..."
  generalized_failure_class: "..."
  recurrence_or_materiality_basis: "..."
  causal_contributors_addressed: []
  facts: []
  unknowns: []

intervention:
  target_layer: "..." # source | input-contract | deterministic-check | classifier | reviewer | adjudicator | closure | human-policy | implementation-control | evaluation-only | retirement
  target_component_id: "..."
  current_version: "..."
  candidate_version: "..."
  hypothesis: "If ..., then ..., measured by ..."
  change_summary: "..."
  why_this_layer_is_preferred: "..."
  alternatives_rejected: []
  possible_regressions: []

evaluation:
  seeded_or_historical_case_ids: []
  clean_or_boundary_case_ids: []
  suite_id_and_version: "..."
  baseline_run_id: "..."
  baseline_run_sha256: "..."
  candidate_run_id: "..."
  candidate_run_sha256: "..."
  required_segment_gates: []
  evaluation_recommendation: null
  evaluation_decision_id: null
  evaluation_decision_record_version: null
  evaluation_decision_record_schema_version: null
  evaluation_decision_record_sha256: null
  authority_matrix_id: null
  authority_matrix_version: null
  authority_matrix_schema_version: null
  authority_matrix_sha256: null

deployment:
  shadow_scope: []
  canary_scope: []
  promoted_at: null
  rollback_target: "..."
  required_monitoring: []
  expiry_or_review_event: "..."

effectiveness:
  target_metric: "..."
  baseline_value: null
  observed_value: null
  recurrence_event_ids: []
  false_positive_or_cost_effects: []
  outcome_established: false
  closure_rationale: null
  closed_at: null

integrity:
  hash_profile: "canonical-json-sha256-v1"
  learning_action_sha256: "..."
```

## Acceptance rules

- The action MUST trace to one or more exact version/hash-bound feedback events.
- The intervention MUST target a plausible causal contributor, not merely the visible symptom.
- A production behavior change MUST include both a failure case and a clean/boundary case.
- Stable objective rules SHOULD move to deterministic enforcement.
- Prompt or reviewer changes MUST pass component 6 before promotion.
- The component author MUST NOT silently edit the promoted version in place.
- Promotion MUST name a rollback target and monitoring window.
- Promotion, shadow, block, and rollback effects MUST resolve the exact candidate evaluation run plus its component-7 evaluation decision and authority-matrix tuples.
- Closure requires evidence of effect; shipping the change is not closure.
