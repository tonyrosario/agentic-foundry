# Adversarial review of agentic engineering plans

This knowledgebase supports the design and maintenance of reviews for engineering plans drafted by AI agents with human input. It covers Claude Code and Codex plan artifacts, staged pipelines such as CRISPY, PRDs and specifications, RFCs and ADRs, implementation plans, migration and rollout plans, and the review workflow itself.

## Executive recommendation

Do not ask several agents whether a plan is “good” and treat agreement as confidence. Use a staged evidence process:

1. Establish the source contract: ticket, requirements, constraints, non-goals, and acceptance criteria.
2. Have an independent reviewer form success criteria from that source before seeing the plan.
3. Run only the additional review lenses implicated by risk: repository grounding, architecture, security, data, operations, testability, rollout, or product policy.
4. Send findings to a separate adjudicator that checks evidence, removes duplicates and preferences, and records dispositions.
5. Let the planner revise against the adjudicated ledger.
6. Re-review the final plan whenever the revision was material.
7. After implementation, compare the actual diff and observed behavior with the approved plan and source contract.

The important unit is not the number of agents. It is the number of genuinely independent evidence channels. Apple found that a nine-model judge panel contained only about two effective independent votes because errors were correlated; the best individual judge matched or beat the panel in its tested conditions ([Apple ML Research, 2026](https://machinelearning.apple.com/research/correlated-llm-evaluation-panels)).

## Knowledgebase guide

- [What to review](01-what-to-review.md)
- [Review taxonomy](02-review-taxonomy.md)
- [Operating model](03-operating-model.md)
- [Scaling and stopping](04-scaling-and-stopping.md)
- [Expectations and anti-patterns](05-expectations-and-antipatterns.md)
- [Maintenance and evaluation](06-maintenance-and-evaluation.md)
- [Curating custom reviews](07-curating-custom-reviews.md)
- [Evidence and source guide](08-evidence-and-source-guide.md)
- [Automating audit convergence](09-automating-audit-convergence.md)
- [Canonical lifecycle components](../canonical/components/)
- [Implementation options and orchestration designs](../implementations/)
- [Reusable reviewer templates](templates/)

The source research memos are retained under [`research/`](research/).

## Evidence labels

This knowledgebase distinguishes:

- **Evidence:** supported directly by a cited study, official documentation, standard, or measured company report.
- **Company practice:** a first-party account of what an organization does; useful but not necessarily causal or generalizable.
- **Practitioner report:** attributable field experience, including newsletters and conference material; informative but weaker than controlled research.
- **Synthesis:** a recommended operating rule inferred from multiple sources. It should be validated locally.

## Core terms

- **Source contract:** the authoritative statement of desired outcome—normally a ticket, PRD, constraints, and acceptance criteria.
- **Plan:** the proposed path from current state to source-contract outcome.
- **Cold review:** a review whose agent does not inherit the drafter’s conversation or rationale.
- **Grounded review:** a review allowed to inspect the repository, authoritative documents, tests, dependencies, or runtime evidence.
- **Adversarial review:** a structured attempt to falsify plan claims or construct a plausible failure, not an instruction to be hostile.
- **Adjudication:** evidence-based disposition of findings, not majority vote.
- **Material revision:** a change to scope, architecture, public interfaces, data, security, sequencing, rollout, verification, or acceptance coverage.
- **Effective review count:** the number of distinct perspectives and evidence sources, discounted for shared model, context, prompt, or evidence blind spots.

For the broader harness vocabulary, see [Review harness vocabulary and composition](../docs/review-harness-vocabulary.md).

## Status of the evidence

There is no mature research literature directly proving an ideal workflow for adversarial review of agent-generated engineering plans. The evidence here is assembled from LLM critique and judge research, software inspection and requirements engineering, agent evaluation, code review, threat modeling, operational readiness, and first-party agentic-development reports.

Treat the workflow as a strong starting hypothesis and calibrate it against local outcomes.
