# Template: common finding record

## Purpose

Represent one raw reviewer finding in a stable, evidence-bearing schema. The finding states a falsifiable defect or unresolved risk; it does not carry adjudication authority.

```yaml
finding_schema_version: "1.0"
lifecycle_id: "life-..."
finding_id: "find-..."
source_review_id: "rev-..."
source_review_execution_id: "revexec-..."
review_lens_id: "..."
lens_catalog_version: "1.0"

classification:
  severity: "major" # blocker | major | moderate | minor
  confidence: "..."
  proposed_disposition: "fix" # fix | clarify | accept-risk | defer | reject-finding

claim:
  summary: "..."
  source_requirement_or_invariant: "..."
  source_location:
    source_bundle_id: "source-bundle-..."
    source_artifact_id: "..."
    artifact_local_location: "..."
  plan_location: "..."
  triggering_scenario: "..."
  expected_outcome: "..."
  plan_outcome: "..."
  impact: "..."

evidence:
  - kind: "source-contract" # source-contract | plan | repository | executable | external | inference
    reference: "..."
    artifact_sha256: null
    excerpt_or_observation: "..."
    supports: "..."

uncertainty:
  facts: []
  inferences: []
  unknowns: []
  evidence_needed: []

scope:
  authorized_by_lens: true
  affected_surfaces: []
  affected_requirements: []

integrity:
  hash_profile: "canonical-json-sha256-v1"
  finding_sha256: "..."
```

## Rules

- `source_review_id` and `source_review_execution_id` bind the reserved composite execution identity, not the final review-record hash.
- Seal the finding first, then include its ID/schema/hash in the immutable review record for that same composite execution identity. This one-way ownership order avoids a circular self-hash.
- A finding is attributable to an execution only when the accepted review record lists the exact finding tuple; matching IDs without that review-owned hash are insufficient.
- One finding describes one materially distinct failure mechanism.
- Evidence must support the claim, not merely mention the same topic.
- A preference for another architecture is not a finding unless the written plan cannot meet an authorized requirement or risk threshold.
- Confidence does not replace evidence and may be `not established`.
- Raw findings are immutable after review completion. Component 4 maps one or more raw `finding_id` values to a canonical `ledger_finding_id` and owns all subsequent disposition state.
