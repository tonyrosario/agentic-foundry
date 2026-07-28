# Evaluation and drift harness

## Purpose

Use this harness to decide whether a review-pipeline component is safe to promote, whether a released component has drifted, and what must happen after an escape or false positive. It evaluates the pipeline as a connected system rather than grading prompts in isolation.

This folder is the canonical, vendor-neutral harness contract. Executable graders, validators, registries, storage, and runtime adapters are separate implementations that must conform to it.

The harness consumes versioned [review input contracts](../02-review-input-contract/review-input-contract.md) and emits a completed evaluation run plus a release recommendation. Component 7 then issues the separate hash-bound authorization decision that a registry may enact. It evaluates:

- classifier routing and risk tiering;
- input-contract validation and role projections;
- reviewer finding quality and evidence use;
- adjudication and remediation-ledger accuracy;
- final-plan closure decisions;
- runtime adapter equivalence;
- orchestration, isolation, permissions, and provenance.

Evaluation never certifies that a component is universally correct. It establishes that the tested version satisfies an explicit policy on a representative, versioned suite, with known limitations.

## Pipeline contract

```text
versioned component candidate
          +
evaluation suite manifest
          +
sealed case oracles
          +
review input contracts
          ↓
isolated evaluation executions
          ↓
schema checks + deterministic graders + semantic adjudication
          ↓
evaluation run record + recommendation
          ↓
component-7 evaluation decision + authority matrix
          ↓
promote | shadow only | block | roll back | no authorized effect
          ↓
release registry and lifecycle monitoring
```

### Required inputs

- Component type, identifier, and semantic version.
- Prompt, skill, policy, script, adapter, model, and tool versions that affect behavior.
- A frozen [evaluation suite manifest](evaluation-suite-manifest.md).
- One [evaluation case](evaluation-case.md) per case ID.
- A valid component-2 input contract for every executed case.
- Baseline version and results for comparative runs.
- Policy-owned release thresholds and zero-tolerance conditions.

### Required outputs

- One raw output and trace reference per trial.
- Deterministic validation results.
- Per-case semantic grading with adjudication provenance.
- Aggregate and segmented metrics.
- Regression and capability comparison against baseline.
- Limitations and facts not established.
- A signed [evaluation run record](evaluation-run-record.md).
- Exactly one release recommendation: `promote`, `shadow_only`, `block`, `roll_back`, or `not_established`.
- For any registry effect, one later component-7 `evaluation-promotion-rollback` decision bound to the completed run hash and exact authority matrix.

## Evaluation suite design

Maintain complementary case classes. No single class is an adequate evaluation.

| Case class | What it establishes |
|---|---|
| Clean positive | The system can approve a sufficient plan without manufacturing defects |
| Seeded omission | Outcome and traceability reviewers detect a missing requirement |
| Seeded infeasibility | Grounded review detects a false repository, API, or environment assumption |
| Weak oracle | Falsification or verification review catches checks that pass the wrong outcome |
| Specialist trigger | Classifier routes security, data, operational, or other mandatory lenses |
| Ambiguous source | The correct result is escalation or `not established`, not invention |
| Conflicting evidence | Authority and precedence rules are followed |
| Noisy pseudo-defect | Reviewer and adjudicator reject plausible-sounding but unsupported criticism |
| Remediation regression | Final re-review catches a fix that introduces a new inconsistency |
| Adapter equivalence | Claude, Codex, or other adapters preserve canonical semantics |
| Isolation attack | Hidden prior conclusions, memory, or untrusted instructions do not control the result |
| Lineage substitution | A stale or mismatched decision, waiver, ledger, closure, or artifact hash is rejected |
| Invalid transition | A lifecycle stage cannot advance without its canonical prerequisite record and authority |
| State-stream conflict | A fork, duplicate/skipped transition number, stale expected head, or substituted predecessor/trigger/authority hash is rejected |
| Review-execution substitution | Parallel arrays, wrong retry hashes, and review-ID-only completion cannot credit an execution or lens |
| Inconclusive progression authority substitution | Final closure rejects an ID-only, stale, expired, foreign-ledger, or otherwise invalid decision used to make a required failed/`not-established` review nonblocking |
| Supersession handshake | Outcome supersession reserves one successor ID, seals the parent terminal state, and then creates the exact bound genesis without circular hashes |
| Post-cancellation successor | A successor binds the parent cancellation state/record without inheriting or silently discharging obligations |
| Rollback re-entry | Recovery binds the rolled-back revision, active feedback ownership, new contract, and required reclassification |
| Release-gate head conflict | Only the atomic accepted release-gate version head can request or carry authorization |
| Post-terminal cancellation correction | Later decision invalidation preserves the terminal state and obligations while opening feedback/corrective response |
| Cancellation obligation loss | Cancellation is blocked when its decision or authority is mismatched, an obligation lacks a durable destination, or a no-obligation assertion lacks evidence and verification |
| Feedback lineage substitution | A feedback event cannot replace the decision, waiver, closure, conformance, or release-gate version that governed the implicated delivery with a later or ID-only record |
| Late-feedback successor loss | Material feedback after closure creates exactly one correctly bound successor lifecycle without reopening the parent or inheriting its approvals |
| Release-gate bypass | Conformance cannot authorize release while required reviews, unknowns, or authority remain pending |
| Inconclusive-review escape | A required failed or `not-established` execution becomes a blocking ledger item rather than disappearing |
| Multi-source loss | Every downstream record preserves the exact authoritative-source-bundle hash |
| Authority substitution | Decisions, waivers, and release gates reject stale or altered authority and reciprocal record hashes |
| Decision-class normalization attack | Adapters and consumers reject renamed, aliased, omitted, or unknown values instead of translating the shared canonical decision-class catalog |
| Emergency authorization class mapping | An emergency waiver is accepted only when its authorizing decision and matched authority rule both use the canonical `operational` class and all emergency controls are complete |
| Independent genesis contract binding | An independent lifecycle reserves its ID, freezes its first contract, and binds that exact contract in genesis before `input-frozen` validation |
| Review status/result correspondence | A current review record is rejected when its redundant status contradicts the authoritative completion result |
| Waived-lens visibility | Waived lenses remain selected while only their execution requirement is removed |
| Live historical | The suite remains connected to actual plans, escapes, and rejected findings |

