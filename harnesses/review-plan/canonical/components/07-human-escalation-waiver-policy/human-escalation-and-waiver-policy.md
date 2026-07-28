# Human escalation and waiver policy

## Purpose

Use this policy when the review pipeline reaches a decision that an agent cannot discover from evidence or is not authorized to make. It defines who must decide, what evidence they receive, how decisions and waivers are bounded, and how downstream stages verify them.

This component consumes IDs and evidence from the classifier, [review input contract](../02-review-input-contract/review-input-contract.md), reviewer findings, adjudication ledger, final closure gate, and [evaluation harness](../06-evaluation-drift-harness/evaluation-and-drift-harness.md). It emits versioned human-decision and waiver records. Component 8 later connects those records to implementation outcomes.

Human involvement is not a substitute for missing analysis. Escalation should present a decision-ready evidence packet, not transfer an unstructured agent conversation to an approver.

## Core invariants

1. Agents identify, analyze, and recommend; accountable humans accept consequential product and residual-risk decisions.
2. A decision MUST name the authority under which the person acts. “Human approved” is insufficient.
3. No response, timeout, or ambiguous acknowledgment is never approval.
4. A waiver is scoped to exact artifacts, findings, policy rules, and versions. It is not reusable precedent by default.
5. Every waiver has an owner, rationale, compensating controls, monitoring, expiry, and re-review triggers.
6. A semantic classifier cannot remove deterministic mandatory reviews. Only an authorized review waiver can do so.
7. An agent cannot grant, renew, broaden, or approve its own waiver.
8. A drafter or change owner cannot be the sole risk acceptor where policy requires independent domain authority or separation of duties.
9. Material plan changes invalidate decisions whose assumptions, scope, or risk surface changed.
10. Final approval applies only to the exact plan and evidence versions named in the decision record.
11. Rejected findings and dissenting evidence remain auditable; majority vote is not a substitute for evidence.
12. Unknown high-impact facts remain `not established` until evidence or an authorized decision resolves them.

## What requires escalation

Escalate when any of the following is true:

### Intent and specification

- Authoritative source artifacts conflict.
- A missing product decision can materially alter scope, behavior, interfaces, tests, rollout, or acceptance.
- The plan defers or changes a ticket requirement without documented authority.
- A requested addition has no traceable requirement or approved risk-control rationale.
- A reviewer would need to choose among legitimate stakeholder trade-offs.

### Consequence and recoverability

- A change is irreversible or recovery is unproven.
- Blast radius, financial exposure, privacy impact, safety impact, or legal consequence exceeds the configured threshold.
- Rollback is weak, unavailable, or itself risky.
- Operational ownership during rollout or incident response is missing.
- A production action needs credentials, mutation authority, or break-glass access not already granted.

### Specialist authority

- Authentication, authorization, secrets, tenancy, or trust boundaries materially change.
- Sensitive data, retention, consent, or regulated obligations change.
- Payments, billing, entitlements, or irreversible user effects change.
- A schema migration, destructive data operation, or high-volume backfill carries material loss or consistency risk.
- A public/cross-team contract changes without the accountable consumer or owner decision.
- A domain specialist marks a risk as requiring accountable acceptance.

### Review and evidence integrity

- A blocker or major finding remains disputed after evidence-based adjudication.
- Required evidence is unavailable or contradictory.
- A mandatory review cannot run or cannot obtain the evidence required by policy.
- Reviewers or adjudicators disagree on a material factual or policy question that further inspection cannot resolve.
- The reviewer’s independence, permissions, source order, or artifact integrity was compromised.
- The final closure gate discovers a new material risk or an unresolved accepted finding.
- The evaluation harness blocks promotion, detects material drift, or requires rollback.

Do not escalate a preference merely because reviewers disagree on architecture. Escalate when the choice changes an authorized outcome, material risk, policy obligation, ownership decision, or evidence threshold.

## Escalation classes

Classify the requested human action before assigning it.

