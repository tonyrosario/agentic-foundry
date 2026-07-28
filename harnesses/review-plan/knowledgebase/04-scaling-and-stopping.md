# Scaling review effort and deciding when to stop

## There is no universal reviewer count

No credible source establishes “three agents” or any other fixed number as sufficient for engineering-plan review. Review need scales more strongly with consequence, novelty, coupling, reversibility, and quality of evidence than with page count.

Human inspection research supports bounded, prepared, perspective-based review rather than unlimited eyeballs. A study of more than 300 industrial specification, design, and code reviews found detected defects were driven primarily by reviewer preparation effort rather than artifact size ([Fraunhofer record](https://publica.fraunhofer.de/entities/publication/94bdd5b1-cf99-4624-b433-86efc2ae03cc)). Google similarly emphasizes that smaller changes are easier to review thoroughly ([Google](https://google.github.io/eng-practices/review/developer/small-cls.html)). Neither result translates into a guaranteed AI-reviewer count.

## Risk tiers and default review portfolios

| Tier | Typical change | Default review portfolio | Human gate |
|---|---|---|---|
| 0 — low | Docs, local test, reversible refactor, no boundary change | One source/plan check; deterministic checks; independent diff review | Owner may merge under normal policy |
| 1 — normal | Bounded feature, internal API, feature-flagged behavior | Cold outcome audit; grounded feasibility/verification review; adjudication; final review after material changes | Named engineer owns decision |
| 2 — high | Auth, money, personal data, schema migration, cross-service/public contract, broad SLO impact | Tier 1 plus 2–4 triggered specialist lenses, rehearsal where possible, explicit operational/rollback review | Domain/security/data/SRE owner as applicable |
| 3 — critical | Irreversible production mutation, safety/legal incident action, foundational platform migration | Formal source traceability, independent design review, specialist panel with evidence, staged proof, dual control, final human approval | Named accountable authority; agent proposes only unless runbook authorizes action |

“2–4 specialist lenses” does not mean four generic agents. It means the minimum distinct expertise needed to cover implicated failure modes.

## Effective review count

Discount nominal reviewers that share:

- the same model family and prompt;
- inherited drafter context;
- the same incomplete evidence packet;
- the same evaluation rubric;
- exposure to earlier persuasive findings;
- no ability to inspect or test claims.

A useful review portfolio might contain only two agents but four evidence channels: independent ticket interpretation, repository inspection, executable tests, and a human domain decision. Conversely, five persona prompts against the same text may constitute roughly one effective review.

## How plan size changes review

Do not add reviewers linearly with pages. Decompose the plan when a reviewer cannot maintain traceability.

Increase or split review when the plan includes:

- more than one independently shippable outcome;
- multiple services, teams, repositories, or deployment units;
- several public interfaces or schema versions;
- many inherited/delta documents;
- a long critical path with compatibility windows;
- phases that require different specialist knowledge;
- a requirements-to-check matrix too large to audit coherently in one pass.

Review slices vertically where possible: source outcome → design decision → implementation surfaces → verification → rollout. Avoid reviewing schema, backend, frontend, and tests as disconnected horizontal piles if correctness depends on their end-to-end interaction.

## A practical default count

Until local data says otherwise:

- **Low risk:** one independent reviewer.
- **Normal material plan:** two independent lenses—outcome and grounded feasibility/testability—followed by one adjudication step.
- **High risk:** add only the triggered specialists, normally producing three to five total lenses, then accountable human adjudication.
- **Critical:** count is policy- and domain-dependent; demand independent human expertise and external proof rather than adding generic agents.

This is an operating prior, not an empirical guarantee.

## Stopping gates

Stop when all required gates pass—not when reviewers agree stylistically or report high confidence.

| Gate | Evidence required |
|---|---|
| Source coverage | Every acceptance criterion is implemented and verified, or explicitly deferred with authority |
| Scope authorization | Every material addition maps to a requirement, risk control, or accepted decision |
| Grounding | Material repo/platform claims are cited or marked unresolved |
| Decision closure | No open question can materially change scope, behavior, architecture, data, security, or rollout |
| Risk coverage | All risk-triggered lenses have run and material residual risks have named acceptors |
| Verification quality | Checks discriminate success from at least the important plausible failures |
| Sequence/reversibility | Preconditions, compatibility, hold points, recovery, and rollback are credible |
| Finding closure | Every confirmed finding has a disposition and all required re-reviews are complete |
| Final-artifact integrity | The approved version—not a predecessor—passed the holistic outcome audit |

## Marginal-yield stopping rule

Track new confirmed material findings per review round and cost. A further generic review is usually low value when:

- required coverage gates are satisfied;
- the latest independent pass found no new evidence-backed major issue;
- remaining disagreements are preferences or explicit risk decisions;
- another reviewer would use the same evidence and failure modes.

Continue or escalate when:

- a blocker/major finding remains disputed;
- an external dependency or current-state fact is unverified;
- the plan depends on a stakeholder decision;
- a specialist surface has not been reviewed;
- the test oracle is weak;
- the plan changed materially after its last review;
- potential loss from a miss exceeds the cost of stronger review or rehearsal.

## Confidence is risk-budgeted, not absolute

Reviews reduce uncertainty; they do not prove absence of defects. Ask: “Is the residual risk below the threshold for this change and rollout?” That threshold should reflect blast radius, reversibility, observability, and recovery time.

For agent behavior itself, repeated trials matter because outputs are non-deterministic. Anthropic distinguishes `pass@k`—at least one success—from `pass^k`—all trials succeed. Reliability-sensitive workflows care about consistent success, not the ability to produce one acceptable review eventually ([Anthropic eval guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)). Use multiple trials when evaluating a reusable audit prompt; do not mechanically run every production plan through an arbitrary number of identical agents.

## Re-review policy

| Revision | Required response |
|---|---|
| Editorial only | Confirm no semantic diff; no full re-review |
| Local clarification with no changed commitment | Targeted reviewer verifies the clarification |
| Test/check change | Verification-quality re-review plus affected traceability |
| Scope, decision, interface, data, security, sequencing, rollout, or rollback change | Affected specialists plus holistic cold outcome audit |
| Large rewrite or conflicting feedback integration | Treat as a new plan version; repeat the required portfolio |

Approval is version-specific. Preserve hashes or immutable versions so there is no ambiguity about what was reviewed.
