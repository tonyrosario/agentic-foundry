# Industry practices for adversarial review of agentic engineering plans

**Purpose.** This memo collects public, primarily first-party evidence about how high-performing engineering organizations make plans, designs, and changes safer. It then translates the evidence—explicitly marked as **inference**—into a review model for agent-authored plans. It is not a claim that any one company uses the proposed model.

## Executive synthesis

The strongest recurring pattern is not “add an architecture committee.” It is a **risk-proportional, staged learning loop**:

1. Record significant, reversible-or-not decisions with context, alternatives, and consequences.
2. Let peers and the relevant domain experts challenge the proposal early, asynchronously where possible.
3. Turn the claims in the proposal into executable or observable checks: tests, rollout gates, SLOs, telemetry, and recovery procedures.
4. Learn from incidents and near misses, then feed those lessons back into the next review checklist.

This avoids two symmetric failures. A plan can be *under-reviewed*, which hides unsafe assumptions until production; or *over-governed*, which turns reviewers into a slow centralized gate and increases batch size and risk. DORA’s research-backed guidance is unusually direct: peer review plus automation is preferable to heavyweight external approval for ordinary changes, while added scrutiny should be targeted to high-risk work ([DORA, “Streamlining change approval”](https://dora.dev/capabilities/streamlining-change-approval/)).

For agentic planning, the principal adversarial question becomes: **what evidence, boundary condition, or operational outcome would falsify this plan before it creates an expensive or unsafe change?** Agents increase drafting speed; they do not eliminate uncertainty, hidden coupling, ownership ambiguity, or the need for independent evidence.

## Evidence by organization / research program

### Google: postmortems as reviewed, shareable prevention artifacts

Google SRE describes a postmortem as a written record of impact, mitigation, root causes, and follow-up actions intended to reduce recurrence. For significant incidents, drafts are reviewed by senior engineers for completeness—incident data, impact, depth of root cause, appropriateness/prioritization of action items, and stakeholder sharing—then shared broadly and retained in a repository ([Google SRE Book, “Postmortem Culture”](https://sre.google/sre-book/postmortem-culture/)). Google explicitly treats an unreviewed postmortem as effectively useless and encourages recurring review sessions.

The newer SRE Workbook adds operational detail: conclusions should be fact- and data-linked; prompt publication preserves freshness; action-item closeout must be rewarded alongside writing; cross-team reviews and a cross-functional developer/SRE/leadership group can review the process and template itself ([Google SRE Workbook](https://sre.google/workbook/postmortem-culture/)). Google also recommends aggregating structured postmortem data to reveal vulnerable services and systemic reliability dysfunctions ([Google incident-management guide](https://sre.google/resources/practices-and-processes/incident-management-guide/)).

**Artifacts reviewed:** incident timeline, impact/blast radius, root cause and trigger, evidence, mitigations, prioritized prevention actions, owner/status metadata.

**Specialized reviewers:** senior engineers initially; cross-functional developers, SREs, and organizational leaders at the process level. The culture is explicitly blameless rather than accountability-free: the focus shifts from who erred to conditions, information, systems, and procedures that permitted failure.

**Useful failure modes called out by Google:** shallow causes; unreviewed or late documents; action items that never close; repeated incidents treated as isolated; and blame suppressing the information reviewers need.

### Amazon / AWS: decision logs and operational-readiness checklists derived from incidents

AWS Prescriptive Guidance defines an ADR as the durable record of an architecturally significant decision: context, decision, and consequences. It recommends ADRs for structure, non-functional requirements (including security/availability/fault tolerance), dependencies, interfaces, and construction techniques. Proposed ADRs are reviewed; accepted ADRs become immutable and later changes are captured as superseding ADRs, preserving the decision history ([AWS, “Architectural decision record process”](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)).

AWS’s Operational Readiness Review (ORR) is the complementary operational artifact. AWS says it distilled lessons from operational incidents into self-service, lifecycle-wide checklists; questions cover architectural recommendations, operational process, event management, and release quality ([AWS Well-Architected, ORR paper](https://docs.aws.amazon.com/wellarchitected/latest/operational-readiness-reviews/wa-operational-readiness-reviews.html); [ORR implementation guidance](https://docs.aws.amazon.com/wellarchitected/2024-06-27/framework/ops_ready_to_support_const_orr.html)). Its purpose is preventing known recurring causes without imposing a centralized bottleneck.

**Artifacts reviewed:** ADRs/decision log; architecture and operational checklist; release quality; event-management and support readiness.

**Stages:** an ADR moves through proposed review to acceptance/supersession; ORRs are revisited from inception through post-release operations.

**Tradeoff:** standard questions make decentralized teams safer and faster, but a static checklist decays. AWS explicitly says questions should evolve from the organization’s own correction-of-error/post-incident learning.

### Shopify: bounded, async RFCs for rapid alignment

Shopify’s guide to running engineering programs describes engineering RFCs as a critical, ad-hoc mechanism during technical design or after performance-testing analysis. It favors GitHub-based asynchronous templates and rules of engagement. The scope is deliberately smaller than whole-program consensus; if alignment is not reached by the deadline and no one has explicitly vetoed the approach, the author decides how to proceed ([Shopify, “A Guide to Running an Engineering Program”](https://shopify.engineering/running-engineering-program-guide)). The same guidance prompts teams to identify concerns that threaten definition of done and to name what they are *not* doing, since stakeholders inherit the technical debt of decisions.

**Artifacts reviewed:** narrow technical design choices, post-performance-test decisions, definition-of-done risks, exclusions/deferred work.

**Review mechanism:** time-boxed async discussion with explicit veto semantics, rather than open-ended consensus-seeking.

**Tradeoff:** this preserves speed and author ownership; it relies on the template, the deadline, and reviewers actually surfacing material objections. It is not evidence that an RFC alone validates operability or security.

### Meta: shift detection earlier, suppress low-value signal, make reliability measurable

Meta’s Fix Fast program combines teams that produce performance, reliability, and correctness regression signals, with the stated aim of moving actionable detection upstream. Meta reports millions of tests on diffs daily, IDE tests before review, and deliberate removal/deduplication of noisy or unactionable bot signals ([Meta, “Fix Fast”](https://engineering.fb.com/2021/02/17/developer-tools/fix-fast/)).

Meta’s SLICK work provides a complementary planning constraint: define service-level indicators/objectives early, make them discoverable in standard dashboards, report them periodically, and use misses to launch reliability reviews and verify that corrective changes restored the objective ([Meta, “SLICK: Adopting SLOs”](https://engineering.fb.com/2021/12/13/production-engineering/slick/)).

**Artifacts reviewed:** code diffs and regression signals; SLI/SLO definition, dashboard and history; reliability report; observed regression and remediation.

**Specialization:** shared infrastructure/reliability tooling produces early signals, while service owners act on them.

**Failure modes:** late detection, untriaged flood/noisy bots, and metrics that cannot be located or connected to an owner. For agentic reviewers, a long list of speculative findings is analogous to a noisy bot: it consumes attention without improving decisions.

### Microsoft: multi-pillar design checklists, operational proof, and safe release design

Microsoft’s Azure Well-Architected guidance frames reviews as business-contextual tradeoffs across reliability, security, cost, operational excellence, and performance—not universal compliance. It advises prioritizing relevant checklist items by criticality, compliance, and time-to-market ([Microsoft, framework overview](https://learn.microsoft.com/en-us/azure/well-architected/what-is-well-architected-framework)).

The operational-excellence checklist asks reviewers to examine standard practices and role clarity; lifecycle transparency; infrastructure-as-code; automated supply-chain quality gates; monitoring/telemetry; incident roles/procedures/recovery; quality practices; and safe deployment with small increments, progressive exposure, and planned emergency deployment ([Microsoft, operational-excellence checklist](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/checklist)). Microsoft’s reliability checklist includes resilience/availability scenario testing and chaos-engineering principles ([Microsoft, reliability design-review checklist](https://learn.microsoft.com/en-us/azure/architecture/framework/resiliency/app-design)).

**Artifacts reviewed:** prioritized pillar checklist, explicit requirements and tradeoffs, IaC/pipeline, telemetry, incident and recovery design, test/chaos scenarios, rollout and rollback design.

**Tradeoff:** breadth prevents a plan from optimizing only the happy path, but a 60-question assessment is potentially too heavy for every change; Microsoft suggests staging/pillar-by-pillar assessment and using specialized reviews for narrower workloads ([Microsoft, assessment guidance](https://learn.microsoft.com/en-us/azure/well-architected/design-guides/implementing-recommendations)).

### GitHub: review the lifecycle of mitigations, not merely the triggering incident

GitHub’s 2026 account of outdated rate-limit protections is especially useful for adversarial review. Emergency controls that were justified during abuse incidents remained in place without expiry, post-incident review, or impact monitoring, eventually blocking legitimate users. GitHub’s corrective direction: make incident mitigations temporary by default; require an intentional documented decision to retain them; improve visibility; and conduct post-incident review ([GitHub, “When protections outlive their purpose”](https://github.blog/engineering/infrastructure/when-protections-outlive-their-purpose-a-lesson-on-managing-defense-systems-at-scale/)).

GitHub also recommends using incident/postmortem context and compact telemetry when assessing platform changes; for distributed infrastructure, it highlights testing on a real test site and exercising provisioning/deprovisioning, not only desired-state configuration ([GitHub, “How engineers tackle platform problems”](https://github.blog/engineering/infrastructure/how-github-engineers-tackle-platform-problems/)).

**Artifact addition:** every mitigation, flag, safeguard, or override should carry owner, purpose, metrics, expiry/review date, and deletion/normalization plan.

### DORA: review close to the work; automate routine proof; escalate by risk

DORA’s published research synthesis says peer review during development plus automated checks early in the lifecycle is the preferred ordinary change-approval mechanism. It reports no evidence that heavyweight external approval lowers change-failure rates, and notes that delays tend to create larger, less frequent, riskier batches ([DORA, “Streamlining change approval”](https://dora.dev/capabilities/streamlining-change-approval/)). DORA instead recommends high-risk-change detection and additional scrutiny, plus continuous testing, CI, and observability.

DORA also treats loosely coupled architecture/teams as a delivery capability: teams should be able to make substantial local changes, test in isolation, and deploy independently; it explicitly offers the percentage of design changes requiring outside formal approval as a measure of decision friction ([DORA, “Loosely coupled teams”](https://dora.dev/capabilities/loosely-coupled-teams/)). Its Core Model links delivery performance with fast feedback, continuous integration, monitoring/observability, SLOs, reliability engineering, security, documentation quality, and working in small batches ([DORA Core Model](https://dora.dev/research/)).

**Implication supported by evidence:** do not route all plans to a central adversarial board. Use independent peer review and automated evidence for normal work; reserve specialized, deeper review for a declared risk threshold.

## Coverage note: companies requested but limited public evidence found

I found no sufficiently specific, public, first-party process description for Uber, Netflix, Cloudflare, or Stripe that adds rigor beyond the sources above within this research pass. Their absence here is an evidence limitation, not a claim that they lack mature practices. Stripe’s publicly indexed “design review” material concerned card-art approval, not engineering design review, so it is intentionally excluded. A credible plan-review process should not fill such gaps with folklore.

**Post-memo synthesis update.** A subsequent primary-source search found Uber’s May 2026 account of a first-pass AI PRD evaluator. It gathers linked and adjacent company context, calibrates review depth by proposal class, scores multiple readiness dimensions, prioritizes actionable gaps, and explicitly positions AI upstream of—not as a replacement for—expert judgment ([Uber, “Lessons from Building a First-Pass AI PRD Reviewer”](https://www.uber.com/gb/en/blog/first-pass-prd/)). This source is incorporated into the curated knowledgebase. The original coverage note is retained to preserve the research trail.

## Proposed adversarial-review model for agentic plans (**inference**)

The following is a synthesis of the evidence, tailored for plans generated or accelerated by agents.

| Stage | Required artifact / question | Appropriate reviewer(s) | Exit evidence |
|---|---|---|---|
| 0. Triage | Risk classification: blast radius, reversibility, data/security/compliance, dependency count, novelty, operational change | Author + owning peer | Review tier and required specialists declared |
| 1. Intent | Problem, user/business outcome, constraints, non-goals, success and failure metrics | Product/owner peer | Testable definition of done; explicit exclusions |
| 2. Decision | ADR/RFC: context, alternatives, chosen option, consequences, assumptions, unresolved decisions | Domain peers; architecture only when threshold met | Dissent captured; decision/owner/date recorded |
| 3. Attack the plan | Preconditions, dependency contracts, worst credible failure modes, abuse/misuse paths, migration/data integrity, human/operator workflow | Fresh independent reviewer; security/privacy/SRE/data specialists based on risk | Findings are evidence-linked, severity-ranked, and assigned or explicitly accepted |
| 4. Operability | SLO/SLI, telemetry, alerting, runbook, ownership, capacity/cost limits, rollback/kill switch, test environment | Service owner + SRE/operations | Observable success/failure and safe recovery demonstrated |
| 5. Change validation | Automated tests, contract tests, performance/resilience experiment, progressive rollout/hold points, rollback criteria | Peer review plus automation; release owner | Each material claim maps to a check or an acknowledged residual risk |
| 6. Learn | Post-release review; incident/near-miss record; action items; temporary-control expiry | Team plus cross-team reviewers for major events | Lessons update templates/checklists and actions have owners/dates |

### Reviewer roles (**inference**)

Use roles as lenses, not a fixed committee. Select only the lenses implicated by the risk:

- **Independent plan reviewer:** tries to falsify assumptions and identify missing work, preserving independence from the agent/author’s framing.
- **Domain owner:** checks real interfaces, data semantics, current architecture, ownership, and feasibility.
- **Security/privacy reviewer:** evaluates trust boundaries, secrets, authorization, data retention, abuse and compliance.
- **SRE/operations reviewer:** checks operability, failure detection, capacity, rollback, incident duties, and recovery.
- **Data/migration reviewer:** checks schema evolution, backfill/replay, idempotency, reconciliation, data-loss/corruption paths.
- **Product/accessibility/legal specialist:** used when user harm, policy, usability, contractual, or regulatory risks are material.

### Questions that make an agentic plan review adversarial rather than editorial (**inference**)

1. Which claims are facts from the repository/system of record, and which are agent assumptions? Link the evidence or label the assumption.
2. What dependency, permission, data shape, traffic level, or operator action would make the chosen approach fail?
3. What changed at the boundary—API, schema, ownership, retry behavior, deployment order, or security trust boundary—and who must coordinate it?
4. How is success measured in production, how soon is regression detected, and who responds?
5. What is the smallest safe rollout, explicit stop condition, rollback procedure, and maximum tolerated blast radius?
6. What temporary bypass/feature flag/mitigation is created, who owns it, and when is it removed or re-justified?
7. What alternative was rejected, why, and under what future evidence would that decision be revisited?
8. Which risks remain deliberately accepted, by whom, and what is the expiry/review date?

## Design constraints and anti-patterns

### Preserve flow with risk tiers

**Inference from DORA, Shopify, AWS, and Microsoft:** make the normal path lightweight: a short plan, peer review, automated checks, and a rollback plan. Escalate only when risk warrants it—e.g., irreversible data migration, a new trust boundary, cross-team interface change, materially altered SLO/cost profile, or broad customer impact. This preserves the speed benefits of agents while concentrating scarce specialist attention.

### Require evidence, not just plausible prose

**Inference from Google/Meta/Microsoft:** an agent’s fluent explanation should never count as validation. Convert each high-impact assertion to an inspectable source, a test, an experiment, an observed metric, or a named residual risk. Findings should be concise and actionable; Meta’s experience with noisy regression signals is a warning that exhaustive but low-confidence critique can degrade review quality.

### Make plans operationally complete

**Inference from AWS ORR, Microsoft, and GitHub:** a technically correct implementation plan is incomplete if it omits monitoring, alert ownership, rollout, recovery, and lifecycle management of safeguards. Treat these as acceptance criteria, especially for agent-generated changes whose implementation speed can otherwise outpace operational preparation.

### Turn failure into reusable guardrails

**Inference from Google and AWS:** postmortems should not merely archive an explanation. Track prevention actions to completion, mine recurring patterns, and convert repeated causes into targeted checklist questions, templates, linters, tests, or platform defaults. Avoid blindly adding a rule after every incident; GitHub’s mitigation experience shows controls need review/expiry and impact telemetry.

### Avoid predictable review failures

- **Central-board theater:** generic approval replaces local responsibility and delays feedback. DORA cautions that heavyweight external approval does not show the intended reliability benefit.
- **Template theater:** every section is filled, yet assumptions, alternatives, and exit evidence are absent. Require links/checks and allow “not applicable” only with rationale.
- **Consensus deadlock:** async RFCs without deadlines or decision rights languish. Shopify’s explicit deadline/veto framing is a useful countermeasure.
- **One-time review:** designs, flags, mitigations, and runbooks decay after shipment. Schedule review based on change/risk and use incident learning to refresh the checks.
- **Blame or scorekeeping:** reviewers hide uncertainty, authors optimize for appearance, and incidents repeat. Google’s blameless framing is about increasing truthful system learning.
- **Reviewer overload:** route every plan to every specialist. Risk-tiering plus clear triggering conditions protects scarce expertise.

## Practical minimum viable policy (**inference**)

For an agent-authored implementation plan, require before work begins: (a) owner and risk tier; (b) goal, non-goals, and measurable success; (c) assumptions/evidence and dependencies; (d) implementation sequence and validation; (e) rollout, rollback, observability, and operational owner; and (f) one independent review focused on falsification rather than rewriting.

Require a deeper ADR/RFC and targeted specialist review only when the plan crosses a published threshold. After release, compare observed results to the declared success and safety metrics. For incidents and meaningful near misses, write and review a blameless postmortem, track actions, and update the review prompts when a failure pattern recurs.

## Source quality

All substantive sources above are first-party company/research publications: Google SRE, AWS documentation, Shopify Engineering, Meta Engineering, Microsoft Learn, GitHub Engineering, and DORA. The final model and recommendations are explicitly inferences; they combine compatible practices but do not purport to reproduce an internal process of any cited organization.
