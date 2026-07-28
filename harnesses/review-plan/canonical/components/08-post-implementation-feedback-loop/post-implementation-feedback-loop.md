# Post-implementation feedback loop

## Purpose

Use this component to learn whether the review pipeline predicted and controlled the failures that mattered after a plan was approved. It compares the source contract, approved plan, actual implementation, rollout, and observed outcomes; then routes evidence-backed improvements back through evaluation.

This component is not an incident tracker or a generic retrospective. It links operational and implementation evidence to the exact classifier, reviewer, adjudicator, waiver, and final-closure versions that influenced the decision.

## Pipeline contract

```text
approved source + final plan + finding/decision/waiver ledgers
                         ↓
actual implementation diff and plan deviations
                         ↓
diff-time classification + conformance review
                         ↓
release and outcome observation windows
                         ↓
feedback events: escape | false positive | near miss | control result | success
                         ↓
causal attribution and preventability analysis
                         ↓
learning action proposal
                         ↓
component 6 evaluation and promotion gates
                         ↓
versioned classifier/reviewer/policy/tool change
```

### Required inputs

- The final [review input contract](../02-review-input-contract/review-input-contract.md).
- Authoritative source-contract and approved-plan hashes.
- Classifier decision and complete review manifest.
- Raw review records and canonical finding/remediation ledger.
- Final-closure record and approval decision.
- Human decisions, active waivers, and authority records from [component 7](../07-human-escalation-waiver-policy/human-escalation-and-waiver-policy.md).
- For a cancelled lifecycle, the exact active [cancellation record](../07-human-escalation-waiver-policy/cancellation-obligation-record.md) and all residual-obligation destinations and evidence.
- Actual base/head revisions, changed-surface manifest, and declared plan deviations.
- Test, deployment, monitoring, incident, customer, and operator evidence authorized by policy.

### Required outputs

- A [post-implementation conformance review](post-implementation-conformance-review.md).
- Versioned [feedback event records](feedback-event-record.md).
- For material feedback discovered after lifecycle closure, one ordered successor-lifecycle handoff consisting of the sealed initiating event, new genesis state and input contract, and superseding event acknowledgment.
- Evidence-based causal and preventability classifications.
- One or more [learning action records](learning-action-record.md).
- New or updated evaluation cases for component 6 when warranted.
- Closure evidence showing whether the action worked and whether the failure recurred.

## Feedback event classes

| Event | Meaning |
|---|---|
| Review escape | A material plan defect existed in authorized evidence but required review stages did not surface or preserve it |
| Routing escape | A required lens or human gate was not selected |
| Evidence escape | Necessary evidence was absent, stale, inaccessible, or incorrectly treated as established |
| Adjudication escape | A valid finding was rejected, weakened, merged incorrectly, or assigned no effective action |
| Revision escape | A confirmed finding was not correctly folded into the plan or the fix introduced a new defect |
| Closure escape | Final approval was granted despite an unresolved condition, invalid waiver, or mismatched artifact |
| Human-decision failure | An authorized decision used incomplete evidence, exceeded scope, or accepted risk whose assumptions failed |
| Cancellation-obligation failure | A residual obligation was lost, overdue, falsely marked fulfilled, or transferred to an unavailable or mismatched destination |
| Implementation deviation | Actual changes materially departed from the approved plan without reclassification and approval |
| Reviewer false positive | A material finding was later established to be unsupported, immaterial, or outside authorized scope |
| Near miss | A failure path was activated or narrowly avoided without material loss |
| Control result | A test, rollout guard, monitoring signal, rollback, or compensating control succeeded or failed |
| Validated success | The plan and controls produced the intended outcome under the defined observation window |

Do not label every implementation bug a review escape. Establish what evidence existed at review time, which role was authorized to inspect it, and whether a reasonable execution of that role could have detected the issue.

## Observation stages

Collect evidence at several stages because different failures become visible at different times.

| Stage | Minimum questions |
|---|---|
| Before merge/implementation completion | Did actual code, schema, infrastructure, permissions, and tests match the plan? |
| Pre-release | Were planned gates, rehearsal, compatibility, rollback, and ownership present? |
| Rollout | Did monitoring and stop/rollback conditions behave as planned? |
| Stabilization window | Did intended user/system outcomes occur without hidden degradation? |
| Long-tail review | Did delayed consistency, cost, retention, adoption, or operational effects emerge? |
| Incident/escape trigger | Which planning/review/control opportunity could have prevented or reduced impact? |

