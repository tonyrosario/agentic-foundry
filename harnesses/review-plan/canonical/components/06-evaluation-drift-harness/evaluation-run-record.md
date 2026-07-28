# Template: evaluation run record

## Identity and provenance

```yaml
schema_version: "1.0"
evaluation_run_id: "..."
started_at: "..."
completed_at: "..."
owner: "..."

suite:
  id: "..."
  version: "..."
  schema_version: "1.0"
  manifest_sha256: "..."
  partitions_executed: []

case_records:
  - case_id: "..."
    case_version: "..."
    public_case_schema_version: "1.0"
    public_case_sha256: "..."
    oracle_schema_version: "1.0"
    oracle_sha256: "..."

candidate:
  component_type: "..."
  component_id: "..."
  component_version: "..."
  prompt_or_skill_hash: "..."
  policy_version: "..."
  model_provider_version: "..."
  reasoning_configuration: "..."
  adapter_version: "..."
  tool_policy_version: "..."

baseline:
  component_version: "..."
  prior_evaluation_run_id: "..."
  prior_evaluation_run_schema_version: "1.0"
  prior_evaluation_run_sha256: "..."
  rollback_target: "..."

environment:
  harness_version: "..."
  deterministic_grader_versions: []
  semantic_grader_versions: []
  runtime_versions: []
  deviations_from_suite_manifest: []
```

## Per-case results

| Case/version | Partition | Trial | Schema | Routes | Findings | Verdict | Process | Cost | Latency | Raw output/trace |
|---|---|---:|---|---|---|---|---|---:|---:|---|
| | | | | | | | | | | |

For every mismatch, record:

- oracle item;
- observed output;
- deterministic or semantic grading result;
- evidence;
- severity;
- baseline behavior;
- adjudication status;
- whether it is a candidate regression, capability gain, fixture defect, grader defect, or not established.

## Aggregate results

Report at minimum:

```yaml
results:
  counts:
    cases: 0
    trials: 0
    infrastructure_failures: 0
    invalid_fixtures: 0
  routing:
    mandatory_trigger_recall: null
    unnecessary_lens_rate: null
    underclassification_rate: null
    precedence_violations: 0
  findings:
    seeded_defect_recall: null
    confirmed_finding_precision: null
    false_block_rate: null
    evidence_validity: null
    severity_calibration: null
  adjudication_and_closure:
    disposition_accuracy: null
    finding_closure_recall: null
    remediation_regression_recall: null
    incorrect_final_approvals: 0
  reliability:
    at_least_one_trial_success: null
    all_trials_success: null
    cross_adapter_equivalence: null
    information_flow_violations: 0
  operations:
    total_cost: null
    median_latency: null
    p95_latency: null
    human_adjudication_minutes: null
```

Repeat the metric block for every required segment: risk tier, lens, case class, adapter, lifecycle stage, and domain. Mark undersized segments as `not established`; do not hide them in the aggregate.

## Baseline comparison

| Segment/metric | Baseline | Candidate | Difference | Material? | Evidence |
|---|---:|---:|---:|---|---|
| | | | | | |

List:

1. Confirmed capability gains.
2. Confirmed regressions.
3. Trade-offs requiring owner approval.
4. Unexpected behavior changes.
5. Cases requiring fixture or grader repair.
6. Results that remain not established.

## Gate evaluation

| Gate | Result | Evidence | Exception/owner/expiry |
|---|---|---|---|
| Zero-tolerance conditions | | | |
| Aggregate thresholds | | | |
| High-risk segment thresholds | | | |
| Cost and latency limits | | | |
| Holdout integrity | | | |
| Provenance completeness | | | |

Any exception credited in this table must resolve the suite manifest’s exact component-7 decision and authority-matrix tuples; owner text alone cannot satisfy a gate.

## Trace inspection

Record sampled checks for:

- required source-before-plan order;
- actual inspection of cited evidence;
- unsupported assumptions or fabricated evidence;
- exposure to prior conclusions or ambient memory;
- unauthorized tools, paths, network, or mutations;
- lucky verdicts reached through invalid reasoning;
- grader disagreement or oracle ambiguity.

## Drift assessment

- Drift signals observed:
- Affected component and segments:
- Earliest known occurrence:
- Evidence distinguishing drift from ordinary variance:
- Immediate containment:
- Required suite/case/policy changes:
- Re-baseline required: yes / no

## Release recommendation

Select exactly one:

- `PROMOTE`
- `SHADOW ONLY`
- `BLOCK`
- `ROLL BACK`
- `NOT ESTABLISHED`

Then record the harness recommendation:

```yaml
release_recommendation:
  value: "NOT ESTABLISHED" # PROMOTE | SHADOW ONLY | BLOCK | ROLL BACK | NOT ESTABLISHED
  rationale: "..."
  effective_component_version: "..."
  rollback_target: "..."
  known_limitations: []
  required_monitoring: []
  canary_scope: []
  expires_at_or_review_event: "..."
  component_8_feedback_event_refs:
    - feedback_event_id: "fdb-..."
      feedback_event_version: "..."
      feedback_event_schema_version: "1.0"
      feedback_event_sha256: "..."
```

The recommendation applies only to the exact candidate, suite, policy, model/runtime, adapter, and tool versions recorded above. It has no deployment effect by itself.

After the run is complete and self-hashed, component 7 issues a separate `evaluation-promotion-rollback` decision whose evaluation-authorization block binds the evaluation-run ID/hash, candidate component/version, selected effect, and authority-matrix tuple. No registry, orchestrator, or learning action may enact `PROMOTE`, `SHADOW ONLY`, `BLOCK`, or `ROLL BACK` until that separate decision validates. This ordered run-then-decision handoff avoids circular self-hashes. `NOT ESTABLISHED` is the fail-closed absence of an authorized effect, not an implicit promotion.

## Integrity

The complete machine-readable evaluation run record, including per-case results, aggregate results, gate evaluation, trace inspection, drift assessment, and release recommendation, ends with:

```yaml
integrity:
  hash_profile: "canonical-json-sha256-v1"
  evaluation_run_record_sha256: "..."
```
