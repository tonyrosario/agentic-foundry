# Design A: controller-centric review orchestrator

## Design

Build a purpose-specific deterministic controller that owns the complete review lifecycle. A thin operator skill accepts the user’s request and invokes the controller. The controller freezes artifacts, classifies the plan, selects and dispatches model-backed reviewer skills, adjudicates findings, pauses for human decisions, invokes a bounded reviser, enforces usage budgets, and approves only the exact final artifact that passes closure.

```text
user
  ↓
thin review-to-convergence skill
  ↓
purpose-built deterministic controller
  ├── artifact and lifecycle store
  ├── classifier and review selector
  ├── model registry and provider adapters
  ├── budget and authority policy
  ├── reviewer dispatch
  ├── adjudication
  ├── repair and deterministic validation
  └── exact-artifact final closure
```

The controller is the control plane. Skills are bounded cognitive workers. Agents can recommend outcomes, but deterministic policy authorizes state transitions.

## Why this design

This design prioritizes governance, integrity, and resumability. It is appropriate when review-to-convergence will become a durable system used across repositories, providers, risk tiers, and human approval boundaries.

Its main advantages are:

- one authoritative lifecycle state machine;
- centralized enforcement of plan hashes, record lineage, budgets, retries, permissions, waivers, and closure;
- straightforward recovery after interruption;
- consistent behavior across Claude, Codex, and future adapters;
- strong prevention of self-review, context leakage, silent model downgrade, and approval by exhaustion;
- one place to implement observability, policy, and audit retention.

The cost is a thicker controller with more purpose-built code. Adding or rearranging stages usually requires a controller change rather than only editing a pipeline file.

## Intended use

Choose this design when:

- reviews govern material or high-risk engineering work;
- exact artifact identity and authority matter;
- workflows must pause and resume around HITL decisions;
- multiple repositories or teams need consistent policy;
- model usage must be budgeted centrally;
- lifecycle records must survive process or provider failures;
- the system will later connect plan review to implementation, release, and observed outcomes.

For an occasional local review experiment, this architecture may be more infrastructure than necessary.

## System boundaries

### The operator skill

The user-facing skill is deliberately thin. It:

- gathers the source documents, plan, repository, and policy selection;
- validates that mandatory intake fields exist;
- calls the controller;
- presents progress, decisions, and final results;
- never performs the audit, repair, adjudication, or approval itself.

It must not retain conversational context and pass it to cold reviewers unless the input contract explicitly permits that context.

### The deterministic controller

The controller owns:

- lifecycle and operation IDs;
- immutable plan and source versions;
- content hashing and reference validation;
- legal state transitions;
- classifier invocation and deterministic trigger precedence;
- review-manifest generation;
- model-profile resolution;
- execution dispatch and retry identity;
- parallel review collection;
- adjudication ordering;
- confirmed-finding ledger state;
- human-decision waits;
- repair authorization;
- semantic-diff routing;
- usage and escalation gates;
- final closure.

### Agent-backed skills

Use separate versioned skills for:

- plan classification;
- independent outcome audit;
- repository grounding and verification;
- adversarial falsification;
- database/data review;
- security/privacy review;
- reliability/operations review;
- compatibility/API review;
- finding adjudication;
- bounded plan repair;
- semantic-diff classification;
- final holistic review.

Each skill receives an immutable role-specific contract and emits a canonical structured record.

### Provider adapters

Provider adapters translate canonical executions into Claude, Codex, or another runtime. They may implement:

- model and effort selection;
- workspace and sandbox creation;
- tool declaration;
- timeout and cancellation;
- structured-output capture;
- provider response metadata;
- usage collection.

They may not change reviewer semantics, severity definitions, read order, artifact scope, or authority.

## Major components

