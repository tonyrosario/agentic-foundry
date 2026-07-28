# Design B: composable skill-command pipeline

## Design

Package every review-lifecycle capability as a command-like skill with a strict structured input/output contract. Connect these skills through a generic durable workflow runner using Unix-style composition: filters transform immutable records, fan-out nodes run reviewers in parallel, join nodes adjudicate, conditional nodes route repair and HITL, and loop edges continue until exact-artifact closure or a hard stop.

```text
freeze
  | classify
  | fan-out(review assignments)
  | adjudicate
  | repair?
  | validate
  | reroute
  | final-close
```

The workflow runner owns generic mechanics—dependency resolution, persistence, retries, budgets, branches, loops, and parallel joins. Individual command skills own stage semantics. The pipeline passes artifact references and canonical records, not conversational context.

## Why this design

This design prioritizes composability, replaceability, local experimentation, and rapid evolution. It is appropriate when the review system should feel like a toolkit whose stages can be invoked independently or rearranged declaratively.

Its main advantages are:

- every skill can be developed, tested, versioned, and replaced independently;
- new specialist reviewers become new commands rather than controller code;
- Claude, Codex, and model-profile changes occur behind command adapters;
- the pipeline graph is visible as configuration;
- individual stages are easy to replay on frozen artifacts;
- local CLI and CI use are natural;
- small teams can implement it incrementally.

The cost is that correctness depends heavily on the common command contract and workflow runner. Without strict schemas, artifact identity, permissions, and durable state, “Unix style” can degrade into piping unvalidated prose through one shared agent context.

## Intended use

Choose this design when:

- reviewer portfolios change frequently;
- teams want to author new specialist skills independently;
- local file-based execution is the initial target;
- stages should be individually runnable for debugging;
- declarative workflow configuration is preferred;
- a generic workflow runner already exists or is acceptable;
- centralized lifecycle policy can be expressed as reusable gates.

Do not use literal shell pipes as the production control plane for material work. The design adopts Unix component principles but adds durable graph execution.

## The central principle

> Pipe records, not conversations.

Every stage consumes a canonical envelope and produces a canonical envelope. Large documents remain in a content-addressed artifact store and flow by ID/version/hash reference.

Skills must not depend on hidden upstream chat history. Cold reviewers start fresh even though their records are connected in the workflow.

## Skill-command interface

Every command implements:

```text
validate(input_envelope)
execute(input_envelope, runtime_context)
emit(output_envelope)
```

The envelope contains:

```yaml
envelope_schema_version: "1.0"
operation_id: "op-..."
lifecycle_id: "life-..."
attempt_id: "attempt-..."

command:
  id: "independent-outcome-audit"
  version: "..."

input_contract:
  id: "review-input-..."
  schema_version: "1.0"
  sha256: "..."

artifact_inputs:
  - record_type: "candidate-plan"
    record_id: "plan-..."
    logical_record_version: "..."
    schema_version: "1.0"
    record_sha256: "..."
    role: "review-target"

execution:
  model_profile: "sol-high"
  adapter_version: "..."
  workspace_mode: "isolated-read-only"
  allowed_tools: []

output_contract:
  record_type: "review-record"
  schema_version: "1.0"

budget:
  maximum_input_tokens: null
  maximum_output_tokens: null
  timeout_seconds: null
```

Output:

```yaml
envelope_schema_version: "1.0"
operation_id: "op-..."
lifecycle_id: "life-..."
attempt_id: "attempt-..."

execution_status: "completed" # completed | infrastructure-failed | invalid-output
semantic_result: "established" # established | not-established | failed

artifacts:
  - record_type: "review-record"
    record_id: "rev-..."
    record_sub_id: "revexec-..."
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."

provenance:
  requested_model_profile: "sol-high"
  provider_attested_model: null
  adapter_version: "..."
  tools_used: []
  context_mode: "fresh"

usage:
  input_tokens: null
  output_tokens: null
  cost_units: null
  latency_ms: null

diagnostics: []
```

Semantic blockers are successful command executions. Process or adapter failure is separate from the review conclusion.

## Command catalog

### Artifact commands

- `freeze-source`
- `freeze-plan`
- `build-input-contract`
- `hash-artifact`
- `validate-record`

### Routing commands

- `apply-deterministic-triggers`
- `classify-plan`
- `select-review-suite`
- `resolve-model-profile`
- `classify-semantic-diff`
- `select-rereviews`

### Reviewer commands

- `independent-outcome-audit`
- `grounded-feasibility-review`
- `adversarial-falsification-review`
- `database-review`
- `security-review`
- `privacy-review`
- `operations-review`
- `compatibility-review`
- `domain-policy-review`

### Judgment commands

