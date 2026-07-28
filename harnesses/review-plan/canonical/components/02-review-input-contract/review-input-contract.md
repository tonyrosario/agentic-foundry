# Template: review input contract

## Purpose

Use this contract to freeze exactly what a plan-review run is authorized to inspect, decide, and produce. It prevents accidental context leakage, ambiguous artifact versions, silent omissions, and reviewers reaching different conclusions because they received different source material.

Create one contract for each review run. The orchestrator may derive role-specific projections from it, but must preserve the same artifact identities and policy decisions.

Normative terms in this template use their ordinary meanings:

- **MUST**: required for a valid review run.
- **SHOULD**: expected unless the contract records a reason to differ.
- **MAY**: optional.

## Contract guarantees

A valid contract establishes:

1. The authoritative source of intent.
2. The exact plan version under review.
3. How inherited and delta documents combine.
4. The repository and external-evidence snapshots, if any.
5. What is deliberately included and excluded.
6. What each reviewer may see and when it may see it.
7. The reviewer’s decision authority and required escalation behavior.
8. The lifecycle state: initial review, adjudication, revision, or final re-review.
9. Enough provenance to reproduce or audit the run later.

The contract describes inputs and authority. It does not instruct a reviewer what verdict to reach.

## Machine-readable template

Fill this manifest before dispatch. Use paths relative to a declared workspace root where practical. Use immutable content hashes and repository revisions for material reviews.

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
input_contract_id: "review-input-..."
created_at: "YYYY-MM-DDThh:mm:ssZ"
created_by: "human-or-system-identity"

run:
  mode: "plan-time" # plan-time | diff-time | adjudication | final-rereview | implementation-conformance | release
  materiality: "material" # trivial | material
  requested_decision: "Does the plan achieve the source contract?"
  human_owner: "..."
  policy_version: "..."
  lens_catalog_version: "1.0"

workspace:
  root_id: "logical-workspace-name"
  repository_revision: "full-commit-sha-or-null"
  dirty_state_allowed: false
  dirty_state_manifest: []

artifacts:
  authoritative_source_bundle:
    id: "source-bundle-..."
    schema_version: "1.0"
    version: "..."
    path: "path/to/source-bundle.yaml"
    sha256: "..."
  plan:
    id: "candidate-plan"
    path: "path/to/plan.md"
    sha256: "..."
    version: "v1"
    read_order: 2
  inheritance:
    resolution_rule: "later delta overrides only explicitly named sections"
    documents: []
    effective_plan_artifact: null
  implementation_diff:
    base_revision: null
    head_revision: null
    changed_paths_manifest: null
  parent_delivery:
    approved_plan_sha256: null
    final_closure_record_id: null
    final_closure_record_schema_version: null
    final_closure_record_sha256: null
    implementation_revision: null
    release_gate_record_id: null
    release_gate_record_version: null
    release_gate_record_schema_version: null
    release_gate_record_sha256: null
    rollout_configuration_sha256: null
  prior_plan:
    path: null
    sha256: null
  finding_ledger:
    path: null
    sha256: null

scope:
  declared_surfaces: []
  explicit_non_goals: []
  constraints: []
  assumptions: []
  unknowns: []
  excluded_context:
    - item: "..."
      reason: "..."
      authorized_by: "..."

evidence:
  repository_access: "none" # none | declared-paths-read-only | repository-read-only
  allowed_paths: []
  denied_paths: []
  authoritative_documents: []
  external_sources:
    - url: "..."
      retrieved_at: "..."
      content_hash_or_snapshot: "..."
  executable_evidence: []
  supplied_evidence_bundle: []

reviewer_authority:
  assigned_lens_ids: []
  may_add_findings_outside_lens: false
  may_propose_alternative_architecture: false
  may_modify_artifacts: false
  allowed_tools: []
  prohibited_tools: []
  allowed_verdicts: []
  abstain_when: []
  escalate_when: []

information_flow:
  context_mode: "fresh" # fresh | inherited | forked
  required_read_order:
    - "authoritative_source_bundle"
    - "independent_criteria"
    - "plan"
  repository_guidance_loaded: []
  ambient_memory_allowed: false
  prior_reviews_visible: false
  drafter_rationale_visible: false
  staged_disclosures: []

lifecycle:
  stage: "plan-time-review"
  origin_kind: "independent" # independent | terminal-feedback-remediation | superseding-outcome | post-cancellation-successor
  parent_lifecycle_id: null
  parent_terminal_state_record_id: null
  parent_terminal_state_record_schema_version: null
  parent_terminal_state_record_sha256: null
  initiating_feedback_event_id: null
  initiating_feedback_event_version: null
  initiating_feedback_event_schema_version: null
  initiating_feedback_event_sha256: null
  initiating_decision_id: null
  initiating_decision_record_version: null
  initiating_decision_record_schema_version: null
  initiating_decision_record_sha256: null
  parent_cancellation_record_id: null
  parent_cancellation_record_version: null
  parent_cancellation_record_schema_version: null
  parent_cancellation_record_sha256: null
  reserved_classification_id: null
  reserved_review_manifest_id: null
  previous_review_executions:
    - review_id: "rev-..."
      review_execution_id: "revexec-..."
      review_record_schema_version: "1.0"
      review_record_sha256: "..."
  supersedes_contract_id: null
  supersedes_contract_schema_version: null
  supersedes_contract_sha256: null
  revision_summary: null
  accepted_finding_ids: []
  waived_finding_ids: []
  required_rereview_lenses: []