```text
review-controller/
  api/
    cli
    operator-skill-bridge
  lifecycle/
    state-machine
    transition-validator
    append-only-record-store
  artifacts/
    source-bundle
    plan-versioning
    hashing
    content-addressed-store
  policy/
    risk-triggers
    lens-selection
    usage-governor
    authority-and-waivers
    convergence-policy
  execution/
    scheduler
    provider-adapters
    model-registry
    workspace-isolation
    retries
  review/
    manifest-builder
    result-validator
    adjudication-router
    ledger
  repair/
    reviser-dispatch
    deterministic-checks
    semantic-diff
  closure/
    affected-lens-reroute
    final-review
    exact-artifact-gate
  evaluation/
    seeded-cases
    adapter-equivalence
    drift-monitoring
```

These may initially be modules in one local program rather than separate services.

## Canonical state flow

Use the [canonical lifecycle state machine](../../canonical/components/03-review-run-orchestrator/lifecycle-state-machine.md). The controller’s plan-review path is:

```text
draft
  ↓
input-frozen
  ↓
classified
  ↓
reviews-running
  ↓
reviews-complete
  ↓
adjudication-running
  ├── revision-required ──→ input-frozen
  ├── blocked
  └── final-review-ready
          ↓
     final-review-running
          ├── revision-required
          ├── blocked
          ├── plan-approved
          └── plan-approved-with-residual-risk
```

Every transition consumes verified canonical records. Agent prose cannot change lifecycle state.

## Persistent record model

The minimum records are:

- authoritative source bundle;
- input contract;
- classification record;
- review manifest;
- raw review records;
- raw finding records;
- canonical finding ledger;
- human decision and waiver records;
- plan version and semantic diff;
- deterministic check results;
- final closure record;
- lifecycle state records;
- usage and execution provenance.

Store logical ID, schema version, record version where applicable, lifecycle ID, and content hash. Join records by complete keyed references, never filename, display name, “latest,” or array position.

An initial local layout can be:

```text
runs/
  life-.../
    lifecycle/
    source/
    plans/
    contracts/
    classifications/
    manifests/
    reviews/
    findings/
    ledgers/
    decisions/
    waivers/
    repairs/
    checks/
    closures/
    traces/
```

## Controller interface

A minimum CLI could be:

```text
reviewctl start --source source-bundle.yaml --plan plan.md --policy standard
reviewctl status --lifecycle life-...
reviewctl decide --lifecycle life-... --decision decision.yaml
reviewctl resume --lifecycle life-...
reviewctl cancel --lifecycle life-...
reviewctl inspect --lifecycle life-... --record finding-ledger
```

The operator skill wraps these actions and renders concise user-facing summaries.

## Intake implementation

`reviewctl start` should:

1. Resolve every authoritative source and inherited plan document.
2. Apply explicit precedence rules.
3. Reject ambiguous delta-plan inheritance.
4. Reserve a lifecycle ID.
5. Freeze the first input contract.
6. Create the genesis lifecycle state bound to that contract.
7. Compute source and plan hashes.
8. Record repository revision and dirty state.
9. Select policy and lens-catalog versions.
10. Advance only after deterministic validation succeeds.

The controller should never let a mutable pathname stand in for the reviewed plan.

## Classification and review selection

Run deterministic triggers first. Examples include:

- database schema or migration;
- authentication or authorization;
- personal or regulated data;
- payments or financial state;
- public API or compatibility boundary;
- production deletion or irreversible mutation;
- multi-service rollout;
- reliability/SLO impact;
- secrets, credentials, or supply chain.

Then invoke the semantic classifier for novelty, coupling, weak evidence, cross-document reasoning, reversibility, and likely specialist needs.

The result is a frozen review manifest containing:

- selected lenses;
- execution-required lenses;
- reviewer assignments;
- minimum capability and context profiles;
- tools and evidence access;
- isolation mode;
- human gates;
- re-review triggers;
- valid waivers.

Semantic classification may add reviews but cannot remove deterministic mandatory triggers.

## Multi-model dispatch

The scheduler resolves each assignment through a deployment-owned model registry.

Example profiles:

```yaml
profiles:
  terra-medium:
    adapter: "codex"
    model: "gpt-5.6-terra"
    effort: "medium"
  terra-high:
    adapter: "codex"
    model: "gpt-5.6-terra"
    effort: "high"
  sol-medium:
    adapter: "codex"
    model: "gpt-5.6-sol"
    effort: "medium"
  sol-high:
    adapter: "codex"
    model: "gpt-5.6-sol"
    effort: "high"
  opus-high:
    adapter: "claude"
    model: "opus-4.8"
    effort: "high"
  opus-1m-high:
    adapter: "claude"
    model: "opus-4.8"
    effort: "high"
    context: "extended-1m"
```