- `adjudicate-findings`
- `request-human-decision`
- `validate-waiver`
- `evaluate-final-closure`

### Mutation commands

- `repair-plan`

This should be the only ordinary plan-mutation command. It writes a new candidate version.

### Verification commands

- `run-deterministic-checks`
- `verify-resolution-map`
- `verify-semantic-no-change`
- `verify-exact-artifact`

## Command behavior rules

Every command must:

- have one bounded responsibility;
- accept only declared canonical inputs;
- emit schema-valid outputs;
- record its version;
- record execution and model provenance;
- declare required permissions;
- declare side effects;
- be idempotent or provide a unique attempt identity;
- return `not-established` rather than invent missing facts;
- avoid decisions owned by another command;
- remain independently evaluable.

Reviewer commands are read-only. Adjudication does not repair. Repair does not adjudicate. Closure does not grant waivers.

## Artifact transport

Do not stream entire plans and source bundles through stdout between commands. Store immutable artifacts and pipe references:

```text
artifact://life-.../plan/plan-v003@sha256:...
record://life-.../review/rev-.../revexec-...@sha256:...
```

The URI syntax is illustrative. The actual reference must carry:

- record type;
- full identity;
- schema version;
- logical record version where defined;
- hash;
- lifecycle;
- role.

The runner resolves and verifies each reference before command execution.

Use stdout or an API result only for the output envelope. Use stderr or a separate log stream for human-readable diagnostics. Never require a downstream parser to scrape Markdown to find the canonical result.

## Declarative pipeline

An implementation pipeline can be:

```yaml
pipeline:
  id: "plan-review-to-convergence"
  version: "1.0"

nodes:
  freeze:
    command: "freeze-review-input"

  classify:
    command: "classify-plan"
    needs: ["freeze"]

  build_manifest:
    command: "select-review-suite"
    needs: ["classify"]

  reviews:
    foreach: "$build_manifest.assignments"
    command: "$item.reviewer_command"
    model_profile: "$item.resolved_model_profile"
    needs: ["build_manifest"]
    parallel: true
    workspace: "fresh-read-only"

  adjudicate:
    command: "adjudicate-findings"
    needs: ["reviews"]
    read_order:
      - "source"
      - "plan"
      - "independent-assessment"
      - "review-findings"

  human_decision:
    command: "request-human-decision"
    needs: ["adjudicate"]
    when: "$adjudicate.needs_human_decision"
    pause: true

  repair:
    command: "repair-plan"
    needs: ["adjudicate", "human_decision?"]
    when: "$adjudicate.has_confirmed_open_findings"
    workspace: "bounded-write"

  deterministic_checks:
    command: "run-deterministic-checks"
    needs: ["repair?"]

  diff:
    command: "classify-semantic-diff"
    needs: ["repair?"]

  rereviews:
    foreach: "$diff.required_rereviews"
    command: "$item.reviewer_command"
    model_profile: "$item.resolved_model_profile"
    needs: ["deterministic_checks", "diff"]
    parallel: true

  final_review:
    command: "independent-outcome-audit"
    mode: "final-holistic"
    needs: ["rereviews", "deterministic_checks"]

  closure:
    command: "evaluate-final-closure"
    needs: ["final_review", "adjudicate", "deterministic_checks"]

edges:
  - from: "closure"
    to: "repair"
    when: "$closure.result == 'revision-required'"

limits:
  maximum_material_rounds: 4
  on_exhaustion: "pause-for-human"
```

The runner validates the graph before execution:

- no command can consume a record type it does not declare;
- only authorized mutation nodes can write;
- final closure must exist;
- every repair loop returns through deterministic validation and final review;
- loop limits cannot resolve to approval;
- every fan-out has an identity-safe join.

## Generic workflow runner

The runner is not plan-review-specific. It supplies:

- dependency scheduling;
- fan-out and join;
- conditional nodes;
- loops with hard bounds;
- checkpoints;
- retries;
- timeouts and cancellation;
- usage accumulation;
- human pause/resume;
- artifact resolution;
- schema validation;
- provenance capture.

Review-specific behavior remains in commands and pipeline policy.

An initial implementation can be a local CLI:

```text
skillpipe run pipeline.yaml --input intake.yaml
skillpipe status life-...
skillpipe resume life-... --decision decision.yaml
skillpipe replay life-... --node database-review
skillpipe inspect life-... --node adjudicate
```

## Pipeline execution algorithm

```text
load and validate pipeline
create or resume lifecycle

while runnable nodes exist:
    select nodes whose dependencies are complete
    apply branch and loop conditions
    check permissions and usage reserve
    resolve model profiles
    execute independent nodes concurrently
    validate output envelopes
    persist artifacts and node state
    update usage

    if a human node is reached:
        checkpoint and pause

    if a loop limit is reached:
        block or request authority

evaluate closure only when all required dependencies are current
approve only the exact unchanged artifact hash
```

