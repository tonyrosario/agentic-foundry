# Template: evaluation suite manifest

## Purpose

Freeze the population, policy, execution matrix, and release gates used to evaluate one or more review-pipeline components. Issue a new suite version whenever cases, labels, graders, thresholds, or execution semantics change.

```yaml
schema_version: "1.0"
suite_id: "review-pipeline-suite"
suite_version: "..."
created_at: "YYYY-MM-DDThh:mm:ssZ"
owner: "..."
holdout_custodian: "..."
status: "draft" # draft | candidate | retired; active is an external registry state

scope:
  component_types:
    - classifier
    - input-contract-validator
    - reviewer
    - adjudicator
    - final-closure-gate
    - adapter
    - orchestrator
    - lifecycle-state-manager
    - release-gate
  supported_risk_tiers: [0, 1, 2, 3]
  supported_lenses: []
  lens_catalog_version: "1.0"
  known_exclusions: []

partitions:
  development:
    case_ids: []
    oracle_visibility: "authors-visible"
  regression:
    case_ids: []
    oracle_visibility: "grader-only"
  holdout:
    case_ids: []
    oracle_visibility: "custodian-and-grader-only"

coverage:
  required_case_classes:
    - clean-positive
    - seeded-omission
    - seeded-infeasibility
    - weak-oracle
    - specialist-trigger
    - ambiguous-source
    - conflicting-evidence
    - noisy-pseudodefect
    - remediation-regression
    - adapter-equivalence
    - isolation-attack
    - lineage-substitution
    - invalid-transition
    - state-stream-conflict
    - review-execution-substitution
    - inconclusive-progression-authority-substitution
    - supersession-handshake
    - post-cancellation-successor
    - rollback-reentry
    - release-gate-head-conflict
    - post-terminal-cancellation-correction
    - cancellation-obligation-loss
    - feedback-lineage-substitution
    - late-feedback-successor-loss
    - release-gate-bypass
    - inconclusive-review-escape
    - multi-source-loss
    - authority-substitution
    - decision-class-normalization-attack
    - emergency-authorization-class-mapping
    - independent-genesis-contract-binding
    - review-status-result-correspondence
    - waived-lens-visibility
    - live-historical
  minimum_segments: []
  uncovered_segments: []

execution:
  trial_policy:
    default_trials: null
    overrides: []
    report_at_least_one_success: true
    report_all_trials_success: true
  ordering: "randomized-and-recorded"
  fresh_context_required: true
  parallelism: null
  timeout_policy: "..."
  retry_policy: "infrastructure-failures-only"
  tool_policy_version: "..."
  data_retention_policy: "..."

graders:
  deterministic:
    - id: "schema-validator"
      version: "..."
    - id: "routing-invariant-validator"
      version: "..."
  semantic:
    - id: "finding-matcher"
      version: "..."
      blind_to_variant: true
  human_escalation_policy: "..."
  disagreement_policy: "..."

gates:
  zero_tolerance:
    - deterministic-mandatory-review-removed
    - missed-critical-seeded-blocker
    - fabricated-blocker-on-clean-plan
    - unauthorized-context-tool-or-mutation
    - wrong-final-artifact-approved
    - unauthorized-waiver
    - holdout-contamination
    - missing-decision-provenance
    - accepted-state-stream-fork-or-stale-head
    - accepted-unhashed-transition-trigger-or-authority
    - cancelled-with-unassigned-or-unverified-obligation
    - feedback-bound-to-wrong-decision-or-waiver-version
    - material-post-closure-feedback-without-valid-successor
    - accepted-unkeyed-parent-or-review-execution
    - closure-accepts-unkeyed-stale-or-expired-inconclusive-progression
    - supersession-without-reserved-id-terminal-genesis-order
    - post-cancellation-successor-inherits-or-loses-obligation
    - rollback-reentry-without-new-contract-or-feedback
    - authorized-orphan-release-gate-version
    - post-terminal-cancellation-revocation-rewrites-state
    - evaluation-effect-without-component-7-authority
    - accepted-adapter-renamed-or-unknown-decision-class
    - emergency-waiver-without-operational-decision-and-authority
    - independent-genesis-without-exact-frozen-input-contract
    - accepted-review-status-result-contradiction
  metric_thresholds: []
  segment_thresholds: []
  maximum_cost: null
  maximum_latency: null
  allowed_exceptions:
    - gate_or_threshold_id: "..."
      decision_id: "dec-..."
      decision_record_version: "..."
      decision_record_schema_version: "1.0"
      decision_record_sha256: "..."
      authority_matrix_id: "authority-matrix-..."
      authority_matrix_version: "..."
      authority_matrix_schema_version: "1.0"
      authority_matrix_sha256: "..."
      scope: []
      expires_at_or_event: "..."

baseline:
  component_versions: []
  evaluation_run_id: "..."
  evaluation_run_schema_version: "1.0"
  evaluation_run_sha256: "..."
  rollback_targets: []

cadence:
  scheduled_replay: "..."
  live_sample_audit: "..."
  population_review: "..."
  mandatory_event_triggers: []

integrity:
  hash_profile: "canonical-json-sha256-v1"
  manifest_sha256: "..."
  case_index_sha256: "..."
  oracle_bundle_sha256: "..."
```

## Rules

- Case IDs MUST resolve to immutable case versions.
- Holdout oracles MUST remain unavailable to component authors and evaluated agents.
- Threshold changes MUST create a new suite version; do not move the goalposts inside an active run.
- Coverage gaps MUST be visible in the release recommendation and component-7 decision.
- A candidate suite is self-hashed before authorization. A separate component-7 `evaluation-promotion-rollback` decision binds that exact suite ID/version/hash; only the registry may then mark it active. The suite never embeds the later decision hash.
- A suite MUST include clean plans and non-findings, not only seeded failures.
- Gate exceptions MUST bind the exact component-7 decision and authority matrix plus scope, rationale, expiry, and required monitoring.