Segment the suite by risk tier, review lens, artifact size, domain, repository access mode, and lifecycle stage. Aggregate success can hide failure in a small high-consequence segment.

## Dataset partitions

Use three non-overlapping partitions:

1. **Development set** — visible cases used to iterate on prompts and schemas.
2. **Regression set** — stable cases run on every candidate release.
3. **Private holdout** — sealed cases used for promotion and periodic audit.

Rotate new cases into the holdout from real escapes, false positives, specification disputes, and changed task populations. Retire or rewrite cases that are stale, contaminated, ambiguous, or no longer representative. Preserve historical results even when a case is retired.

Prompt authors and candidate agents MUST NOT receive sealed oracles, expected findings, mutation notes, grader rationales, or holdout labels. The runtime receives only the case’s public input contract and authorized artifacts.

## Evaluation workflow

### 1. Open a change record

Record the candidate, baseline, reason for change, target failure class, predicted improvement, possible regression, owner, and rollback target.

### 2. Freeze the suite

Resolve the suite manifest, case versions, artifact hashes, policies, model configuration, tools, adapters, and graders before running either candidate or baseline. Never modify a case after seeing a candidate failure without issuing a new case and suite version.

### 3. Validate input contracts

Reject cases whose source, plan, inheritance, authority, permissions, or artifact hashes cannot be resolved. An invalid test fixture is not evidence of component failure.

### 4. Execute independently

- Run baseline and candidate against identical public inputs.
- Randomize presentation order where comparison bias matters.
- Blind semantic graders to variant identity.
- Use fresh contexts when the production role requires independence.
- Run multiple trials when nondeterminism can affect the release recommendation.
- Store raw outputs and tool traces before grading.

Trial count is policy-owned. Increase it when outputs are unstable, consequences are high, or a single lucky pass would conceal unreliability. Report both “at least one trial passed” and “all trials passed” rather than selecting the best sample.

### 5. Run deterministic checks

Check before semantic grading:

- output schema validity;
- required fields and stable identifiers;
- artifact and citation resolution;
- deterministic routing invariants;
- prohibited lens removal;
- tool and permission compliance;
- required read/disclosure order where traceable;
- valid disposition vocabulary;
- final-plan hash identity;
- cross-record lifecycle, contract, classification, manifest, finding, ledger, closure, and release referential integrity;
- keyed canonical parent and review-execution tuples, including retry/result correspondence and rejection of parallel-array joins;
- keyed closure-local progression decisions for every inconclusive required review credited as nonblocking, matched to the exact bound ledger item, owner, expiry, and re-review obligations;
- authoritative-source-bundle identity and downstream hash preservation;
- selected-lens versus execution-required-lens invariants and waiver visibility;
- unresolved-review ledger coverage for every required failed or `not-established` execution;
- authority-matrix, decision, waiver, and ordered release-authorization hash bindings;
- byte-identical shared decision-class values across policy, records, adapters, authority rules, and evaluation authorization;
- emergency-authorization waiver mapping to an `operational` decision and matched `operational` authority rule, including hard stop, monitoring/containment, dual control where feasible, and retrospective;
- independent-lifecycle genesis binding to the exact first frozen input-contract ID/hash before the `input-frozen` transition;
- review-record status correspondence with the authoritative `completion.result`, while superseded records remain ineligible for current execution credit;
- lifecycle predecessor, transition-number, trigger-record, decision, and authority hash bindings;
- atomic state-head compare-and-swap, consecutive ordering, and single-successor enforcement;
- ordered outcome-supersession reservation/terminal/genesis handoff and origin-specific cross-lifecycle bindings;
- rollback re-entry contract/feedback/reclassification bindings;
- atomic release-gate version-head enforcement and orphan-candidate rejection;
- cancellation-record activation and complete residual-obligation transfer or verified no-obligation assertion;
- post-terminal cancellation correction semantics that preserve state and obligations;
- exact feedback lineage for governing decision/waiver versions and closure, conformance, and release-gate hashes;
- ordered post-closure feedback handoff, single successor, parent-terminal immutability, and fresh-contract/classification enforcement;
- exact-revision release-gate enforcement;
- provenance completeness.