output:
  finding_schema_version: "..."
  required_sections: []
  output_path: "..."
  preserve_raw_trace: false
  redact_fields: []

attestation:
  artifacts_resolved: false
  hashes_verified: false
  exclusions_acknowledged: false
  authority_acknowledged: false

integrity:
  hash_profile: "canonical-json-sha256-v1"
  input_contract_sha256: "..."
```

Use `null` for a field that does not apply. Use an entry in `unknowns` when a fact matters but has not been established. Do not use an empty value to hide uncertainty.

`reserved_classification_id` and `reserved_review_manifest_id` are optional collision-resistant output reservations, not parent records and not evidence that either downstream record exists. The later classification and manifest must independently hash-bind this completed contract.

## Artifact rules

### Terminal-feedback remediation

For the first contract of a lifecycle created from material post-closure feedback:

- set `origin_kind: terminal-feedback-remediation` and bind the exact parent `closed` state and initiating feedback-event IDs/hashes;
- fill `artifacts.parent_delivery` with the parent’s approved-plan hash, final-closure ID/hash, implicated implementation revision, release-gate ID/hash, and rollout configuration;
- identify the new remediation plan as the candidate plan and disclose whether it changes source intent, implementation, controls, or operations;
- use a fresh classification under current policy and inherit no approval, decision, waiver, review, or release authority from the parent lifecycle;
- require a superseding parent feedback-event version, created after this contract and genesis are sealed, to acknowledge their IDs and hashes without changing the initiating event version/hash bound here.

For `superseding-outcome`, bind the exact parent `superseded` state and initiating specification decision plus the reserved lifecycle ID. For `post-cancellation-successor`, bind the exact parent `cancelled` state, initiating decision, and current cancellation-record version/hash. These successor contracts inherit no parent approval or obligation discharge.

### Authoritative source bundle

- Create and hash [an authoritative source bundle](authoritative-source-bundle.md) containing every ticket, PRD, acceptance criterion, ADR, policy, approved decision, supporting source, and disputed source relevant to the outcome.
- Mark conflicts as `disputed`; do not silently choose the convenient artifact.
- Preserve bundle read order. A cold outcome reviewer MUST form success criteria from the complete bundle before reading the plan.
- Supporting context MUST NOT be mislabeled as authoritative intent.
- Every downstream record MUST bind the bundle ID, version, and hash; one artifact from the bundle cannot stand in for the whole source set.

### Candidate plan

- Identify one exact candidate plan by path, version, and hash.
- A mutable filename alone is insufficient for a material review.
- If the plan is a delta, identify every inherited document and the precedence rule.
- When feasible, include a generated effective-plan artifact while retaining the constituent documents for auditability.
- If inheritance is ambiguous, classification or review MUST return `not established` rather than inventing resolution semantics.

### Repository and implementation state

- Pin repository-grounded reviews to a commit SHA or record the complete dirty-state manifest.
- Do not describe a moving branch name as a reproducible snapshot.
- For diff-time review, declare both base and head revisions plus the observed changed-path manifest.
- Declared change surfaces and observed change surfaces are separate fields; their mismatch is review evidence.

### External evidence

- Record retrieval time and a stable snapshot or content hash when an external fact can change.
- Label vendor documentation, standards, policy, experiments, and informal commentary according to their authority.
- If live external access is prohibited, state that explicitly rather than letting a reviewer assume current facts were verified.

## Scope and uncertainty rules

- Record constraints separately from non-goals. A constraint limits acceptable solutions; a non-goal excludes an outcome.
- Record assumptions as claims the plan relies upon and unknowns as facts still requiring evidence or a decision.
- Every explicit exclusion needs a reason and authorizer.
- Missing high-impact evidence MUST trigger escalation or `not established`; it MUST NOT reduce the risk tier.
- Repository access does not authorize unrestricted context. Limit evidence to what the role needs.

## Authority and permission rules

Each reviewer receives a bounded decision:

- An outcome auditor judges requirement coverage and outcome sufficiency, not implementation style.
- A grounded reviewer verifies feasibility and testability against authorized evidence.
- A specialist judges only its risk lens unless the contract permits adjacent findings.
- An adjudicator validates findings and dispositions but does not rewrite the plan unless separately authorized.
- A final reviewer may approve only the exact final-plan hash in its contract.

All plan reviews SHOULD be read-only. Network access, command execution, repository scope, and mutation authority MUST be explicit. Absence of a permission means it is not granted.

## Role-specific projections

The orchestrator SHOULD generate the smallest input projection that preserves each role’s evidence needs.

| Role | Initially receives | Initially withheld |
|---|---|---|
| Classifier | Source contract, plan, declared/observed surfaces, policy | Drafter self-assessment and reviewer conclusions |
| Cold outcome auditor | Source contract, then plan and declared dependencies | Prior reviews, drafter rationale, unrelated repository context |
| Grounded reviewer | Source contract, plan, pinned repository/docs/tests | Other reviewers’ conclusions until its own findings are recorded |
| Specialist | Relevant source criteria, plan sections, and domain evidence | Unrelated review noise and unnecessary sensitive context |
| Adjudicator | Source contract and plan first; findings only after independent assessment | Reviewer popularity, vote totals, or author assurances as evidence |
| Final reviewer | Final plan, source contract, adjudicated ledger, current evidence, prior-plan diff | Any assertion that approval of the earlier plan carries forward |

Withholding is staged, not destructive: the run record should retain the complete contract while each agent receives only its authorized projection.

## Mode-specific requirements

### Plan-time

Require the source contract, exact plan, inheritance rules, scope declaration, access policy, classifier decision, and review manifest.

### Diff-time

Additionally require the approved plan, implementation base/head revisions, actual changed surfaces, plan deviations, and current executable evidence. The classifier may raise risk or add reviews based on undeclared implementation changes.

### Adjudication

Require the source contract, reviewed plan hash, raw review outputs, evidence attachments, and finding-schema versions. Enforce staged read order so the adjudicator forms an independent view before seeing conclusions.

### Final re-review

Require the previous and final plan hashes, canonical finding ledger, revision summary, changed-surface manifest, waivers, and current evidence. Approval applies only to the final hash.

## Validation policy

### Reject dispatch

Do not start the review when:

- the source contract or plan cannot be resolved;
- hashes do not match supplied artifacts;
- delta inheritance has no unambiguous resolution rule;
- no human owner or requested decision is identified for a material review;
- the reviewer’s artifact-mutation or tool authority is ambiguous;
- a required artifact is replaced by an unversioned summary;
- information-flow requirements cannot be enforced but independence is mandatory.

### Dispatch with `not established` capability

A review may proceed while explicitly recording uncertainty when:

- optional repository or external evidence is unavailable;
- an assumption is known but unresolved;
- a supporting artifact is missing without making the core source or plan ambiguous;
- a runtime cannot guarantee perfect isolation and the limitation is recorded.

The reviewer must be allowed to report `not established` and identify the evidence needed to resolve it.

## Assembly procedure

1. Resolve and hash the source contract before collecting the plan.
2. Resolve the plan, inherited documents, and precedence rules.
3. Pin repository and external evidence snapshots.
4. Record scope, constraints, exclusions, assumptions, and unknowns.
5. Attach the classifier result and selected review manifest.
6. Set role-specific authority, tools, permissions, and disclosure order.
7. Validate required fields and artifact integrity.
8. Freeze the contract and give it a unique ID.
9. Generate role-specific projections without changing artifact identities.
10. Store the completed contract ID in every review record and finding ledger.

## Contract lineage

Use one immutable input contract per material lifecycle stage. Plan-time review, adjudication, final re-review, diff-time review, conformance, and release each receive a contract that pins their exact artifacts, permissions, and requested decision.

- For an independent lifecycle, reserve the unused `lifecycle_id`, freeze its first input contract under that ID, and only then compare-and-create the genesis `draft` state record bound to the contract's exact ID/hash. The `input-frozen` transition revalidates this existing binding.
- Contracts pursuing the same authoritative outcome keep the same `lifecycle_id`.
- A later stage or material revision receives a new `input_contract_id` and records the superseded contract’s exact ID/schema/hash.
- Never edit a frozen contract in place or allow approval from a superseded contract to carry forward.
- If an authorized source decision replaces the outcome rather than clarifying it, create a new lifecycle and link it as the parent/successor according to [the record-lineage rules](../03-review-run-orchestrator/record-lineage-and-integrity.md).
- Every downstream record must repeat the lifecycle and contract IDs and verify repeated artifact hashes.

## Acceptance checklist

- [ ] The originating intent is represented by authoritative, versioned artifacts.
- [ ] The exact plan and all inherited/delta documents are identifiable and hashable.
- [ ] Precedence among plan documents is explicit.
- [ ] Repository and external evidence are pinned or their absence is declared.
- [ ] Scope, non-goals, constraints, assumptions, unknowns, and exclusions are distinct.
- [ ] Review authority, allowed tools, and mutation permissions are explicit.
- [ ] Cold reviewers cannot see prior conclusions before recording independent criteria.
- [ ] Role projections preserve necessary evidence without leaking unrelated context.
- [ ] Missing high-impact facts cause escalation or `not established`.
- [ ] Diff-time and final-review contracts identify both previous and current artifacts.
- [ ] Every output can be traced to the contract, artifact hashes, policy, prompt/skill version, model, and tool policy.
- [ ] A human owner is accountable for unresolved specification and risk decisions.
