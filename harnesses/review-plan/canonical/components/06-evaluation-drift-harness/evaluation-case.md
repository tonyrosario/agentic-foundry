# Template: evaluation case

## Purpose

Define one reproducible pipeline scenario with a public execution envelope and a sealed grading oracle. Store them separately in actual use so the agent cannot infer the expected answer.

## Public execution envelope

This section may be supplied to the harness and evaluated component.

```yaml
schema_version: "1.0"
case_id: "..."
case_version: "..."
case_class: "..."
title: "..."
status: "active" # draft | active | retired
origin: "synthetic" # synthetic | historical | escaped-defect | false-positive | red-team
owner: "..."
lens_catalog_version: "1.0"

target:
  component_types: []
  lifecycle_stage: "plan-time"
  risk_tier_claimed: null
  review_lens_ids: []

input:
  review_input_contract_id: "review-input-..."
  review_input_contract_schema_version: "1.0"
  review_input_contract_path: "..."
  review_input_contract_sha256: "..."
  artifact_bundle_path: "..."
  artifact_bundle_sha256: "..."
  allowed_runtime_adapters: []

execution:
  required_context_mode: "fresh"
  required_tools: []
  prohibited_tools: []
  trial_override: null
  timeout_override: null

public_notes: []

integrity:
  hash_profile: "canonical-json-sha256-v1"
  public_case_sha256: "..."
```

## Sealed oracle

This section is available only to authorized graders and holdout custodians.

```yaml
schema_version: "1.0"
case_id: "..."
case_version: "..."
lens_catalog_version: "1.0"

oracle:
  authoritative_interpretation: "..."
  expected_risk_tier:
    exact: null
    acceptable: []
  required_routes:
    - lens_id: "..."
      trigger: "..."
      evidence: []
  forbidden_route_removals: []
  acceptable_additional_routes: []

  required_findings:
    - oracle_id: "..."
      severity: "..."
      requirement_or_invariant: "..."
      triggering_scenario: "..."
      supporting_evidence: []
      acceptable_formulations: []
      required_lens_ids: []
  forbidden_findings:
    - claim: "..."
      rejection_reason: "..."
  optional_useful_observations: []

  allowed_verdicts: []
  required_abstentions_or_escalations: []
  prohibited_assumptions: []
  required_human_gates: []
  required_rereview_triggers: []

  process_expectations:
    required_read_order: []
    required_evidence_actions: []
    prohibited_information_flows: []
    prohibited_actions: []

  mutation:
    seeded: false
    source_artifact: null
    mutation_description: null
    expected_detection_surface: []

grading:
  deterministic_checks: []
  semantic_match_rules: []
  severity_tolerance: "..."
  partial_credit_policy: "..."
  automatic_failure_conditions: []
  expert_domains_required: []
  adjudication_notes: "..."

integrity:
  hash_profile: "canonical-json-sha256-v1"
  oracle_sha256: "..."
  labeled_by: []
  independently_verified_by: []
  last_calibrated_at: "..."
```

## Case authoring rules

0. Bind the public input contract by ID, schema version, and self-hash; path alone is non-authoritative.
1. Start from a concrete failure or capability claim, not a vague desire for skepticism.
2. Include the smallest artifact set that preserves the real decision.
3. Make the source authority and expected interpretation explicit.
4. Define material non-findings so verbosity is not rewarded as rigor.
5. Accept semantically equivalent findings; do not require one exact wording.
6. Record the evidence that makes each expected finding true.
7. Include clean controls for every major failure class.
8. For mutations, preserve an unmutated counterpart when feasible.
9. Double-label consequential or ambiguous cases.
10. Retire cases whose correct answer changes with policy or repository drift unless they are re-versioned.

## Case acceptance checklist

- [ ] Public inputs contain no oracle or answer leakage.
- [ ] The component-2 input contract resolves and validates.
- [ ] Artifact hashes are immutable and reproducible.
- [ ] Expected findings are material, evidence-backed, and scoped.
- [ ] Acceptable alternative formulations are documented.
- [ ] Non-findings and forbidden assumptions are documented.
- [ ] Process expectations can be observed or are marked non-scoring.
- [ ] The case has an owner and calibration history.
- [ ] At least one independent labeler verified high-consequence oracles.