Objective failures should not be delegated to an LLM judge.

### 6. Grade semantic behavior

Use the sealed oracle to score required findings, forbidden findings, acceptable variants, severity bands, verdicts, abstentions, and evidence. A grader must distinguish:

- the correct conclusion reached with valid evidence;
- a lucky verdict supported by invalid reasoning;
- a valid alternate formulation;
- a useful but non-required observation;
- an unsupported or out-of-scope finding.

Use expert human adjudication for disputed high-severity cases. A model grader may assist with normalization or clear matches, but it must not silently become the final authority for risks it cannot establish.

### 7. Compare baseline and candidate

Report gains and regressions by case class, risk tier, lens, adapter, and verdict. Do not promote solely because an aggregate score improves. Inspect material disagreements and representative traces.

### 8. Apply promotion gates and authorize the effect

Evaluate zero-tolerance conditions first, then policy thresholds, then operational trade-offs. Produce one explicit recommendation and rationale, finalize the evaluation-run hash, and send that exact run to component 7. The evaluation owner’s later `evaluation-promotion-rollback` decision binds the run hash, candidate component/version, selected effect, and authority matrix. The registry applies no effect from the recommendation alone.

### 9. Shadow and canary

For material changes, run the candidate on live inputs without affecting decisions. Then canary it on low-risk work with normal human oversight. Compare disagreements, costs, latency, and unique confirmed findings before general promotion.

### 10. Archive and monitor

Store the run record, raw-output references, suite/case versions, recommendation, component-7 authorization decision, limitations, and rollback target. Send production escapes and false positives to component 8’s feedback loop.

## Metrics

### Classifier and routing

- Mandatory-trigger recall.
- Unnecessary-lens rate.
- Risk-tier underclassification and overclassification.
- Unknowns correctly escalated.
- Human-gate and re-review-trigger recall.
- Deterministic/semantic precedence violations.
- Execution-portfolio consolidation correctness.

### Reviewer findings

- Seeded-defect recall.
- Confirmed-finding precision.
- False-block rate on clean plans.
- Evidence validity and source fidelity.
- Severity calibration.
- Correct `not established` rate.
- Unique confirmed findings by lens.
- Duplicate and stylistic-noise rate.

True recall on live plans is unknowable because undiscovered defects are unobserved. Report seeded recall, historical-escape recall, and expert-audit results separately.

### Adjudication and closure

- Confirmed/rejected disposition accuracy.
- Duplicate-merge accuracy without loss of distinct failure mechanisms.
- Required human-decision recall.
- Remediation-ledger completeness.
- Accepted-finding closure recall.
- New-regression detection after revision.
- Incorrect final-approval and incorrect-block rates.
- Approval-to-exact-artifact integrity.

### Reliability and independence

- All-trials success rate.
- At-least-one-trial success rate.
- Repeated-run variance.
- Equivalent-plan and plan-order consistency.
- Sensitivity to author or model identity.
- Cross-adapter semantic equivalence.
- Correlation and duplicate rate between nominally independent reviewers.
- Information-flow or context-leakage violations.

### Operational value

- Cost and latency per run and per confirmed material finding.
- Human adjudication time and disagreement rate.
- Time from draft to approved plan.
- Review-induced scope growth and rework.
- Escaped defect and false-positive rate after release.
- Marginal unique yield of each reviewer lens.

Never collapse the release recommendation or authorization decision into one opaque score. Preserve the metric vector and segment-level results.

## Promotion gates

Threshold values belong in the suite manifest and organizational policy. The following conditions block promotion regardless of aggregate score unless an authorized policy explicitly says otherwise:

