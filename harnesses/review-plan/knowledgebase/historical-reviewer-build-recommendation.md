# Reviewers to Build Next

> **Status:** Historical design input. Its reviewer consolidation and build rationale informed the canonical components and incremental implementation options. Its recommendation to package the system as exactly two skills is not authoritative; `review-plan` is now defined as a harness of agent-backed workers, deterministic gates, records, policies, and adapters.

## Recommendation

Build two canonical skills:

1. `review-plan` — one reusable review procedure with selectable reviewer modes.
2. `adjudicate-plan-reviews` — a separate procedure for validating, reconciling, and dispositioning findings.

Execute each selected reviewer mode in a fresh, isolated agent context. Use deterministic scripts for schemas, validation, evidence collection, and rendering. The distinction is:

- A **skill** stores the canonical, versioned procedure and rubric.
- An **agent** supplies an isolated context, model judgment, and constrained permissions.
- A **script** enforces objective rules and stable output formats.

Do not create a separate skill for every reviewer. Keep the shared workflow in `review-plan` and put each lens in a progressively loaded reference file.

## Core reviewer set

### 1. Independent outcome audit

Use as the baseline review for every material plan.

- Read the originating requirement before the plan.
- Form independent success criteria before seeing the plan's framing.
- Compare the written plan against those criteria.
- Remain cold: no drafter discussion or prior review findings.
- Permit an unqualified `ACHIEVES GOAL` verdict when warranted.
- Do not inspect the repository unless the review manifest authorizes it.

This catches goal drift, omitted requirements, unjustified scope, and plans whose own checkpoints can pass while the ticket remains unsolved.

### 2. Grounded feasibility and verification review

Use for plans that change code, configuration, infrastructure, data, integrations, or operational behavior.

- Inspect the authorized repository and documentation read-only.
- Verify that named components, APIs, dependencies, and assumptions exist.
- Identify missed change surfaces and integration points.
- Judge whether tests and checkpoints establish the claimed outcome.
- Separate current evidence from inference and unresolved questions.

This combines repository grounding and testability because both depend on the same implementation evidence. It complements rather than duplicates the cold outcome audit.

### 3. Adversarial falsification review

Use for medium- and high-risk plans, or when failure could remain hidden behind passing checkpoints.

- Construct concrete ways a competent engineer could execute the plan exactly as written, pass its tests, and still miss the intended outcome.
- Attack assumptions, sequencing, boundaries, failure handling, rollback, observability, and acceptance evidence.
- Report only plausible failure paths tied to the plan and source requirements.
- Do not invent stylistic objections or propose a preferred architecture.

### 4. Triggered specialist risk reviews

Initially build only the three specialist modules that cover the broadest consequential risks:

#### Data and migration

Trigger for schema changes, migrations, backfills, retention, destructive writes, consistency changes, or large data movement. Review compatibility, invariants, recovery, rehearsal, validation, and rollback.

#### Security and trust boundaries

Trigger for authentication, authorization, secrets, sensitive data, untrusted input, public interfaces, tenancy, cryptography, or privilege changes. Review threats, abuse paths, boundary enforcement, failure modes, and verification.

#### Operational readiness

Trigger for deployments, infrastructure, distributed behavior, third-party dependencies, availability, performance-sensitive paths, or high-blast-radius changes. Review rollout, rollback, observability, capacity, degradation, incident response, and operator evidence.

Treat these as references or modes under `review-plan`, not standalone skills. The classifier may select more than one for a plan.

### 5. Finding adjudicator

Use whenever two or more reviews produce findings. Run it as a separate skill in a fresh, strong-agent context.

- Read the original requirement and plan before reading reviewer conclusions.
- Validate each finding against primary evidence.
- Merge duplicates without erasing distinct failure mechanisms.
- Reject unsupported, out-of-scope, or merely stylistic findings.
- Resolve conflicts by evidence, not reviewer count or confidence language.
- Produce a disposition ledger: accept, reject, defer, or needs clarification.
- Identify the minimum required plan changes and re-review triggers.

The adjudicator should not be the original drafter and should not use majority vote as a truth mechanism.

## Final re-review

Final re-review is a mode, not a new reviewer type. Run it after material findings have been folded into the plan.

- Re-run the independent outcome audit on the complete revised plan.
- Re-run every specialist mode affected by the revision.
- Run the classifier again in diff-time mode so new risks introduced by remediation are routed correctly.
- Confirm that accepted findings were actually resolved and that the revised plan remains internally coherent.

Skip this only for immaterial edits that cannot affect scope, behavior, risk, sequencing, or verification.

## Proposed packaging

```text
select-plan-reviews/
└── classifier and dispatch policy

review-plan/
├── SKILL.md
├── references/
│   ├── outcome.md
│   ├── grounding-and-verification.md
│   ├── falsification.md
│   ├── risk-data-migration.md
│   ├── risk-security.md
│   ├── risk-operational-readiness.md
│   ├── final-rereview.md
│   └── finding-schema.md
└── scripts/
    ├── collect-repository-evidence
    └── validate-findings

adjudicate-plan-reviews/
├── SKILL.md
├── references/
│   ├── disposition-policy.md
│   └── finding-ledger-schema.md
└── scripts/
    ├── normalize-findings
    └── validate-ledger
```

Create thin Claude and Codex adapters around the same canonical core. Adapters should translate invocation, isolation, permissions, and output plumbing without changing reviewer semantics.

## Classifier-to-reviewer routing

| Classifier output | Execution |
|---|---|
| Independent outcome | `review-plan` with `outcome` mode in a cold agent |
| Grounded feasibility | `review-plan` with `grounding-and-verification` mode and authorized read-only evidence |
| Verification quality | Included in `grounding-and-verification` |
| Adversarial falsification | `review-plan` with `falsification` mode in a separate cold agent |
| Data or migration risk | `review-plan` with `risk-data-migration` |
| Security or trust-boundary risk | `review-plan` with `risk-security` |
| Operational risk | `review-plan` with `risk-operational-readiness` |
| Two or more completed reviews | Always run `adjudicate-plan-reviews` separately |
| Materially revised plan | Re-run `outcome`, affected modes, and diff-time classification |

The semantic classifier may add reviews but must not remove reviews required by deterministic policy.

## Build order

1. Common finding and evidence schema.
2. Independent outcome audit mode.
3. Grounded feasibility and verification mode.
4. Finding adjudicator.
5. Adversarial falsification mode.
6. Data and migration specialist mode.
7. Security and trust-boundary specialist mode.
8. Operational readiness specialist mode.
9. Final re-review mode and diff-time routing.

This sequence establishes a useful minimum system after step 4, then adds higher-cost reviews in descending order of general value.

## Deliberate consolidations

- Fold requirements traceability into the independent outcome audit.
- Fold testability and checkpoint adequacy into grounded feasibility.
- Evaluate sequencing within falsification and relevant specialist reviews.
- Treat final re-review as a mode applied to the revised artifact.
- Add narrower domain specialists only when classifier evidence and evaluation data show repeated misses.

## Minimum viable review stack

For a normal material engineering plan:

1. Classify the plan.
2. Run the cold independent outcome audit.
3. Run grounded feasibility and verification.
4. Add only triggered falsification or specialist modes.
5. Adjudicate findings in a separate context.
6. Revise the plan.
7. Reclassify and re-review the final plan after material changes.

This is the smallest set on which the research converged: broad outcome coverage, real-world grounding, adversarial challenge when warranted, specialist depth for high-risk surfaces, independent adjudication, and closure after revision.