| Class | Human action |
|---|---|
| Specification decision | Resolve intent, priority, scope, or acceptance criteria |
| Evidence decision | Decide whether supplied evidence meets an organizational threshold |
| Residual-risk acceptance | Accept a known risk after analysis and controls |
| Review waiver | Authorize omission or consolidation of a normally mandatory review |
| Policy exception | Temporarily depart from a stated engineering or governance rule |
| Operational authorization | Approve rollout, production mutation, credentials, or break-glass action |
| Release decision | Approve, condition, block, or roll back a version |
| Lifecycle cancellation | End a lifecycle without claiming completion and assign every surviving obligation to a durable destination |
| Evaluation promotion/rollback | Promote, shadow, block, or roll back a review-pipeline component version |

A specification decision changes or clarifies the source contract; it is not a waiver. A deferral does not make a mandatory requirement complete. If the ticket goal changes, update and version the authoritative source before re-review.

The canonical machine values, shared unchanged by the decision record, authority matrix, evaluation harness, and every consumer, are:

```text
specification
evidence
residual-risk
review-waiver
policy-exception
operational
release
cancellation
evaluation-promotion-rollback
```

Adapters may display friendlier labels but cannot add, omit, or rename decision classes inside canonical records.

`emergency-authorization` is a waiver type, not a tenth decision class. Every emergency-authorization waiver MUST be authorized by a decision whose canonical `trigger.class` is `operational`, and the matched authority-matrix rule MUST likewise use `decision_class: operational`. That operational rule must require the emergency hard stop, monitoring and rollback/containment, dual control where feasible, and retrospective described by this policy. A `policy-exception` decision or an adapter alias cannot substitute for this mapping.

## Roles and authority

Organizations must map these logical roles to named people or groups.

| Logical role | Authority |
|---|---|
| Change owner | Owns the plan, evidence assembly, remediation, and ordinary bounded decisions |
| Product/requirement owner | Decides intended outcome, priority, scope, and accepted non-goals |
| Domain approver | Decides within security, privacy, data, SRE, finance, legal, accessibility, or another specialty |
| Risk acceptor | Accepts specified residual consequence within a documented mandate |
| Release authority | Authorizes deployment or production mutation under release policy |
| Policy owner | Grants or rejects exceptions to the policy it owns |
| Evaluation owner | Promotes, blocks, or rolls back review-pipeline components |
| Auditor | Verifies process and records but does not gain decision authority by reviewing them |

Authority MUST be checked against risk type, tier, environment, value/blast-radius threshold, and organizational policy. Every decision and waiver binds the exact active authority-matrix ID, version, and self-hash plus matched rule and authority-entry IDs. Role labels in an agent-produced record do not prove authority.

## Default approval depth

Use this as a starting policy and replace it with organization-specific authority rules.

| Risk tier | Minimum human control |
|---|---|
| Tier 0 — low | Named change owner under normal policy; no special waiver for configured trivial classes |
| Tier 1 — normal | Named engineer or product owner accountable for the decision |
| Tier 2 — high | Change owner plus each triggered domain/risk authority; independent acceptance where the owner benefits from proceeding |
| Tier 3 — critical | Named accountable authority, required domain approvals, and dual control for irreversible or high-consequence execution |

The number of approvers is not a confidence score. Each approver must cover a distinct authority. Five generic approvals do not replace one required security, data, legal, or operations owner.

## Escalation workflow

```text
trigger detected
      ↓
create escalation record and freeze evidence
      ↓
classify decision + resolve authority
      ↓
decision-ready review
      ↓
approve | approve with conditions | reject | defer | request evidence
      ↓
apply decision to source/plan/policy/ledger
      ↓
reclassify and run required re-reviews
      ↓
verify exact-artifact closure
      ↓
close, expire, or revoke
```

### 1. Create the escalation

Use the [escalation and decision record](escalation-and-decision-record.md). Link the input contract, plan hash, finding IDs, classifier/review IDs, policy rule, risk tier, and triggering evidence.

### 2. Build a decision-ready packet

Supply:

- the question requiring authority;
- authoritative source and policy excerpts;
- observed facts, inferences, and unknowns separated;
- credible options, including no-change or delay where applicable;
- impact, likelihood, blast radius, reversibility, and detection;
- reviewer and adjudicator conclusions with supporting and dissenting evidence;
- proposed controls, monitoring, rollback, and expiry;
- the exact downstream changes caused by each option.