The plan or release policy should define observation windows and success signals. If no meaningful outcome can yet be observed, record `not established` rather than declaring validated success.

## Workflow

### 1. Freeze implementation evidence

Record exact implementation base/head revisions, changed files, dependency changes, migrations, permissions, infrastructure, tests, rollout configuration, and plan deviations. Hash or snapshot mutable operational evidence where policy permits.

### 2. Run diff-time classification

Compare declared plan surfaces with observed implementation surfaces. The classifier may raise risk, add lenses, require evidence, or invoke a human gate. A new high-risk surface cannot inherit approval merely because the original plan was approved.

### 3. Perform conformance review

Use the [conformance template](post-implementation-conformance-review.md) to determine:

- whether every required outcome is represented in the implementation;
- whether the implementation follows the approved plan’s material commitments;
- whether deviations were explicitly approved and re-reviewed;
- whether verification distinguishes success from plausible failure;
- whether rollout, monitoring, ownership, and recovery controls exist;
- whether active human decisions and waivers still match scope and assumptions.

Conformance is not code review. It judges the agreement among intent, plan, implementation, controls, and observed outcome. Trigger code/security/data/operations review separately when the classifier selects them.

### 3a. Enforce the release gate

Create a [release-gate record](release-gate-record.md) after conformance. Material deviations, new risk lenses, or high-impact unknowns block release until diff-time reviews and adjudication complete. Conformance then moves the gate only to `awaiting-authority`; component 7’s verified release authority must authorize the exact implementation revision and rollout configuration. Any later material change revokes that authorization and returns to diff-time classification.

### 4. Observe outcomes

Capture expected and unexpected signals over the configured windows. Include successes and control activations, not only incidents. Preserve facts, inferences, and unknowns separately.

### 5. Create feedback events

Create one record per materially distinct mechanism. Link related events without merging away different causes. Record the earliest stage at which each event could have been prevented, detected, contained, or recovered.

For a cancelled lifecycle, monitor every residual obligation through its due event. Open a feedback event when an obligation becomes overdue, its destination cannot be resolved or fails integrity validation, fulfillment evidence is insufficient, or a supposedly absent obligation is later established. Bind the event to the exact cancellation-record version and obligation IDs.

Every event references the exact versions and self-hashes of the decisions, waivers, closure, conformance review, and release gate that governed the implicated delivery. Never resolve an ID to its latest version. Later decision or waiver versions may be recorded only as comparison evidence and cannot replace the historical governing records.

### 5a. Route material feedback discovered after closure

Do not reopen or mutate a `closed` lifecycle. When current policy classifies a post-closure event as requiring corrective implementation, containment follow-up, source/plan revision, or replacement release:

1. Seal an initiating feedback-event version with material evidence, `response_lifecycle.state: required-pending`, and null successor fields.
2. Have the policy-designated accountable owner or incident/release authority initiate one successor lifecycle.
3. Create its `draft` genesis state and first component-2 contract, binding the parent `closed` state and sealed feedback-event version/hash plus the exact original source, plan, implementation, closure, and release records.
4. Atomically append a superseding feedback-event version with `response_lifecycle.state: acknowledged` and the successor lifecycle, genesis-state hash, and input-contract hash. Compare-and-swap against the initiating event head ensures only one successor is recognized; unacknowledged candidates are invalid and cannot dispatch.
5. Run fresh classification and the normal lifecycle. Parent approvals, reviews, decisions, waivers, and release authority do not carry forward.

Nonmaterial observations remain attached to the closed lifecycle. Emergency containment may proceed under component 7’s bounded authorization, but its decision and execution evidence must be linked into the successor contract.

### 6. Classify causal contribution

Use the taxonomy below. Multiple contributing stages may be true. Avoid assigning one convenient root cause when the failure crossed several controls.

### 7. Decide learning actions

Select the smallest reliable intervention:

- no pipeline change; the event was outside authorized review scope;
- improve source/specification quality;
- strengthen the input contract or evidence bundle;
- add or repair a deterministic rule, schema, test, or linter;
- change classifier routing or risk policy;
- change a reviewer rubric, prompt, or reference;
- change adjudication, remediation, or closure handling;
- change human authority, waiver, or escalation policy;
- improve implementation/release controls;
- add an evaluation case without changing production behavior yet;
- retire or consolidate a low-value reviewer.

Do not add a prompt rule for every event. The proposed action must identify the generalized failure class and a clean counterexample protecting against overcorrection.

