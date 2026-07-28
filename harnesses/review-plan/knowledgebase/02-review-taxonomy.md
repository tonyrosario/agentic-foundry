# Review taxonomy: which review to use and when

Different reviews answer different questions. Combining them into one giant prompt usually produces shallow coverage, duplicated findings, and unclear decision rights.

## Core review types

### 1. Independent outcome audit

**Question:** If the plan were executed exactly as written, would the originating goal be achieved?

**Use:** Every material plan; especially when the plan is detailed enough to impose its own framing.

**Method:** Give the reviewer the ticket/spec first. Require it to write success criteria before seeing the plan. Then provide the plan and only its declared dependencies. Keep the drafter’s conversation and self-assessment out.

**Finds:** Scope omissions, unrequested additions, unresolved specification gaps, tests that can pass without the goal, and plan/source divergence.

**Does not establish:** Repository feasibility unless the reviewer is also given repository access.

### 2. Grounded feasibility audit

**Question:** Are the plan’s claims about the current system, APIs, dependencies, files, and constraints true?

**Use:** Unfamiliar or changing repositories; platform/API assumptions; migrations; plans containing many exact file or symbol claims.

**Method:** Read-only repository and authoritative documentation access. Require citations to files, symbols, commands, schemas, or official docs. Label anything not established.

**Finds:** Stale paths, missing call sites, incompatible patterns, impossible ordering, undeclared dependencies, and environment mismatches.

**Tension with cold audits:** An empty-directory audit preserves framing independence but cannot verify repository completeness. Use both when risk warrants it: cold outcome first, grounded feasibility second.

### 3. Adversarial falsification review

**Question:** What plausible implementation or operating condition could follow this plan and still fail?

**Use:** After basic completeness; before approval for medium/high-risk work.

**Method:** Ask for counterexamples, not generic criticism. Examples:

- Construct the smallest implementation that satisfies every named checkpoint but violates an acceptance criterion.
- Identify the repository or platform fact that would falsify each major assumption.
- Describe a realistic failure that the planned tests cannot distinguish from success.
- Find where a safe local phase creates an unsafe deployment or migration sequence.

**Finds:** Happy-path bias, weak oracles, correlated assumptions, missing failure paths, and false confidence from green tests.

### 4. Requirements and traceability review

**Question:** Does every requirement map to a change and discriminating verification method, and does every material change map back to an authorized requirement or risk control?

**Use:** PRDs, contractual work, broad feature plans, regulated work, and plans with multiple inherited/delta documents.

**Output:** A requirement → implementation → verification → owner/status matrix.

**Finds:** Orphan requirements, gold-plating, silent deferrals, and acceptance criteria with no proof.