Do not include pages of raw debate when a concise evidence index is available. Preserve raw artifacts by reference for audit.

### 3. Resolve the authority

Verify the named decision owner can make this class and magnitude of decision. If authority is missing or disputed, escalate to the policy owner rather than accepting the most available person.

### 4. Record one decision

Allowed decision outcomes are:

- `approved`
- `approved_with_conditions`
- `rejected`
- `deferred`
- `more_evidence_required`
- `not_authorized`

Conditions must be objectively verifiable. `Deferred` needs an owner, due date or event, and an explicit statement of what remains blocked.

`expired` and `revoked` are post-decision record lifecycle statuses, not values of `decision.state`. Record them through the top-level decision-record `status`, expiry, and revocation fields while preserving the original decision outcome and history.

### 5. Apply and re-review

- Specification decisions update the authoritative source contract.
- Accepted findings update the remediation ledger and candidate plan.
- Risk acceptances create a [risk waiver record](risk-waiver-record.md) if residual risk remains.
- Review waivers update the classifier manifest but preserve the waived lens and reason.
- Policy exceptions link the governing policy and exception authority.
- Operational authorizations constrain environment, action, time window, and operator.
- Lifecycle cancellations create an active [cancellation and residual-obligation record](cancellation-obligation-record.md) bound to the exact predecessor-state, decision, and authority hashes. Every surviving obligation must have an owner, due event, verification criteria, and durable destination; an evidence-backed, appropriately verified assertion is required when none remain.
- Evaluation decisions are issued only after the evaluation run or candidate suite is self-hashed. They bind that exact record plus candidate component/version and authorize the registry effect; the harness recommendation alone has no effect.

Material decisions trigger reclassification and affected-lens re-review. The final closure gate verifies the decision, conditions, and exact final-plan hash.

A release decision is valid only when it names component 8’s accepted release-gate ID/version/schema/hash head, exact implementation revision, and rollout-configuration hash. Conformance evidence may move a gate to `awaiting-authority`, but it cannot authorize release. Any material post-decision change invalidates the release decision and returns the lifecycle to diff-time classification.

### 6. Close and monitor

Close only after downstream artifacts reflect the decision and required verification passes. Component 8 tracks whether the decision’s assumptions, controls, and outcomes held during implementation and operation.

## Waiver types

### Residual-risk acceptance

Accepts a known remaining risk without claiming the risk was fixed. It must state the possible loss, affected population/system, rationale, controls, monitoring, recovery, and authorized acceptor.

### Review waiver

Allows a normally required lens or independent execution to be omitted, delayed, or consolidated. It must identify the deterministic rule, why equivalent evidence is available or delay is justified, what could be missed, and how coverage is restored.

A review waiver cannot delete the lens from the manifest. Record it as selected-and-waived so the evaluation and feedback systems can measure its consequences.

### Policy exception

Temporarily permits a bounded departure from an engineering or governance policy. Only the owner of that policy, or explicitly delegated authority, may grant it.

### Emergency authorization

Permits time-bounded action when following the normal path would create greater imminent harm. It requires:

- a declared emergency trigger;
- named incident/release authority;
- minimum necessary scope and duration;
- action logging and dual control where feasible;
- monitoring and rollback/containment;
- mandatory retrospective review and expiry.

Emergency authorization is not a permanent waiver and cannot silently become precedent.

## Waiver validity

A waiver is valid only when all of these are true:

- The waiver ID and type are unique.
- The exact policy rule, review lens, finding, or risk is named.
- Scope and affected artifacts are pinned by version/hash.
- The acceptor’s authority is verified.
- The risk and potential consequence are stated plainly.
- Alternatives and rejection rationale are recorded.
- Compensating controls and monitoring are testable.
- Expiry and revocation conditions are explicit.
- Required re-review and feedback hooks are present.
- No upstream artifact changed in a way that invalidates the rationale.

Invalid or expired waivers are treated as absent.

## Default non-waivable conditions

Organizational policy may add stricter rules. By default, an agent-only workflow cannot waive:

