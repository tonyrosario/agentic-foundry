# Curating custom reviews

The best custom audit is built from a specific decision and failure class, not from a generic demand for rigor.

## Start with a review contract

Define:

1. **Artifact:** exactly what is reviewed and its authoritative dependencies.
2. **Decision:** what the review is allowed to conclude.
3. **Threat model:** the errors or failures it should find.
4. **Evidence:** sources/tools it may use and how claims must be cited.
5. **Exclusions:** preferences or design work outside its scope.
6. **Finding schema:** scenario, violated requirement, impact, evidence, severity, confidence.
7. **Abstention:** when it must say `not established` or ask for a human decision.
8. **Exit verdicts:** explicit outcomes such as achieves / achieves with gaps / does not achieve.
9. **Versioning:** owner, version, model assumptions, and evaluation cases.

Uber’s PRD evaluator reports that frameworks tied to real decision criteria outperform generic critique, richer context changes the blind spots found, hard boundaries improve honesty, and prioritization is part of usefulness ([Uber](https://www.uber.com/gb/en/blog/first-pass-prd/)).

## Build from local failure taxonomies

Tag confirmed findings and escaped defects. Useful categories include:

- wrong problem or acceptance interpretation;
- omitted user surface or call path;
- unrequested scope/product decision;
- stale repository or external-platform fact;
- incompatible interface/schema/deployment sequence;
- missing authorization, privacy, security, or abuse path;
- weak test oracle or absent end-to-end proof;
- missing observability/rollback/operator ownership;
- late risky work or irreversible early phase;
- invalid reviewer finding or severity inflation;
- final revision not re-reviewed;
- context/provenance/authority failure.

Create a focused review only when a category is material, recurring, and not better enforced mechanically.

## Prompt anatomy

A strong custom prompt normally contains:

```text
ROLE
You are an independent [lens] reviewer. You did not author this artifact.

DECISION
Determine [one bounded question]. Do not redesign unless explicitly requested.

ORDER OF OPERATIONS
1. Read [source contract] first.
2. Record independent criteria/risks before reading [candidate plan].
3. Inspect [allowed evidence].
4. Test the plan against the criteria.

ADVERSARIAL METHOD
Attempt these specific falsifications/counterexamples: [...]

EVIDENCE RULES
Cite every material claim. Separate observed fact, inference, and unknown.

FINDING BAR
Report only issues with a triggering scenario, violated requirement/invariant,
impact, evidence, severity, and confidence. `No material findings` is valid.

OUTPUT
[fixed verdicts, criteria matrix, findings, specification gaps, residual risks]
```

The order-of-operations instruction is a real control. If the reviewer sees the plan first, it can inherit the plan’s problem decomposition.

## Customize by artifact

### Ticket/spec audit

Emphasize ambiguity, conflicting stakeholders, measurable outcomes, non-goals, edge cases, and decision ownership. Do not let the reviewer turn every ambiguity into an architecture proposal.

### Research audit

Emphasize source authority, recency, completeness, negative evidence, contradictions, and fact/recommendation separation. Require retrieval date and URLs/file citations.

### Design/RFC audit

Emphasize consequential assumptions, alternatives and rejection reasons, interface boundaries, failure model, operability, reversibility, and conditions for revisiting the decision.

### Implementation-plan audit

Emphasize exact source-contract outcome, affected surfaces, sequencing, prerequisites, check discriminating power, implementation questions, and whether checkpoints can pass while the problem remains.

### Migration audit

Emphasize compatibility matrix, state transitions, idempotency, retry/replay, backfill, reconciliation, data loss/corruption, deployment order, observability, hold points, and rollback feasibility.

### Rollout/operations audit

Emphasize SLOs, signals, ownership, thresholds, capacity, incident actions, canary population, stop/rollback, and temporary-control expiry.

### Review-synthesis audit

Emphasize evidence validation, duplicates, contradictions, reviewer overreach, severity, rejected-finding rationale, and whether human decisions are being hidden as technical conclusions.

## Customize by risk trigger

Add a specialist lens only when the plan changes that risk surface. Maintain small reusable modules rather than one giant prompt:

- `authz-boundary.md`
- `data-migration.md`
- `public-api-compatibility.md`
- `distributed-retry-idempotency.md`
- `privacy-retention.md`
- `performance-cost-model.md`
- `operational-readiness.md`
- `prompt-injection-authority.md`

Each module should identify activation conditions, required inputs, falsification questions, finding bar, and deterministic companion checks.

## Calibrate strictness

Define severity by consequence and decision threshold:

- **Blocker:** exact execution cannot achieve a mandatory outcome, or creates an unacceptable safety/security/data risk.
- **Major:** likely material rework, outage, compatibility break, or unverified high-impact assumption.
- **Moderate:** meaningful weakness with bounded workaround or evidence gap.
- **Minor:** useful correction that does not change approval.
- **Not a finding:** preference, hypothetical without trigger/evidence, out-of-scope redesign, or already-covered behavior.

Require the reviewer to explain why an issue meets the threshold. This improves adjudication and reduces “wall of comments” output.

## Add counterexample seeds

Prompts become more effective when they name the kind of failure to construct without revealing the answer to the evaluated case:

- a normal-user path is gated but a direct action/API is not;
- a migration passes locally but deploy order breaks mixed versions;
- a test asserts rendering but not behavior;
- a flag hides navigation but not deep links;
- a fallback depends on the same unavailable source;
- an admin exception silently contradicts “off” semantics;
- a deferred follow-up is actually a ticket requirement;
- a phase’s manual validation was inherited from a phase later removed.

Rotate seeds and holdout cases to prevent prompt-specific overfitting.

## When to use cheaper versus frontier reviewers

Use cheaper models for:

- deterministic traceability extraction;
- source-link checking;
- duplicate clustering;
- checklist routing;
- broad low-severity discovery with human/model validation.

Use stronger models and/or experts for:

- ambiguous source-contract interpretation;
- long-range repository coupling;
- architecture and sequencing;
- subtle auth/data/concurrency failures;
- finding adjudication;
- high-risk final review.

Evaluate locally: capability rankings on coding benchmarks do not directly predict plan-review precision.

## Curator checklist

- Is the review’s single decision clear?
- Does it read authoritative inputs in the correct order?
- Does the reviewer have enough context to judge, but not inherited persuasion?
- Are factual claims verifiable?
- Can it return no finding or `not established`?
- Does it distinguish ticket failure from preference?
- Is severity actionable?
- Is there a separate adjudication step?
- Is re-review triggered by material revision?
- Does a gold set include both defects and clean plans?
- Are model/prompt/tool/source versions recorded?
- Is the review cheaper or more informative than a deterministic check?

Use the material in [templates](templates/) as starting points, then evaluate changes through [the maintenance process](06-maintenance-and-evaluation.md).
