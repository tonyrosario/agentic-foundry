# Template: canonical finding and remediation ledger

## Purpose

Provide the authoritative mapping from immutable raw reviewer findings to adjudicated dispositions, remediation, human decisions, waivers, and re-review obligations.

## Ledger

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
ledger_id: "ledger-..."
ledger_version: "..."
input_contract_id: "review-input-..."
classification_id: "class-..."
review_manifest_id: "manifest-..."
policy_version: "..."
lens_catalog_version: "1.0"
status: "adjudicating" # adjudicating | remediation-required | ready-for-final-review | blocked | superseded
created_at: "..."
updated_at: "..."

parent_records:
  - record_type: "review-input-contract"
    record_id: "review-input-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: "adjudication-input"
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
    role: "governing-review-set"

artifacts:
  authoritative_source_bundle:
    id: "..."
    schema_version: "1.0"
    version: "..."
    path: "..."
    sha256: "..."
  reviewed_plan:
    id: "..."
    path: "..."
    sha256: "..."
  evidence_manifest_sha256: "..."

inputs:
  raw_review_executions:
    - review_id: "rev-..."
      review_execution_id: "revexec-..."
      schema_version: "1.0"
      logical_record_version: null
      review_record_sha256: "..."
      result: "established" # established | not-established | failed
  raw_findings:
    - finding_id: "find-..."
      finding_schema_version: "1.0"
      finding_sha256: "..."
      source_review_id: "rev-..."
      source_review_execution_id: "revexec-..."
  adjudicator_identity_and_version: "..."
  adjudication_trace_reference: null

findings:
  - ledger_finding_id: "lf-..."
    source_finding_ids: []
    source_review_ids: []
    source_finding_refs:
      - finding_id: "find-..."
        finding_schema_version: "1.0"
        finding_sha256: "..."
        source_review_id: "rev-..."
        source_review_execution_id: "revexec-..."
    disposition: "confirmed" # confirmed | rejected | duplicate | needs-human-decision | not-established
    finding_type: "source-requirement-defect" # source-requirement-defect | residual-risk | plan-quality-defect | evidence-gap | policy-or-authority-decision
    severity: "major"
    source_requirement_or_invariant: "..."
    source_locations:
      - source_bundle_id: "source-bundle-..."
        source_artifact_id: "..."
        artifact_local_location: "..."
    plan_locations: []
    triggering_scenarios: []
    evidence: []
    adjudication_rationale: "..."
    duplicate_of_ledger_finding_id: null
    required_action_or_decision: "..."
    owner: "..."
    unresolved:
      materiality: "high" # low | moderate | high | critical
      blocks_progression: true
      progression_basis: null
      progression_decision_id: null
      progression_owner: null
      expires_at_or_event: null
      required_rereview_lenses: []
    remediation:
      state: "pending" # not-applicable | pending | implemented | verified | failed | superseded
      candidate_plan_sha256: null
      resolution_evidence: []
      decision_records:
        - decision_id: "..."
          decision_record_version: "..."
          decision_record_schema_version: "1.0"
          decision_record_sha256: "..."
      waiver_records:
        - waiver_id: "..."
          waiver_record_version: "..."
          waiver_record_schema_version: "1.0"
          waiver_record_sha256: "..."
      re_review_lenses: []
      re_review_ids: []
      verified_by: null
      verified_at: null

unresolved_review_executions:
  - ledger_unresolved_review_id: "lur-..."
    review_id: "rev-..."
    review_execution_id: "revexec-..."
    review_record_schema_version: "1.0"
    review_record_sha256: "..."
    required_lens_ids: []
    execution_result: "not-established" # not-established | failed
    reason: "..."
    missing_evidence_or_capability: []
    materiality: "high" # low | moderate | high | critical
    blocks_progression: true
    progression_basis: null
    progression_decision_id: null
    progression_decision_record_version: null
    progression_decision_record_schema_version: null
    progression_decision_record_sha256: null
    progression_owner: null
    expires_at_or_event: null
    required_rereview_lens_ids: []
    replacement_review_ids: []
    resolution_evidence: []

human_decisions_required: []
required_final_review_lenses: []

integrity:
  hash_profile: "canonical-json-sha256-v1"
  ledger_sha256: "..."
  supersedes_ledger_id: null
  supersedes_ledger_sha256: null
```

## Authority and immutability

- Top-level parent IDs and `source_*_ids` arrays are non-authoritative indexes. Parent records, raw review executions, and source findings are credited only through their keyed ID/version/hash tuples.
- Raw review records are immutable observations and never carry canonical dispositions.
- This ledger is the sole authority for disposition and remediation state.
- Every raw `finding_id` must map to exactly one canonical ledger finding, including rejected and duplicate findings.
- Every required review execution whose result is `not-established` or `failed` must map to exactly one `unresolved_review_executions` item, even if no raw finding exists.
- One ledger finding may map several duplicates, but each distinct triggering mechanism must remain visible.
- Changes create a new `ledger_version`; preserve the prior version and hash.
- Only the assigned adjudicator may set initial dispositions. Human decision owners may resolve `needs-human-decision` through component 7 records. Final reviewers verify remediation but do not rewrite adjudication history.

## Remediation and closure rules

- `source-requirement-defect`: close only when the requirement is met or the authoritative source contract is explicitly changed, versioned, reclassified, and re-reviewed. A waiver or deferral cannot mark it complete.
- `residual-risk`: may remain in an approved plan only with a valid, scoped component-7 risk acceptance and satisfied conditions.
- `plan-quality-defect`: requires a plan revision and affected-lens verification.
- `evidence-gap`: requires evidence or remains `not-established`; unknown high-impact facts block closure.
- `policy-or-authority-decision`: requires a valid component-7 decision record.

Every `not-established`, failed review execution, or otherwise unresolved item defaults to `blocks_progression: true`. It may be nonblocking only when it is not an unmet source criterion, policy gate, or high/critical-impact unknown and all of these fields are present: `materiality`, evidence-backed `progression_basis`, authorized component-7 progression-decision ID/version/hash, named owner, expiry/review event, and required re-review lenses. Silence, missing fields, or a reviewer recommendation cannot authorize progression.

Set ledger status to `ready-for-final-review` only when every confirmed finding has the required remediation or valid decision evidence, every required review execution is represented, every required re-review has completed, and every unresolved finding or review execution either has been resolved by a replacement review or has a currently valid nonblocking progression decision. Component 5 independently verifies this claim.