- the existence or identity of the authoritative source and candidate artifact;
- artifact-hash, provenance, or evidence-integrity failures;
- the need for an authorized human when law, contract, or policy reserves the decision to one;
- a reviewer’s lack of permission to mutate systems or access protected data;
- a known false statement represented as verified evidence;
- an unresolved conflict about who has authority;
- final approval of an artifact other than the exact reviewed version;
- retrospective logging and review after emergency authorization.

If one of these blocks urgent work, use the explicit emergency path with the appropriate accountable authority; do not manufacture an ordinary waiver.

## Invalidation and re-review

Revalidate a decision or waiver when:

- the source contract or plan changes materially;
- risk tier, blast radius, affected users, data, permissions, or environment changes;
- a supporting assumption or cited fact becomes false or unknown;
- a compensating control fails or is removed;
- monitoring detects the waived failure mode;
- the owner or authority changes;
- the expiry date or review event arrives;
- implementation deviates from the approved plan;
- evaluation or production feedback shows the review process missed a relevant class of failure.

The classifier’s diff-time mode should emit these conditions as re-review triggers. The final closure gate must reject an expired or mismatched waiver.

## Anti-patterns

- Blanket waivers such as “accept all remaining risk.”
- Permanent exceptions without review dates.
- Approval through silence, emoji, chat acknowledgment, or meeting attendance.
- Letting the drafter summarize away dissenting evidence.
- Asking an agent to impersonate a human risk owner.
- Counting approvers instead of checking distinct authority.
- Using a waiver to relabel an unmet requirement as complete.
- Waiving a review because its result is inconvenient.
- Attaching a waiver to a mutable branch or filename without a hash.
- Reusing one approval after scope, evidence, or implementation changes.
- Hiding accepted risk from final reviewers, operators, or affected owners.
- Treating cancellation as completion, using it to erase an obligation, or terminating before obligations have durable owners and destinations.
- Escalating every minor style disagreement and creating approval fatigue.

## Pipeline handoffs

| Producer | Human-policy input | Human-policy output | Consumer |
|---|---|---|---|
| Classifier | Risk tier, mandatory lenses, human gates, unknowns | Review waiver or required decision | Orchestrator and review manifest |
| Reviewer | Evidence-backed finding or unresolved question | Specification/risk decision | Adjudicator and reviser |
| Adjudicator | Canonical finding and recommended disposition | Accepted/rejected/deferred decision | Remediation ledger |
| Final closure | Unresolved condition, invalid waiver, or residual risk | Final acceptance, condition, or block | Implementation authority |
| Orchestrator | Requested lifecycle termination and current hash-linked state | Cancellation decision plus active residual-obligation record | Lifecycle state manager and component 8 |
| Evaluation harness | Promotion gate failure or drift | Promote, shadow, block, or rollback authority | Component registry/orchestrator |
| Implementation/operations | Conformance record, exact revision/configuration, deviation, control failure, or incident | Exact-scope release, containment, or renewed-risk decision | Component 8 release gate and feedback loop |

Every handoff preserves `input_contract_id`, artifact hashes, finding IDs, decision/waiver IDs, policy version, owner, and timestamps.

## Completion criteria

- [ ] Logical roles map to named organizational authorities.
- [ ] Escalation triggers are wired into classifier, reviewers, adjudicator, closure, and evaluation.
- [ ] Decision and waiver records use stable IDs and exact artifact hashes.
- [ ] Silence and timeout cannot approve a decision.
- [ ] Review waivers preserve the selected lens in the manifest.
- [ ] Waiver expiry, invalidation, revocation, monitoring, and re-review are enforced.
- [ ] Tier 2/3 decisions require appropriate domain authority and separation of duties.
- [ ] Final closure verifies all conditions against the exact final artifact.
- [ ] Emergency authorization is bounded and retrospectively reviewed.
- [ ] Cancellation binds the exact predecessor, decision, and authority records and transfers or verifies the absence of every residual obligation.
- [ ] Evaluation promotion, shadow, block, rollback, and suite activation use the shared decision class and an ordered run/suite-then-decision registry handoff.
- [ ] Component 8 can trace real outcomes back to decisions and waivers.