## Multi-model invocation

The command identifies reviewer semantics; `model_profile` identifies execution capability.

```text
skillpipe invoke independent-outcome-audit \
  --contract review-input.json \
  --model-profile terra-medium

skillpipe invoke independent-outcome-audit \
  --contract review-input.json \
  --model-profile sol-high

skillpipe invoke independent-outcome-audit \
  --contract review-input.json \
  --model-profile opus-1m-high
```

These are new executions with distinct execution IDs. They may share an immutable input contract when comparing model behavior, but closure after repair requires a new contract bound to the new plan hash.

### Adapter command

The runner invokes:

```text
provider-adapter execute \
  --profile sol-high \
  --command independent-outcome-audit \
  --input-envelope input.json \
  --output-envelope output.json
```

The actual adapter may be an API client, CLI wrapper, or host-native agent invocation.

## Model registry

Use the same deployment-owned registry as Design A:

```yaml
profiles:
  terra-medium:
    provider: "codex"
    model: "gpt-5.6-terra"
    effort: "medium"
  terra-high:
    provider: "codex"
    model: "gpt-5.6-terra"
    effort: "high"
  sol-medium:
    provider: "codex"
    model: "gpt-5.6-sol"
    effort: "medium"
  sol-high:
    provider: "codex"
    model: "gpt-5.6-sol"
    effort: "high"
  opus-high:
    provider: "claude"
    model: "opus-4.8"
    effort: "high"
  opus-1m-high:
    provider: "claude"
    model: "opus-4.8"
    effort: "high"
    context: "extended-1m"
```

Eligibility is based on locally evaluated reviewer × model × adapter combinations.

## Parallel fan-out and safe join

The `reviews` node behaves like a typed, durable form of `xargs -P`:

1. Read assignments from the manifest.
2. Create one operation and execution ID per assignment.
3. Create separate workspaces.
4. Dispatch across eligible providers.
5. Persist each terminal result independently.
6. Join by `(review_id, review_execution_id, schema_version, hash)`.
7. Send the complete set to adjudication.

Never join by output order. Never drop a failed or inconclusive required execution.

## Information-flow isolation

Pipeline dependencies do not imply conversational inheritance.

For cold review nodes:

- instantiate a new execution;
- provide source before plan;
- exclude upstream logs and conclusions;
- allow only declared artifact references;
- make the workspace read-only;
- record ambient repository instructions;
- preserve raw output separately.

For adjudication:

- first expose source and plan;
- require an independent assessment artifact;
- then disclose raw findings.

For repair:

- expose the canonical ledger, not unfiltered reviewer debate.

## Side-effect policy

Commands declare:

```yaml
side_effects:
  filesystem: "none" # none | candidate-write | controlled-mutation
  external_network: false
  production_action: false
```

The runner enforces:

- review, classification, adjudication, and closure: no writes;
- repair: write a new candidate version only;
- no command may mutate the reviewed source or predecessor plan;
- no review pipeline command performs production operations;
- external access requires an input-contract grant.

## Usage-gate command

Usage enforcement can be expressed as a mandatory runner gate rather than a model-backed skill:

```yaml
usage_policy:
  base_material_rounds_before_diagnosis: 2
  promoted_holistic_executions: 2
  absolute_material_round_limit: 4
  protected:
    adjudication: 1
    final_closure: 1
  approval_on_exhaustion: false
```

Before each node:

```text
usage-gate
  | if within budget: execute node
  | if soft limit: checkpoint and diagnose
  | if authorization required: pause
  | if hard limit: block
```

The runner, not an LLM command, performs arithmetic and hard enforcement.

## Tier escalation as graph routing

After `N` material rounds:

```yaml
nonconvergence_diagnosis:
  command: "diagnose-nonconvergence"
  needs: ["adjudicate"]
  when: "$usage.material_rounds >= $policy.N"

promoted_review:
  command: "independent-outcome-audit"
  model_profile: "$nonconvergence_diagnosis.promoted_profile"
  needs: ["nonconvergence_diagnosis"]
  when: "$nonconvergence_diagnosis.auto_promote"
```

Only capability-limited integration, context-capacity failure, or repeated confirmed new cross-cutting findings can set `auto_promote`.

These route to HITL instead:

- ambiguous source;
- missing evidence;
- repeated unfixed finding;
- risk decision;
- noisy reviewer;
- material redesign.

Reserve one of `M` promoted executions for exact-artifact closure.

## HITL command

`request-human-decision` is a blocking command with no inferred output:

