# Operating model: draft, review, adjudicate, revise, re-review

## Recommended pattern

Use one accountable plan owner and several bounded evidence roles:

```text
source contract
      ↓
drafter ↔ human decision owner
      ↓ approved draft
cold outcome audit ─┐
grounded audit ─────┼→ independent adjudicator → finding ledger
specialist reviews ─┘                            ↓
                                        drafter/reviser
                                                ↓
                                      final-plan re-review
                                                ↓
                                           implementation
                                                ↓
                                  diff/outcome conformance review
```

This is preferable to sending raw feedback directly back to the drafter and asking it to “fix everything.” The drafter is well positioned to revise coherently but poorly positioned to be the sole judge of criticism aimed at its own assumptions. A separate adjudicator prevents false positives, preferences, contradictions, and duplicate findings from becoming scope.

OpenAI reports an internal agent-first loop in which Codex self-reviews, requests additional specific reviews, responds to human and agent feedback, and iterates, while repository-local tools and checks provide external evidence ([OpenAI harness engineering](https://openai.com/index/harness-engineering/)). Anthropic’s public PR-review architecture similarly uses parallel bug discovery followed by verification and severity ranking, not raw comment aggregation ([Anthropic Code Review](https://claude.com/blog/code-review)).

## Role definitions

### Drafter

- Forms a coherent plan from approved inputs.
- Labels facts, assumptions, decisions, and open questions.
- Maintains source-contract traceability.
- Does not certify its own plan.

A frontier planner can be valuable for difficult synthesis, but model prestige does not remove the need for evidence or independent review.

### Human decision owner

- Owns product, risk, and trade-off decisions.
- Resolves gaps that cannot be discovered from authoritative artifacts.
- Accepts explicitly documented residual risk.
- Approves merge/release authority according to policy.

The human need not rewrite agent output. The highest-leverage work is specifying intent, supplying missing context, deciding tradeoffs, and validating outcomes.

### Cold outcome reviewer

- Starts without the drafter’s conversation.
- Reads the source contract before the plan.
- Creates independent success criteria before comparison.
- Judges outcomes rather than preferred architecture.

An empty directory is useful when it prevents accidental access to unrelated framing. Give this reviewer exactly the declared source documents and plan dependencies. Do not mistake context scarcity for factual validation.

### Grounded reviewer

- Has read-only access to the repository and authoritative external documentation.
- Verifies file, symbol, API, test, schema, and environment claims.
- Identifies relevant surfaces omitted from the plan.
- Separates observed fact from inference.

### Specialist reviewer

- Receives a narrow mandate and relevant evidence.
- Does not re-review the entire plan generically.
- Returns findings in a common evidence schema.

### Adjudicator

- Independently reads source and plan before seeing reviews.
- Validates each finding against evidence.
- Deduplicates and resolves contradiction.
- Does not invent a replacement architecture unless authorized.
- Produces the canonical finding ledger.

For high-risk work, the adjudicator should be a strong model plus an accountable human/domain expert. A cheap judge can triage obvious duplicates but should not be the final authority on subtle security, data, or product decisions.

### Reviser

Usually the original drafter, because it retains the most coherent model of plan structure. It should receive the adjudicated ledger rather than all raw debate. Every ledger item must be resolved, explicitly rejected with owner approval, deferred, or left open as a blocker.

### Final reviewer

Reviews the actual final plan. It may reuse a previous reviewer for continuity, but a cold verifier is preferable after large changes. It checks both finding closure and the whole source contract.

## Information-flow controls

Coldness should be designed, not assumed.

| Role | Should see | Should initially not see |
|---|---|---|
| Outcome auditor | Source contract, then exact plan/dependencies | Drafter rationale, previous verdicts, implementation preference |
| Grounded auditor | Source contract, plan, repo/docs/tests | Other reviewers’ conclusions until its view is recorded |
| Specialist | Relevant plan sections and system evidence | Unrelated review noise |
| Adjudicator | Source contract and plan first; then all findings/evidence | Majority tally or “author says this is fine” as decision evidence |
| Reviser | Approved source decisions and adjudicated ledger | Rejected/noise findings unless needed for explanation |
| Final reviewer | Final plan, source contract, resolved ledger, current evidence | A claim that prior approval carries forward automatically |

Claude Code documents that normal subagents start with fresh isolated contexts, though they may still inherit repository guidance; forks inherit parent context and are not cold ([Claude Code subagents](https://code.claude.com/docs/en/sub-agents)). Record the actual isolation method rather than labeling any subagent “independent.”

## Same model or different models?

Model diversity can help, but role names alone do not create independence. Shared training, provider, prompt, context, and evidence can yield correlated errors. Recent research found substantial correlation even across model families, and Apple’s nine-judge study found roughly two effective votes ([correlated-errors study](https://arxiv.org/abs/2506.07962); [Apple](https://machinelearning.apple.com/research/correlated-llm-evaluation-panels)).

Prioritize diversity in this order:

1. Different evidence or oracle: tests, repository search, official docs, runtime metrics, domain expert.
2. Different review question: outcome, feasibility, security, data, operations, verification.
3. Independent context and initial analysis.
4. Different model family/provider when cost and confidentiality permit.
5. Different sampling seed/persona only as a weak final source of diversity.

Using a frontier drafter and cheaper reviewers can be cost-effective for broad discovery. High-severity finding validation should use a model and/or human capable of understanding the relevant domain. Do not let a low-capability consensus overrule a grounded expert.

## Finding schema

Every reviewer should return:

- `id`
- `review_lens`
- `severity`: blocker / major / moderate / minor
- `source_requirement_or_invariant`
- `plan_location`
- `triggering_scenario`
- `expected_outcome`
- `plan_outcome`
- `impact`
- `evidence`
- `confidence`: with `not established` allowed
- `recommended_disposition`: fix / clarify / accept risk / defer / reject finding

The adjudicator adds:

- `status`: confirmed / rejected / duplicate / needs decision / not established
- `rationale`
- `owner`
- `resolution_in_plan_version`
- `re_review_required`

## Feedback loop

1. Freeze and identify the reviewed version.
2. Run initially independent reviews in parallel only where their tasks are separable.
3. Adjudicate before revision.
4. Resolve specification questions with the human owner.
5. Revise once coherently rather than accepting comments piecemeal.
6. Generate a traceability diff: requirements, decisions, phases, checks, and risks added/removed/changed.
7. Re-run affected specialist reviews and a holistic final outcome audit.
8. Freeze the approved version and preserve the ledger.

Anthropic reports that multi-agent research is strongest for breadth-first, separable investigations but much more token-intensive and less suitable for tightly dependent coding work ([Anthropic multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system)). Parallelize review lenses; centralize synthesis and ownership.

## Does folded feedback need another review?

Yes, when feedback changes anything material. Reasons:

- the revised plan was never reviewed;
- a fix can introduce a new inconsistency;
- phases and dependencies may shift;
- new scope may lack tests or operational handling;
- a clarification can reveal a different requirement interpretation;
- two individually valid findings can produce an invalid combined revision.

For spelling, formatting, citation repair, or an explanation that does not change commitment, a targeted verification is enough. For scope, behavior, architecture, interface, data, security, sequence, rollout, rollback, tests, or acceptance mapping, perform both affected-lens review and a final holistic outcome audit.