ISO/IEC/IEEE 29148 provides a requirements-engineering foundation, while NASA explicitly includes requirements and plans in peer inspection ([ISO 29148](https://www.iso.org/standard/72089.html); [NASA SWE-087](https://swehb.nasa.gov/spaces/SWEHBVB/pages/32604573/SWE-087%2B-%2BSoftware%2BPeer%2BReviews%2Band%2BInspections%2Bfor%2BRequirements%2BPlans%2BDesign%2BCode%2Band%2BTest%2BProcedures)).

### 5. Specialist risk review

**Question:** Does the plan correctly handle a particular class of consequence?

**Use:** Only when triggered. Typical lenses:

- Security: trust boundaries, authn/authz, secret handling, abuse, supply chain.
- Privacy/legal: collection, purpose, retention, consent, geography, auditability.
- Data/migration: compatibility, backfill, dual-read/write, idempotency, reconciliation, rollback.
- SRE/operations: SLOs, capacity, telemetry, alert ownership, failure recovery, runbooks.
- Performance/cost: workload model, budgets, measurement method, regression thresholds.
- Accessibility/product policy: user segments, denied states, policy consistency, operator experience.

Microsoft recommends threat modeling during design because enumerating STRIDE threats across trust boundaries catches design errors earlier ([Microsoft secure design](https://learn.microsoft.com/en-us/azure/security/develop/secure-design)). AWS Operational Readiness Reviews similarly turn learned operational risks into repeatable checks ([AWS ORR](https://docs.aws.amazon.com/wellarchitected/2022-03-31/framework/ops_ready_to_support_const_orr.html)).

### 6. Premortem / failure-story review

**Question:** Assume the plan shipped and failed badly. What happened?

**Use:** Novel initiatives, complex coordination, unclear dependencies, or teams displaying optimism/commitment bias.

**Method:** Generate independent failure stories before discussion, cluster causes, then map high-impact causes to prevention/detection/response. AHRQ describes the project premortem as imagining failure before launch and developing mitigations ([AHRQ](https://www.ahrq.gov/hai/tools/mvp/modules/cusp/premortem-tool.html)).

**Caution:** Premortems are divergent risk discovery, not probability estimates. Do not turn every imagined event into required scope.

### 7. Comparative / alternative review

**Question:** Given two or more authorized plans, which better satisfies explicit criteria and why?

**Use:** Real decision forks, not as ritual. Blind labels and swap ordering to detect position bias.

**Method:** Criterion-level comparison using the source contract, constraints, and evidence. Reject “more detailed” or “sounds safer” as standalone reasons.

LLM judges exhibit position, verbosity, and self-preference biases; order swaps and evidence rubrics reduce but do not eliminate them ([MT-Bench judge study](https://arxiv.org/abs/2306.05685); [position-bias study](https://arxiv.org/abs/2406.07791)).

### 8. Implementation rehearsal / spike review

**Question:** Can the riskiest assumption be tested cheaply before the plan commits to it?

**Use:** Unknown API behavior, migration throughput, integration permissions, framework limitations, or uncertain UX/state flows.

**Method:** A disposable prototype, dry run, schema experiment, contract test, or command-level proof. Review the result, then update the plan.

**Value:** External feedback is stronger than introspection. Research on self-correction consistently finds that reliable environmental feedback improves revision more than simply asking a model to reconsider ([Reflexion](https://arxiv.org/abs/2303.11366); [limits of intrinsic self-correction](https://deepmind.google/research/publications/48252/)).

### 9. Verification-quality review

**Question:** Do planned tests and observations prove the intended behavior?

**Use:** Before implementation and again on the resulting tests.

**Method:** For each check, ask what wrong implementation would still pass. Inspect test setup, assertions, fixtures, failure injection, production-like behavior, and whether the check is actually run at the right phase.

Even human-validated coding benchmarks can contain flawed tests or underspecified tasks. OpenAI’s benchmark audits are a reminder that “verified” does not make an oracle infallible ([OpenAI coding-evaluation methodology](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)).

### 10. Sequencing and reversibility review

**Question:** Does the plan surface risky assumptions early and preserve safe intermediate states?

**Use:** Phased work, migrations, cross-service changes, and follow-up-dependent variants.

**Method:** Inspect prerequisites, deployment order, compatibility windows, critical path, irreversible steps, hold points, and rollback. Ask whether a later phase can invalidate an earlier interface or force broad rework.

### 11. Adjudication / finding-validation review

**Question:** Which findings are real, material, in scope, and supported?

**Use:** After multiple reviews and before revision.

**Method:** The adjudicator independently reads the source contract and plan first, then the findings. It confirms, rejects, merges, downgrades, escalates, or marks each as not established. It must cite evidence and may not decide by vote.

### 12. Post-revision regression review

**Question:** Does the final plan still satisfy the whole source contract, and did revisions introduce new gaps?

**Use:** Mandatory after material revision; targeted review may suffice for editorial changes.

**Method:** Review the final artifact, not only a summary of edits. Re-run traceability and all lenses affected by the change. A review of version 1 is not approval of version 2.

### 13. Post-implementation conformance review

**Question:** Did implementation and actual behavior match both the approved plan and original goal?

**Use:** Before merge/release and after rollout for material changes.

**Method:** Compare final diff, migrations, dependencies, test evidence, runtime observations, deviations, and unresolved risks against the plan and source contract. Tests are one layer, not the entire review.

### 14. Workflow red-team review

**Question:** Can the review process itself be misled, bypassed, or made noisy?

**Use:** When establishing or changing reviewer prompts, agent permissions, tool access, or automatic gates.

**Test cases:** malicious instructions in tickets/logs; stale evidence; fake test output; shared hidden premise; same-model consensus; excessive false positives; unauthorized writes/network; reviewer prompt drift; and a final revision not re-reviewed.

## Recommended combinations by work type

| Work | Minimum useful combination |
|---|---|
| Small reversible local change | Source-contract check + deterministic checks + independent diff review |
| Normal feature | Outcome audit + grounded feasibility + verification review; final re-review if changed |
| Cross-service/API change | Add interface/architecture and sequencing reviews |
| Data migration | Add data specialist, rehearsal, reconciliation, rollout/rollback reviews |
| Auth/security/privacy | Add threat-model specialist and accountable human sign-off |
| Novel/high-blast-radius system | Add premortem, operational readiness, prototype/spike, and post-release review |
| New or modified review prompt | Gold-set replay + workflow red team + shadow/canary evaluation |

## Adversarial does not mean antagonistic

An adversarial reviewer should maximize tested claims, not objections. Require findings to contain a triggering scenario, violated requirement or invariant, evidence, impact, and confidence. Reward `ACHIEVES GOAL` when no material gap is found. A reviewer optimized to always find something will manufacture low-value criticism and eventually be ignored.
