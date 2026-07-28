# Incremental implementation options before orchestration

## Goal

Build and prove the eight canonical review components in small, useful increments before committing to either orchestration architecture or an automatic audit/repair loop.

The controller-centric and composable-command plans remain future orchestration options. The early implementation should produce shared workers and canonical records that either design can invoke.

## Recommendation

Start with a manually advanced, audit-only vertical slice. Add adjudication, human decisions, manual repair, and exact-artifact closure one capability at a time. Do not automate convergence until the same lifecycle works reliably through explicit invocations.

## Option 1: manual stage commands

Build small commands that a human invokes in order:

```text
freeze → classify → review → adjudicate → report
```

Later:

```text
repair → validate → final-review → close
```

This is the recommended starting option because every stage is inspectable and no orchestration design is required.

## Option 2: thin sequential runner

Build the same workers, then add a small runner that executes one fixed path without loops or dynamic graph behavior.

It may stop at:

- `revision-required`;
- `waiting-for-human`;
- `blocked`;
- `approved`.

A human explicitly starts the next revision/re-review run.

This provides convenience while keeping lifecycle behavior easy to debug.

## Option 3: interface-first dual compatibility

Define one shared worker interface before implementing either runner:

```text
execute(canonical request) → canonical record
```

Implement every classifier, reviewer, adjudicator, and validator behind that interface. Both future designs can reuse the workers:

- the controller-centric implementation calls them from its lifecycle engine;
- the composable pipeline invokes them as typed commands.

This requires slightly more interface work initially but avoids coupling workers to one orchestrator.

## Increment 1: canonical records and integrity

Implement:

- component 1 finding and review-record schemas;
- component 2 source bundle and input contract;
- component 3 record-lineage and integrity rules;
- content hashing;
- schema and reference validation;
- immutable plan versions.

Exit when an exact source bundle and plan can be frozen, validated, and reproduced.

## Increment 2: one cold audit

Implement:

- a model registry;
- one provider adapter;
- fresh read-only execution;
- the independent outcome reviewer;
- canonical review and finding output.

The usable workflow is:

```text
freeze → cold audit → save result
```

Exit when the reviewer consistently binds the exact input artifacts and produces schema-valid records.

## Increment 3: classification and review portfolio

Implement component 3 routing:

- deterministic risk triggers;
- semantic classification;
- review manifest;
- grounded reviewer;
- adversarial reviewer;
- only the highest-value triggered specialists;
- multi-model assignments.

Exit when every selected lens has a keyed terminal execution or an explicit valid waiver placeholder.

## Increment 4: adjudication and ledger

Implement component 4:

- source-first adjudicator;
- confirmed, rejected, duplicate, needs-decision, and not-established dispositions;
- canonical finding/remediation ledger;
- coverage for failed and inconclusive required reviews.

Exit when raw reviewer conclusions no longer flow directly into repair.

## Increment 5: human decisions and policy

Implement the minimum component 7 path:

- decision request;
- authority lookup;
- HITL pause/resume;
- residual-risk and review-waiver records;
- deny-by-default behavior.

Exit when unresolved intent, authority, or risk cannot be silently converted into approval.

## Increment 6: manual repair and final closure

Implement component 5 plus a bounded repair worker:

- repair from confirmed ledger items;
- new immutable plan version;
- resolution map;
- deterministic checks;
- semantic-diff classification;
- affected-lens re-review;
- holistic final review;
- exact-plan-hash closure.

Do not loop automatically. If closure returns `revision-required`, stop and require another explicit invocation.

Exit when a materially edited plan cannot inherit approval from its predecessor.

## Increment 7: evaluation and drift

Grow component 6 alongside earlier increments, then complete:

- clean and seeded cases;
- historical misses;
- deterministic graders;
- model/adapter equivalence;
- false-block and abstention cases;
- usage and lifecycle invariant tests;
- promotion and rollback policy.

Exit when every allowed reviewer × model × adapter combination is evaluated for its assigned role.

## Increment 8: implementation feedback

Implement component 8 after plan closure is reliable:

- implementation conformance;
- diff-time classification;
- release-gate records;
- observation and feedback events;
- learning actions.

Exit when escaped defects and false positives can become evaluation cases and controlled component changes.

## Orchestration decision point

Only after increments 1–6 work manually, choose an orchestration design:

- [`controller-centric`](controller-centric/implementation-plan.md) for stronger centralized lifecycle and policy enforcement;
- [`composable skill-command pipeline`](composable-skill-pipeline/implementation-plan.md) for modular commands and declarative composition.

The choice should not require rewriting the canonical records or bounded workers.

## Optional final increment: bounded convergence

After manual closure is dependable, add:

- automatic repair/re-review edges;
- usage and round limits;
- protected final-closure budget;
- non-convergence diagnosis;
- model-tier escalation;
- HITL after exhaustion.

Automatic orchestration is a convenience layer. Exact-artifact re-review remains mandatory whether iteration is manual or automatic.