### 8. Evaluate before promotion

Send proposed prompt, skill, policy, tool, schema, or adapter changes to the [evaluation and drift harness](../06-evaluation-drift-harness/evaluation-and-drift-harness.md). Require a baseline comparison, relevant regression and holdout cases, trace inspection, shadow/canary where material, a release recommendation, and a separate component-7 authorization bound to the completed run hash.

### 9. Verify and close

After promotion, monitor whether the targeted failure recurs, whether false positives increase, and whether cost or latency became unacceptable. Close the learning action only with outcome evidence. Preserve the original event and rejected alternatives.

## Causal taxonomy

Record all material contributors:

- `source_contract_missing_or_ambiguous`
- `plan_omission_or_contradiction`
- `input_contract_or_context_failure`
- `classifier_routing_failure`
- `reviewer_capability_failure`
- `reviewer_instruction_or_rubric_failure`
- `repository_or_external_evidence_failure`
- `tool_or_permission_failure`
- `information_flow_or_context_leakage`
- `adjudication_failure`
- `remediation_or_revision_failure`
- `final_closure_failure`
- `human_authority_or_decision_failure`
- `waiver_assumption_or_control_failure`
- `implementation_deviation`
- `implementation_execution_defect`
- `verification_or_test_oracle_failure`
- `deployment_or_operational_control_failure`
- `model_runtime_or_adapter_drift`
- `evaluation_or_grader_failure`
- `not_review_detectable_at_the_time`
- `not_established`

For each contributor, record evidence, confidence, counterfactual prevention, and accountable system owner. This taxonomy is for system improvement, not automatic individual blame.

## Preventability and detection opportunity

Classify the earliest credible opportunity:

| Opportunity | Test |
|---|---|
| Specification-preventable | A clearer authoritative requirement or decision would have prevented the defect |
| Plan-preventable | A competent plan using available evidence should have covered it |
| Routing-preventable | The correct lens or human authority would likely have found or decided it |
| Review-detectable | The assigned reviewer had sufficient evidence, tools, and mandate |
| Adjudication/remediation-preventable | A surfaced finding was mishandled or incompletely resolved |
| Closure-preventable | Final integrity or condition checks should have blocked approval |
| Implementation-detectable | Only the actual diff, tests, or runtime behavior exposed it |
| Operations-detectable | The plan could reasonably require monitoring or containment, not preclude the event |
| Not reasonably detectable | Evidence or knowledge did not exist and no prudent control was omitted |
| Not established | Available evidence cannot support a classification |

An event can be review-detectable and implementation-detectable; record both while naming the earliest reliable opportunity.

## Hindsight controls

- Reconstruct only the evidence available at each historical stage.
- Do not treat a bad outcome as proof that every earlier decision was unreasonable.
- Do not treat absence of an incident as proof that a waiver or risky plan was safe.
- Distinguish a reviewer missing evidence from the input contract never supplying it.
- Blind causal reviewers to author/model identity where practical.
- Preserve contemporaneous records rather than replacing them with retrospective summaries.
- Require supporting evidence for both escapes and false-positive claims.
- Use `not established` when counterfactual prevention cannot be defended.

## False-positive handling

A finding is not false merely because the implementation succeeded, the author disagreed, or the proposed scenario did not occur. Establish that the claim was unsupported, contradicted by authoritative evidence, immaterial under policy, or outside the reviewer’s mandate.

For confirmed false positives, measure:

- unnecessary plan changes or scope growth;
- delay and human adjudication cost;
- whether the adjudicator should have rejected the finding;
- whether a rubric encouraged stylistic or speculative criticism;
- what clean evaluation case will prevent recurrence.

## Waiver and human-decision outcomes

Track active waiver assumptions and controls through implementation and the observation window.

- If an assumption fails, re-open the linked decision and waiver immediately.
- If a compensating control activates successfully, record the control result without declaring the underlying risk nonexistent.
- If scope changes, revalidate authority and artifact binding.
- If expiry arrives, treat the waiver as absent until renewed through component 7.
- Compare waived-review outcomes with comparable non-waived work to detect systematic blind spots.

## Metrics

Report by risk tier, lens, domain, component version, adapter, and event class:

