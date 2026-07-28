# What to review

Plan quality depends on upstream inputs and downstream proof. Reviewing only the final implementation plan can find internal inconsistencies while missing that the ticket was wrong, the research was stale, the design decision was never authorized, or the tests cannot distinguish success from a plausible failure.

## Review the chain, not just the plan

| Artifact | Primary question | Typical failure | Best review |
|---|---|---|---|
| Ticket / problem statement | Is the desired outcome unambiguous and valuable? | Solution disguised as requirement; missing user or policy decision | Independent outcome extraction; product/domain review |
| PRD / specification | Are requirements complete, testable, consistent, and prioritized? | Polished prose with undefined metrics, exclusions, or edge cases | Requirements/traceability audit; cross-functional readiness review |
| Research / current-state brief | Are claims current, authoritative, and separated from recommendations? | Stale files/docs; selective evidence; inferred facts presented as observed | Source-quality and repository-grounding audit |
| Design / RFC / ADR | Are consequential decisions, alternatives, assumptions, and consequences visible? | Architecture chosen by momentum; irreversible commitment hidden | Design challenge; specialist review; premortem |
| Structure / dependency map | Are ownership and boundaries accurate? | Hidden cross-team, schema, auth, or deployment coupling | Dependency/interface review |
| Implementation plan | Would exact execution achieve the source contract? | Missing surface, wrong sequence, non-discriminating tests | Independent outcome audit plus feasibility/falsification reviews |
| Test / evaluation plan | Would checks fail for realistic wrong implementations? | Tests mirror implementation; happy-path-only assertions | Verification-quality review; mutation or counterexample design |
| Migration / rollout / rollback plan | Can the change be observed, stopped, reversed, and operated? | No hold point, reconciliation, kill switch, owner, or recovery proof | Data/SRE/operational-readiness review |
| Agent context packet | Is it sufficient, current, scoped, and free of untrusted instructions? | Context leakage, stale SHA, hidden prompt injection, excess noise | Context/provenance and authority review |
| Review findings and synthesis | Were findings verified and fairly dispositioned? | Majority vote; preferences treated as defects; rejected findings disappear | Independent adjudication audit |
| Final revised plan | Did revision introduce gaps or invalidate earlier approval? | Fixing one finding breaks traceability or sequence | Focused plus holistic re-review |
| Implemented diff and observed outcome | Did reality match the approved plan and goal? | Plan-following implementation still misses behavior; implementation drift | Conformance review, tests, runtime validation, post-release review |