Freeze the resolved profile in the manifest. The execution record must distinguish requested profile from provider-attested actual execution. Silent downgrade is invalid.

### Scheduling policy

- Run separable reviewers concurrently.
- Run adjudication only after required review executions reach terminal results.
- Limit concurrency per provider and lifecycle.
- Use a new execution ID for every retry.
- Retry only infrastructure failure.
- Preserve failed and `not-established` reviews for adjudication.

## Isolation

For each cold reviewer:

1. Create a fresh non-forked execution.
2. Mount only contract-authorized files.
3. Make the workspace read-only.
4. Load the source before the plan when independent criteria are required.
5. Exclude prior reviews and drafter rationale.
6. Record automatically loaded repository instructions and skills.
7. Destroy the ephemeral workspace after retaining outputs and traces.

The adjudicator independently reads source and plan before receiving review conclusions.

## Adjudication

The controller gives the adjudicator:

- authoritative source bundle;
- exact plan version;
- raw review and finding records;
- evidence attachments;
- policy and finding schema.

The adjudicator produces one canonical ledger with:

- confirmed;
- rejected;
- duplicate;
- needs decision;
- not established.

The controller validates that every raw finding and every required failed or inconclusive review maps to exactly one ledger item.

Material `needs decision` items create a component-7 decision request and pause the lifecycle. Silence does not resolve the request.

## Repair

Only confirmed and authorized ledger items enter the repair request.

The reviser receives:

- exact source and plan;
- canonical ledger;
- human decisions;
- allowed paths;
- mutation boundary;
- required checks.

It emits:

- a candidate new plan;
- a finding-resolution map;
- a summary of semantic changes;
- new assumptions or unknowns;
- any disputed item returned for adjudication.

The controller freezes the candidate as a new version. It never overwrites the approved or reviewed predecessor.

## Deterministic validation

Run available objective checks before semantic re-review:

- schema and duplicate-key checks;
- references and local links;
- required traceability fields;
- source/plan hash consistency;
- repository paths and symbols;
- compile, type, lint, and test commands;
- migration or policy validators;
- lifecycle and record-lineage checks;
- unresolved ledger checks;
- obsolete-field and vocabulary checks.

Objective failure returns to repair without spending a semantic closing review.

## Diff routing and re-review

Classify the change from the prior plan:

- editorial;
- clarification;
- verification change;
- scope or source change;
- interface/compatibility;
- data/migration;
- security/privacy;
- sequencing/dependency;
- rollout/rollback;
- cross-cutting rewrite.

Editorial changes receive semantic-no-change verification. Material changes re-run every affected lens plus one holistic final review.

## Usage governor

The controller enforces:

- total model executions;
- executions by capability tier;
- material repair rounds;
- input/output tokens;
- cost;
- wall-clock duration;
- provider concurrency;
- protected adjudication and final-closure reserve.

A practical default is:

```yaml
convergence:
  base_material_rounds_before_diagnosis: 2
  promoted_holistic_executions: 2
  absolute_material_round_limit: 4
  promoted_allocation:
    diagnosis: 1
    final_closure: 1
  on_exhaustion: "pause-for-human"
  approval_on_exhaustion: false
```

Before every dispatch:

```text
remaining budget
  - estimated pending execution
  - protected adjudication reserve
  - protected final-closure reserve
must remain nonnegative
```

After the configured base rounds, diagnose non-convergence. Automatically promote only capability or context failures. Source ambiguity, missing evidence, repeated failed repairs, risk decisions, and reviewer noise go to HITL or workflow correction.

## Final closure

The final closure gate verifies:

- all source criteria have dispositions;
- all mandatory lenses ran or have valid waivers;
- all failed or inconclusive reviews reached the ledger;
- all confirmed findings are fixed, blocking, or validly authorized;
- affected-lens re-reviews completed;
- deterministic checks pass;
- the holistic reviewer examined the complete current plan;
- no artifact changed after final review;
- every closing record binds the same plan hash.