- review, routing, adjudication, revision, and closure escape rates;
- preventable escape rate and earliest detection opportunity;
- implementation deviation rate;
- confirmed reviewer false-positive and false-block rates;
- time from evidence availability to detection and containment;
- incident impact reduced by planned controls;
- waiver activation, control-failure, expiry, and renewal rates;
- recurrence rate after a learning action;
- learning-action age and closure rate;
- proportion of actions converted to deterministic enforcement;
- unique confirmed yield and marginal value by reviewer lens;
- cost, latency, rework avoided, and review-induced rework;
- evaluation case coverage created from live events.

Observed escape rate is a lower bound because undiscovered defects remain invisible. Pair outcome metrics with seeded evaluations and periodic expert audit from component 6.

## Learning-action policy

Create a production change only when:

1. The event is material or represents a credible recurring class.
2. The proposed intervention addresses an evidenced causal contributor.
3. The rule generalizes beyond the single wording or artifact.
4. A case demonstrates the intended improvement.
5. A clean or boundary case protects against overcorrection.
6. The intervention is placed in the most reliable layer.
7. An owner, evaluation plan, rollback target, and expiry/review condition exist.

Prefer deterministic checks for stable objective invariants. Reserve semantic reviewers for contextual judgment. Retire rules and reviewers that stop matching the task population or create more harm than they prevent.

## Cadence and triggers

Run conformance at implementation completion and before production release for material plans. Observe outcomes according to the plan’s defined windows. Open immediate feedback events for:

- a blocker/major escaped defect;
- incident, rollback, data loss, security/privacy event, or material customer harm;
- an unauthorized implementation deviation;
- a waiver assumption or compensating-control failure;
- a confirmed false blocker causing material rework or delay;
- model, adapter, tool, or policy drift implicated in a decision.

On a volume-appropriate schedule, sample successful and uneventful plans, rejected findings, active waivers, and low-risk work. Incident-only learning biases the corpus toward visible failures and cannot measure false positives or quiet degradation.

## Data governance

- Collect only evidence needed for review-system learning.
- Apply repository, customer-data, incident, and personnel access policies.
- Redact secrets and sensitive personal data before evaluation reuse.
- Record retention, deletion, and access authority.
- Keep sealed evaluation oracles separate from normal agent context.
- Do not publish incident-derived cases without authorization and sanitization.

## Pipeline handoffs

| Feedback result | Required destination |
|---|---|
| New deterministic risk trigger | Classifier policy and component 6 routing cases |
| New reviewer failure mode | Reviewer rubric/reference and component 6 seeded plus clean cases |
| Evidence/context failure | Component 2 input contract and fixture validation |
| Adjudication or closure failure | Components 4/5 plus regression cases |
| Authority or waiver failure | Component 7 policy, matrix, and waiver cases |
| Cancellation or residual-obligation failure | Component 7 cancellation policy/record plus component 6 state-stream and cancellation cases |
| Material event after lifecycle closure | New linked remediation lifecycle through component 3, with fresh component-2 contract and classification |
| Runtime/adapter drift | Component 3 orchestration and adapter-equivalence suite |
| Stable recurring objective rule | Deterministic script/schema/test rather than prompt prose |
| Low-value or duplicative reviewer | Classifier consolidation/retirement proposal and comparative evaluation |

No handoff changes a promoted component directly. Component 6 establishes the evidence and recommendation, component 7 authorizes the exact effect, and the registry applies only that hash-bound decision.

## Completion criteria

- [ ] Approved-plan, implementation, decision, waiver, and review IDs are traceable end to end.
- [ ] Diff-time classification and conformance run on material implementations.
- [ ] The release gate blocks on material deviations, pending lenses, unknowns, invalid waivers, or missing exact-revision authority.
- [ ] Outcome windows and success/failure signals are declared.
- [ ] Escapes, false positives, near misses, control results, and successes can all be recorded.
- [ ] Causal classification reconstructs evidence available at the time.
- [ ] Preventability is separated from blame and hindsight.
- [ ] Waiver assumptions and controls are monitored through expiry.
- [ ] Cancellation obligations remain traceable to durable destinations and are monitored through verified fulfillment.
- [ ] Feedback events bind the exact governing decision, waiver, closure, conformance, and release-gate record versions and hashes.
- [ ] Material post-closure feedback creates one hash-bound successor lifecycle through the ordered event/genesis/contract acknowledgment handshake.
- [ ] Every production learning change has seeded and clean evaluation cases.
- [ ] Component 6 gates every prompt, skill, policy, tool, schema, and adapter change.
- [ ] Action effectiveness and recurrence are measured after promotion.
- [ ] Sensitive feedback evidence follows retention and access policy.