- A deterministic mandatory review can be removed by semantic classification.
- A seeded blocker in a critical required segment is missed.
- A clean plan receives a fabricated blocker supported by nonexistent evidence.
- Output violates the canonical schema in a decision-critical field.
- The run uses unauthorized context, tools, permissions, or artifact mutations.
- A final closure gate approves a different plan hash from the reviewed artifact.
- A stale or cross-lifecycle record satisfies a finding, closure, waiver, or release gate.
- An ID-only, unkeyed, wrong-version, or wrong-execution reference satisfies a parent, review-completion, or lens-coverage gate.
- Final closure credits a failed or `not-established` required review as nonblocking through an ID-only, stale, expired, foreign-ledger, or otherwise invalid progression decision.
- A supersession or terminal successor bypasses its ordered origin-specific handoff.
- An orphan or forked release-gate version carries authority.
- A lifecycle transition advances without its required canonical record or authority.
- Conformance evidence is treated as release authorization.
- A waiver is accepted without the required human authority.
- An emergency-authorization waiver is accepted under a class other than `operational`, under a nonmatching authority rule, or without its required emergency controls.
- An independent lifecycle genesis has a missing, placeholder, or mismatched first input-contract binding.
- A current review record's status contradicts its authoritative completion result, or a superseded record receives current execution credit.
- The candidate materially regresses a high-risk segment without an explicit accountable decision.
- A registry effect occurs without a completed evaluation-run hash and valid component-7 evaluation decision/authority tuple.
- An adapter-renamed, aliased, omitted, or unknown decision class satisfies an authority or consumer gate.
- Holdout integrity or grader independence is compromised.
- Required provenance is missing, making the result non-reproducible.

If the evidence is insufficient to determine a gate, return `not_established`; do not reinterpret missing evidence as a pass.

## Drift detection

| Drift source | Signal | Required response |
|---|---|---|
| Model/provider | Changed snapshot, output distribution, or reliability | Replay regression and holdout suites; re-baseline before promotion |
| Prompt/skill | Instruction or reference changes | Candidate-versus-baseline run plus trace inspection |
| Policy | New mandatory trigger, waiver rule, or risk threshold | Revalidate routing, gates, and affected historical cases |
| Repository/domain | Architecture, source-of-truth, ownership, or tests change | Refresh grounded cases and evidence snapshots |
| Tool/runtime | Sandbox, search, network, memory, or subagent behavior changes | Run integration, permission, and isolation cases |
| Adapter | Vendor-specific translation changes | Run canonical-versus-adapter equivalence suite |
| Population | Live work shifts toward new risk classes | Rebalance suite and report metrics by current population |
| Threat | New injection, data-exfiltration, or supply-chain path | Add red-team cases and review permission policy |
| Evaluator | Human/model grading disagreement rises | Double-label samples, recalibrate, and audit the oracle |

Trigger an evaluation immediately when a material escape, false blocker, unauthorized action, model change, policy change, or adapter change occurs. Use scheduled replay and live-sample audits in addition to event-driven checks.

## Change and release policy

Every component change follows this state machine:

```text
draft → regression evaluation → holdout evaluation → shadow
      → canary → promoted
      ↘ block/revise                     ↘ rollback
```

Do not edit a promoted component in place. Issue a new version, preserve the previous rollback target, and record migration or compatibility requirements for downstream schemas.

Retire or consolidate a reviewer when it adds no unique confirmed findings, duplicates a deterministic check at higher cost, no longer matches current artifacts, or cannot achieve acceptable precision without missing consequential defects.

## Ownership and separation of duties

Assign accountable owners for:

- component behavior;
- suite and case curation;
- sealed holdout custody;
- deterministic graders;
- semantic adjudication;
- release approval;
- production monitoring and rollback.

For consequential releases, the component author should not be the sole holdout curator, grader, and release approver. Blind comparative adjudication where practical.

## Completion criteria

The evaluation component is ready for use when:

- [ ] Suite, case, and run-record templates have stable version fields.
- [ ] Every case references a valid component-2 input contract.
- [ ] Development, regression, and private-holdout partitions exist.
- [ ] Clean, defective, ambiguous, noisy, and remediation-regression cases exist.
- [ ] Deterministic validation runs before semantic grading.
- [ ] Metrics are reported by risk tier and review lens.
- [ ] Zero-tolerance and policy thresholds are explicit.
- [ ] Baseline comparison and rollback targets are required.
- [ ] Adapter equivalence and isolation are evaluated.
- [ ] Raw outputs and trace references are retained under the declared data policy.
- [ ] Promotion, shadow, blocking, and rollback effects bind the exact completed run, component-7 decision, and authority matrix.
- [ ] Production feedback has a defined handoff to component 8.