Usage exhaustion, timeout, reviewer silence, or nominal reviewer agreement cannot produce approval.

## Failure and recovery

### Infrastructure failure

- Preserve the failed execution.
- Retry under a new execution ID when policy permits.
- Use an evaluated equivalent fallback only when capability, context, tools, isolation, and confidentiality match.

### Invalid agent output

- Reject before lifecycle progression.
- Record schema or provenance failure.
- Retry only if policy classifies it as execution failure, not until a favorable verdict appears.

### Controller interruption

- Reload the unique lifecycle head.
- Verify all record hashes.
- Resume the first incomplete legal operation.
- Never replay a completed mutation without idempotency or compare-and-swap protection.

### Budget exhaustion

- Stop dispatch.
- Preserve state and open findings.
- Request authorized budget, decomposition, model/portfolio change, or cancellation.
- Never approve.

## Human-in-the-loop integration

Create a decision packet with:

- one exact question;
- plan and source hashes;
- established facts, inferences, and unknowns;
- options and consequences;
- required authority;
- reviewer and adjudicator evidence;
- affected findings and lifecycle stages;
- default blocked behavior if unanswered.

After an authorized decision, create an append-only decision record and resume from the exact paused lifecycle head.

## Security model

- Reviewers are read-only.
- The reviser writes only to an explicit candidate location.
- Provider credentials stay in secret storage.
- Artifact projections follow least privilege.
- External network is denied unless contract-authorized.
- Tools and automatically loaded guidance are recorded.
- Agent output never directly performs production operations.
- Authority and waivers are verified against active policy records.

## Observability

Record:

- lifecycle state and age;
- execution queue and latency;
- requested and actual model profiles;
- usage by role, model, provider, and round;
- confirmed/rejected finding yield;
- repeated failure classes;
- rounds to closure;
- HITL wait time;
- final closure result;
- post-implementation escapes and false blockers.

Use historical results to improve routing and evaluate reviewer/model combinations.

## Implementation sequence

### Phase 1: local controller

1. Implement schemas and content hashing.
2. Implement lifecycle persistence and legal transitions.
3. Implement the model registry and Claude/Codex adapters.
4. Invoke existing reviewer prompts/skills in isolated workspaces.
5. Validate and persist canonical records.
6. Implement manual HITL resume.
7. Implement exact-artifact final closure.

### Phase 2: convergence automation

1. Add deterministic triggers and semantic classification.
2. Add parallel scheduling and adjudication.
3. Add bounded repair and diff routing.
4. Add usage governor and tier escalation.
5. Add resumability, retries, and fallback.
6. Add evaluation cases for known historical misses.

### Phase 3: organizational deployment

1. Add CI and repository integrations.
2. Add durable database/object storage.
3. Add authority matrix, decisions, and waivers.
4. Add dashboards and audit export.
5. Add implementation conformance and post-release feedback.

## Verification strategy

Test the controller independently of models:

- state-transition tests;
- stale-head and duplicate-successor tests;
- hash and schema substitution tests;
- retry identity tests;
- mandatory-lens preservation;
- usage-reserve enforcement;
- budget exhaustion never approves;
- HITL pause/resume;
- material edit invalidates prior closure;
- only the exact final hash can be approved.

Then test reviewer/model/adapter combinations with seeded and clean evaluation cases.

## Trade-offs

### Strengths

- Strongest integrity and policy enforcement.
- Best resumability and auditability.
- Clear operational ownership.
- Centralized provider, budget, authority, and security controls.
- Natural extension into implementation and release governance.

### Costs

- More purpose-built code.
- Controller changes are needed for many workflow changes.
- Larger initial schema and persistence investment.
- Risk of the controller becoming monolithic without module boundaries.

## Decision summary

Use the controller-centric architecture when correctness of the review lifecycle is itself a governed system requirement. It is the stronger long-term design for high-value, multi-model, resumable review-to-convergence. Its defining principle is:

> The controller owns state and authority; skills supply bounded cognition.