```yaml
status: "waiting"
decision_request_id: "dec-request-..."
required_authority: "..."
default_if_unanswered: "remain-blocked"
```

The runner checkpoints the graph. An authorized response creates a new immutable decision artifact and satisfies the node. The same lifecycle then resumes.

## Repair loop

The repair loop is:

```text
canonical ledger
  | repair-plan
  | freeze-new-plan
  | deterministic-checks
  | classify-semantic-diff
  | affected-rereviews
  | holistic-final-review
  | adjudicate-new-findings
  | closure
```

If closure requires revision, the loop returns to `repair-plan` with a new ledger version. The loop limit counts material repair cycles, not every parallel reviewer command.

## Final closure

Closure receives only hash-bound records:

- final source bundle;
- final plan;
- active manifest;
- review records;
- current ledger;
- decisions and waivers;
- deterministic checks;
- re-review records;
- holistic final review;
- usage status.

It checks the same canonical gates as Design A. The workflow configuration cannot omit final closure; the runner rejects such a pipeline as invalid for approval-producing mode.

## Failure behavior

### Command process failure

- Mark the attempt infrastructure-failed.
- Retry under a new attempt/execution ID if policy allows.
- Do not reinterpret it as a semantic result.

### Schema-invalid output

- Reject the output.
- Preserve raw response and diagnostics.
- Treat the required command as incomplete.

### Semantic `not-established`

- Treat execution as complete.
- Route the result to the ledger.
- Do not retry until favorable.

### Runner interruption

- Reload persisted node states and artifact references.
- Verify hashes.
- Schedule only incomplete or invalidated nodes.

### Artifact change

- Invalidate downstream nodes that consumed the predecessor hash.
- Issue a new contract.
- Re-run affected graph paths.

### Budget exhaustion

- Checkpoint.
- Block or wait for authorized expansion.
- Never execute the approval edge.

## Local implementation layout

```text
skillpipe/
  runner/
    graph
    scheduler
    conditions
    loops
    checkpoints
    usage
  contracts/
    envelope.schema.json
    command.schema.json
    pipeline.schema.json
  artifacts/
    store
    hashing
    references
  adapters/
    codex
    claude
  commands/
    freeze-review-input/
    classify-plan/
    independent-outcome-audit/
    grounded-review/
    adjudicate-findings/
    repair-plan/
    deterministic-checks/
    final-closure/
  pipelines/
    plan-review-to-convergence.yaml
  evaluations/
```

Each command folder may contain a skill, references, scripts, schemas, and adapter-specific entry points.

## Implementation sequence

### Phase 1: command contract and linear pipeline

1. Define the input/output envelope.
2. Implement artifact storage and hashing.
3. Wrap `freeze`, `classify`, one reviewer, adjudicate, repair, and closure as commands.
4. Implement a linear runner with checkpoints.
5. Add Claude and Codex adapters.
6. Validate every command output.

### Phase 2: graph behavior

1. Add `foreach` fan-out and keyed join.
2. Add conditional nodes.
3. Add bounded repair loops.
4. Add human pause/resume.
5. Add usage gates and protected closure reserve.
6. Add semantic-diff re-routing.

### Phase 3: production hardening

1. Add atomic node-state updates.
2. Add permission enforcement and isolated workspaces.
3. Add authority and waiver commands.
4. Add evaluated fallbacks.
5. Add CI integration, observability, and drift evaluation.

## Verification strategy

Test every command in isolation:

- valid input to valid output;
- invalid reference rejection;
- permission boundary;
- schema failure;
- `not-established`;
- model and adapter provenance;
- deterministic replay where applicable.

Test the runner:

- fan-out/join identity;
- no array-position joins;
- failed required command remains visible;
- loop counters;
- usage reserve;
- pause/resume;
- invalidation after artifact change;
- no closure without current required nodes;
- budget exhaustion never follows approval edge.

Test whole pipelines with clean plans and seeded failure cases.

## Trade-offs

### Strengths

- Highly modular and replaceable.
- Easy to add specialist commands.
- Pipeline configuration makes composition visible.
- Individual stages can be replayed and debugged.
- Natural local CLI and CI ergonomics.
- Generic runner can support workflows beyond plan review.

### Costs

- Strong schemas and a capable runner are mandatory.
- Policy can become scattered across commands and graph configuration.
- More artifact-envelope plumbing.
- Dynamic graphs and invalidation are harder than a literal pipe suggests.
- Poorly designed commands can leak context or hide side effects.
- Generic runner errors may be less domain-obvious than controller-specific errors.

## Decision summary

Use the composable command architecture when rapid evolution and independent skill development are primary. Keep the Unix philosophy but not the unsafe literalism:

> Each skill does one job; the runner owns pipes, state, limits, and recovery.