NASA applies peer review and inspection to requirements, plans, designs, code, and test procedures rather than treating review as a code-only activity ([NASA SWE-087](https://swehb.nasa.gov/spaces/SWEHBVB/pages/32604573/SWE-087%2B-%2BSoftware%2BPeer%2BReviews%2Band%2BInspections%2Bfor%2BRequirements%2BPlans%2BDesign%2BCode%2Band%2BTest%2BProcedures)). NIST likewise recommends that qualified people not involved in the design review it against security requirements and identified risks ([NIST SSDF](https://csrc.nist.gov/Projects/ssdf)).

## Claude Code and Codex plans

Tool-generated plan-mode artifacts are useful tactical contracts, but they are not automatically product specifications or architecture decisions.

Review them when the work is unfamiliar, multi-file, cross-boundary, risky, or ambiguous. A one-line, reversible change with strong deterministic checks rarely needs a large plan review. Claude Code’s own documentation positions plan mode as read-only exploration before mutation and supports editing/approving the plan before execution ([Claude Code permission modes](https://code.claude.com/docs/en/permission-modes)). OpenAI reports that agent-first development required depth-first decomposition into design, code, review, and test, plus repository-visible knowledge and enforceable feedback loops ([OpenAI harness engineering](https://openai.com/index/harness-engineering/)).

For a Claude/Codex plan, check:

- source-contract traceability;
- current repository facts and exact evidence locations;
- omitted files, interfaces, user surfaces, actions, data paths, or owners;
- decisions silently made by the agent;
- phase prerequisites and whether risky work fails early;
- tests that demonstrate behavior rather than merely execute code;
- rollout, rollback, observability, and operator steps where applicable;
- whether the plan is small enough for both a human and an agent to hold coherently.

Do not review a plan-mode document only for eloquence or implementation detail. A plan can be technically rich and still solve the wrong ticket.

## CRISPY and other staged pipelines

Public descriptions of CRISPY identify Context, Research, Iterate, Structure, Plan, sYnthesize, then Implement. Its useful property is not the acronym; it is the placement of reviewable boundaries between fact discovery, decision-making, execution planning, and context handoff ([public HumanLayer workflow summary](https://www.zenml.io/llmops-database/evolving-ai-coding-agent-workflows-from-research-plan-implement-to-crispy)).

Recommended reviews by stage:

| Stage | Review target | Keep hidden initially |
|---|---|---|
| Context | Ticket interpretation, constraints, affected system, risk tier | Proposed solution if testing independent problem understanding |
| Research | Accuracy, completeness, source freshness, current-state model | Ticket’s proposed approach when avoiding solution anchoring |
| Iterate | Human decisions, alternatives, product/security policy | Nothing material; this is the decision checkpoint |
| Structure | Modules, interfaces, dependencies, ownership | Prior persuasive prose not needed to check repository facts |
| Plan | Outcome coverage, feasibility, sequence, verification | Drafter rationale during the first independent outcome audit |
| sYnthesize | Minimal execution context, provenance, instructions, permissions | Irrelevant transcripts and rejected alternatives |
| Implement | Diff, tests, runtime evidence, plan deviations | Implementer’s self-certification during cold review |

The same review boundaries apply to Research–Plan–Implement, spec-driven development, RFC/ADR workflows, Working Backwards-style product narratives, and design-doc processes. Names matter less than explicit inputs, decisions, evidence, and exit criteria.

## Strong patterns among high-performing organizations

There is no defensible public league table identifying one planning workflow as universally best. The strongest recurring patterns are:

1. **Customer/outcome first:** Amazon’s Working Backwards principle starts with the customer rather than implementation ([Amazon](https://www.amazon.jobs/en/landing_pages/about-amazon%20)).
2. **Early contextual review:** Uber’s PRD Evaluator gathers adjacent artifacts and prior experiments, calibrates review depth by proposal class, and strengthens drafts before expensive cross-functional review; Uber explicitly keeps final judgment with people ([Uber, 2026](https://www.uber.com/gb/en/blog/first-pass-prd/)).
3. **Bounded async decisions:** Shopify uses focused, time-boxed RFCs with explicit decision rights rather than requiring global consensus ([Shopify](https://shopify.engineering/running-engineering-program-guide)).
4. **Small, reviewable changes:** Google reports that smaller changes are reviewed more thoroughly, are easier to reason about, and waste less work if the direction is rejected ([Google engineering practices](https://google.github.io/eng-practices/review/developer/small-cls.html)).
5. **Operational readiness from learned failures:** AWS turns incident lessons into evolving Operational Readiness Review questions ([AWS](https://docs.aws.amazon.com/wellarchitected/latest/operational-readiness-reviews/wa-operational-readiness-reviews.html)).
6. **Risk-proportional approval:** DORA favors peer review and automation close to the work, with extra scrutiny for identified high-risk changes instead of heavyweight approval for everything ([DORA](https://dora.dev/capabilities/streamlining-change-approval/)).
7. **Mechanically enforced boundaries:** OpenAI reports that an agent-first repository benefited from structural tests, custom linters, executable checks, and repository-local knowledge rather than documentation alone ([OpenAI](https://openai.com/index/harness-engineering/)).
8. **Structured, replayable workflows:** Shopify reports better reliability when complex agent tasks are broken into discrete steps with guardrails and session replay ([Shopify Roast](https://shopify.engineering/introducing-roast)).

## Scope the review using risk, not document prestige

Escalate scrutiny when any of these are present:

- irreversible or difficult-to-reconcile data changes;
- authentication, authorization, secrets, privacy, payments, legal, or safety boundaries;
- new external dependencies or platform assumptions;
- public APIs, schemas, queues, protocols, or cross-team contracts;
- distributed ordering, concurrency, retry, or idempotency behavior;
- broad blast radius, weak rollback, or uncertain observability;
- material performance/cost/SLO impact;
- unfamiliar repository/domain or contradictory source artifacts;
- a plan large enough that reviewers cannot trace requirements to changes and checks.

Artifact length is a weak proxy. A five-line permission change can merit more scrutiny than a fifty-page internal refactor plan.
