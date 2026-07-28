# Automating audit, adjudication, repair, and convergence

## Short answer

Yes, most of the loop can be automated. The safe pattern is not “ask an agent to audit and fix until it says the plan is good.” It is a versioned workflow with separate roles, immutable inputs, deterministic gates, controlled information flow, and an explicit stopping rule:

```text
freeze source + plan
        ↓
classify risk and select reviews
        ↓
run cold reviewers
        ↓
independently adjudicate findings
        ↓
human decisions where required
        ↓
repair the exact plan
        ↓
run deterministic checks and classify the diff
        ↓
re-run affected reviews + holistic final review
        ↓
approve exact hash | repeat | block/escalate
```

The controller should be ordinary deterministic software. The classifier, reviewers, adjudicator, and reviser may be agent executions. Agents produce evidence and proposed changes; they do not decide for themselves that the lifecycle is complete.

This document describes an operational automation layer over the [eight canonical lifecycle components](../canonical/components/). It does not add a ninth review role.

## Why a naïve self-review loop is unsafe

A loop such as this is easy to build:

```text
while reviewer finds issues:
    ask planner to fix issues
```

It has several failure modes:

- The reviewer inherits the planner’s framing and repeats its blind spots.
- The reviewer’s finding is treated as true without evidence-based adjudication.
- False positives and architectural preferences become unauthorized scope.
- The planner silently changes the goal to make criticism easier to satisfy.
- A repair introduces a new defect, but only the old finding is checked.
- Repeated calls use the same model, prompt, evidence, and failure modes, creating the appearance of independent agreement.
- The system stops because an agent emits “clean,” not because all required gates passed.
- No exact artifact version is tied to the approval.
- The loop can continue indefinitely as reviewers discover progressively smaller editorial issues.

Automation must therefore separate discovery, judgment, mutation, and closure.

## The automation architecture

### 1. Deterministic lifecycle controller

Use a script, service, CI workflow, durable job runner, or state-machine engine as the controller. It should:

- allocate lifecycle, run, review, execution, finding, decision, and artifact IDs;
- compute and validate content hashes;
- enforce legal state transitions;
- issue immutable input contracts;
- dispatch the selected agent roles;
- prevent reviewers from writing to the plan;
- collect and schema-validate outputs;
- apply retry policy only to infrastructure failures;
- pause for required human decisions;
- invoke the reviser only with confirmed findings;
- run deterministic checks;
- decide whether a material edit requires re-review;
- approve only the exact artifact hash that passed final closure.

Do not make the controller another unconstrained conversational agent. An agent may recommend the next state, but deterministic policy should authorize the transition.

### 2. Classifier and review selector

Package the classifier as a versioned skill or prompt with a strict output schema. The controller invokes it against the frozen source bundle and plan metadata. Its output is a review manifest, not prose.

The classifier should identify:

- risk tier;
- changed systems and boundaries;
- data stores, migrations, retention, or destructive operations;
- authentication, authorization, privacy, secrets, and supply-chain exposure;
- public interfaces and compatibility commitments;
- production operations, deployment, observability, rollback, and incident surfaces;
- novelty, coupling, reversibility, blast radius, and evidence quality;
- required review lenses;
- required model/reasoning capability;
- required human gates;
- re-review triggers.

Deterministic triggers outrank semantic judgment. For example, a schema migration, auth-policy change, production deletion, or payment path should add its required specialist even if the classifier considers the plan simple.

### 3. Ephemeral reviewer agents

Reviewers are fresh executions of versioned reviewer skills. Each receives a role-specific projection of the same immutable input contract.

For a normal material plan, the default portfolio is:

1. A cold outcome reviewer that derives success criteria from the source before reading the plan.
2. A grounded feasibility and verification reviewer with read-only repository or authoritative-document access.
3. Triggered specialists, such as database/data, security/privacy, operations/reliability, API compatibility, or domain policy.
4. An adversarial falsification pass when the plan has complex sequencing, weak oracles, high-impact assumptions, or claims that can plausibly pass their own checkpoints while failing the outcome.

Reviewer agents should be read-only. They return immutable review records and findings in the [common finding schema](../canonical/components/01-common-finding-schema/finding-record.md). They must not edit the plan, close their own findings, accept risk, or expand their authority.

### 4. Independent adjudicator

The adjudicator separates useful criticism from confident noise. It should first read the source contract and plan and form its own view, then receive the raw findings.

For each finding it records:

- confirmed;
- rejected;
- duplicate;
- needs human decision;
- not established.

The adjudicator verifies the cited source requirement, plan location, concrete failure scenario, severity, and evidence. It merges only genuinely duplicate failure mechanisms. It must not decide product intent, grant exceptions, or accept consequential residual risk unless it is also the authorized human decision path.

For high-risk or subtle cross-system findings, use a high-capability model and the relevant human/domain owner. A low-cost model can normalize records and identify obvious duplicates, but should not be the final authority merely because it is a separate execution.

### 5. Reviser

The reviser is usually the original drafter because it retains plan-wide coherence. It receives:

- the exact current plan;
- the authoritative source bundle;
- the canonical adjudicated ledger;
- authorized human decisions;
- allowed files and mutation scope;
- required checks;
- a prohibition on changing source intent or accepting risk.

It should not receive rejected findings as instructions. It may receive them as non-authoritative context only when necessary to avoid repeating a misunderstanding.

The reviser creates a new immutable plan version and a resolution map from every confirmed finding to:

- fixed in the new version;
- rejected by authorized decision;
- accepted residual risk with authority;
- deferred with owner and expiry;
- still open and blocking.

### 6. Deterministic validators

Before another semantic audit, run every objective check available:

- schema and duplicate-key validation;
- link, reference, and artifact-hash checks;
- required-section and traceability checks;
- repository symbol/path existence;
- compile, type, lint, and test commands where relevant;
- migration validation and dry runs;
- policy, permission, and secret scans;
- lifecycle, authority, and record-lineage invariants;
- checks for unresolved ledger items;
- checks that the approved candidate is the current artifact hash.

An LLM should not spend review effort rediscovering a failure a deterministic validator can prove.

### 7. Diff classifier and re-review router

After repair, compare the previous and current immutable versions. Classify the semantic diff:

- editorial only;
- local clarification;
- test or acceptance-oracle change;
- source/scope change;
- interface or compatibility change;
- data or migration change;
- security/privacy change;
- sequencing or dependency change;
- rollout, observation, containment, or rollback change;
- large or cross-cutting rewrite.

The diff classifier selects affected specialist re-reviews. Any material revision also requires a holistic final outcome audit because local fixes can interact.

### 8. Final closure gate

Closure is separate from ordinary discovery. It verifies:

- the final plan hash is the one reviewed;
- every source criterion is covered or has an authorized disposition;
- every required lens ran or has a valid waiver;
- every required failed or inconclusive review reached the ledger;
- every confirmed finding is closed, blocking, or covered by valid authority;
- every material repair received affected-lens re-review;
- the final holistic review examined the complete current artifact;
- deterministic checks pass;
- no artifact changed after the final review.

The closure gate returns approval, approval with authorized residual risk, revision required, or blocked. It must not infer approval from reviewer silence.

## End-to-end workflow

### Step 1: Intake and freeze

Build an authoritative source bundle containing the ticket, PRD/specification, acceptance criteria, constraints, non-goals, approved decisions, inherited plan documents, and precedence rules. Freeze:

- source-bundle ID, version, and hash;
- plan ID, version, path, and hash;
- repository revision and dirty-state manifest;
- evidence manifest;
- policy, lens-catalog, prompt/skill, model, adapter, and tool versions.

Reject intake if the plan is a delta but inherited documents or precedence cannot be resolved.

### Step 2: Classify and manifest

Run deterministic risk triggers, then semantic classification. Produce one manifest containing selected lenses, execution assignments, isolation requirements, evidence access, model tier, human gates, and waivers.

Do not optimize for the fewest agents before mandatory risk coverage is satisfied. Consolidate compatible lenses into one execution only when each lens retains explicit exit criteria.

### Step 3: Dispatch independent reviews

Run separable reviews in parallel. For cold reviews:

- use a fresh, non-forked context;
- provide only the declared input projection;
- disclose source documents before the plan when independent success criteria are required;
- exclude drafter conversation, previous verdicts, and ambient memory;
- record repository guidance that was automatically loaded;
- record the actual model, effort, adapter, tools, and permissions.

Parallelism reduces latency; it does not create independence by itself.

### Step 4: Adjudicate

Schema-validate every review. Reject findings that lack a source requirement or invariant, concrete scenario, plan evidence, and impact. Feed valid raw findings to the adjudicator only after it forms an independent view.

Persist one canonical finding ledger. Do not use majority voting. Two agents repeating the same unsupported concern do not outweigh one grounded refutation.

### Step 5: Pause for decisions

Require human-in-the-loop action when a finding needs:

- clarification or change of product intent;
- a scope or acceptance-criteria decision;
- architecture ownership outside the plan owner’s mandate;
- security, privacy, legal, financial, safety, or data-risk acceptance;
- a review waiver or policy exception;
- production, release, rollback, or emergency authorization;
- resolution of materially conflicting authoritative sources;
- destructive or irreversible action;
- acceptance of a high-impact fact that remains unestablished.

The loop should stop in a `waiting-for-decision` state. It should not manufacture a decision, quietly downgrade severity, or treat timeout as approval.

### Step 6: Repair

Once decisions are resolved, ask the reviser for one coherent revision rather than one patch per reviewer comment. Constrain it to the adjudicated ledger and authorized decisions.

After the edit:

- issue a new plan version and hash;
- record a semantic diff and finding-resolution map;
- invalidate approval for the prior version;
- run deterministic validators;
- return to adjudication if the reviser disputes a finding rather than silently ignoring it.

### Step 7: Re-route and re-review

For editorial-only changes, verify that the hash change has no semantic effect. For any material change:

- re-run affected specialist lenses;
- run a cold holistic final outcome audit;
- route every new finding through adjudication;
- repair again only if confirmed.

The agent that checks whether a particular finding was fixed should also consider whether the fix introduced a nearby regression. The final outcome reviewer must examine the whole current plan, not only the previous ledger.

### Step 8: Close or escalate

Close only when the stopping policy below passes. Otherwise repeat from the appropriate state. If progress stalls, escalate rather than consuming unlimited audit rounds.

## What convergence means

Convergence is a property of evidence and state, not a count of reassuring verdicts.

A plan has converged when:

1. The source bundle and plan are exact, immutable, and internally resolvable.
2. All classifier-mandated review lenses have valid results or authorized waivers.
3. Every raw material finding has an adjudicated disposition.
4. Every confirmed finding is fixed in the current plan, remains an explicit blocker, or has valid human authority for its residual state.
5. Objective validators pass.
6. Every material repair has received affected-lens re-review.
7. A holistic final review of the complete current plan finds no new unresolved blocker, major, or policy-blocking issue.
8. Remaining moderate/minor issues are either fixed or explicitly classified as nonblocking under policy; they are not merely ignored.
9. No source, plan, evidence, policy, waiver, or authority artifact changed after the final review.
10. The final closure record approves the exact current plan hash.

A “clean” audit before the latest edit is not closure. Any semantic edit invalidates that audit for approval purposes.

## Default stopping and escalation policy

### Suggested defaults

| Risk tier | Closing evidence |
|---|---|
| Low | Deterministic checks plus one independent review of the exact final artifact |
| Normal | Cold outcome review, grounded/verification review, adjudication, and one holistic final re-review after material repair |
| High | Normal portfolio plus all triggered specialists, accountable human/domain adjudication, rehearsal where possible, and a clean exact-artifact closure pass |
| Critical | Policy-defined specialist and human gates, external proof or rehearsal, dual control where required, and explicit accountable approval |

For high-impact work with weak evidence, subtle cross-record invariants, or nondeterministic reviewer behavior, require two closing passes with meaningfully different evidence, prompts, or model families. Do not make “two clean agents” a universal ritual.

### Automatic-loop budget

A useful default is:

- at most three automatic material repair rounds;
- at most one retry per failed agent execution, and only for infrastructure failure;
- immediate human escalation for any blocker/major conflict that adjudication cannot resolve;
- escalation when the same failure class recurs in two successive repaired versions;
- escalation when the number or severity of confirmed findings stops decreasing;
- escalation when reviewers disagree because the source is ambiguous;
- escalation when the next repair would change architecture, scope, authority, or policy beyond the authorized envelope.

The round limit is a circuit breaker, not evidence that the plan is acceptable. Reaching it produces `blocked` or `needs-human-review`, never approval.

### Marginal-yield rule

Do not continue generic auditing merely to obtain another clean statement. Continue when a required lens is missing, a material fact is unverified, a test oracle is weak, a repair changed the plan, or the expected loss from a miss justifies stronger evidence.

Stop adding generic reviewers when mandatory coverage is complete, the exact current artifact has passed closure, and another execution would use the same evidence, prompt, and failure modes.

## Model and effort selection

Model selection should be an output of classification policy.

- Use economical models for deterministic extraction, schema normalization, straightforward repository grounding, and bounded low-risk review.
- Use stronger reasoning for cross-document inheritance, long dependency chains, distributed-system sequencing, authority boundaries, concurrency, cryptographic/hash lineage, migrations, subtle security properties, and adjudication of disputed material findings.
- Use a frontier model or human expert for the final adjudication of consequences the cheaper model cannot establish.
- Consider a different model family for final closure when correlated blind spots are consequential.

A stronger model may reduce the number of rounds by finding interacting defects earlier, but it does not remove the need for exact-artifact re-review after edits. The goal is not to minimize nominal audit count; it is to minimize total cost while satisfying required evidence gates.

## Multi-model execution across providers

### Separate reviewer semantics from model execution

Treat these as independent configuration layers:

1. **Reviewer definition:** the question, evidence rules, read order, authority, output schema, and versioned skill/prompt.
2. **Model profile:** provider, model, reasoning effort, context mode, tool support, cost class, and permitted roles.
3. **Provider adapter:** the mechanics for invoking Codex, Claude, or another runtime and returning a canonical execution record.
4. **Assignment:** one reviewer definition bound to one model profile for one immutable input contract.

This separation lets the same canonical independent-outcome reviewer run on `gpt-5.6-terra-medium`, `gpt-5.6-terra-high`, `gpt-5.6-sol-medium`, `gpt-5.6-sol-high`, `opus-4.8-high`, `opus-4.8-1M-high`, or a future model without cloning and gradually diverging the review logic.

The adapter may translate transport mechanics, tool declarations, sandbox configuration, and output capture. It must not paraphrase the review question, change severity definitions, omit input artifacts, relax abstention rules, or reinterpret the output schema.

### Model registry

Maintain a deployment-owned registry. The following aliases illustrate the profiles used during development; the actual provider model IDs and supported options belong in adapter configuration rather than canonical reviewer prompts.

```yaml
registry_version: "1.0"

model_profiles:
  terra-medium:
    provider_adapter: "codex"
    requested_model: "gpt-5.6-terra"
    reasoning_effort: "medium"
    context_profile: "standard"
    capability_tier: "bounded-material"
    allowed_roles:
      - grounded-review
      - bounded-specialist
      - low-normal-outcome-review
    tool_profiles:
      - read-only-repository
      - no-network
    relative_cost_class: "low"

  terra-high:
    provider_adapter: "codex"
    requested_model: "gpt-5.6-terra"
    reasoning_effort: "high"
    context_profile: "standard"
    capability_tier: "complex-semantic"
    allowed_roles:
      - grounded-review
      - holistic-outcome-review
      - adversarial-falsification
      - bounded-specialist
      - adjudication
      - final-closure
    tool_profiles:
      - read-only-repository
      - isolated-documents
    relative_cost_class: "medium"

  sol-medium:
    provider_adapter: "codex"
    requested_model: "gpt-5.6-sol"
    reasoning_effort: "medium"
    context_profile: "standard"
    capability_tier: "complex-semantic"
    allowed_roles:
      - grounded-review
      - holistic-outcome-review
      - adversarial-falsification
      - bounded-specialist
      - adjudication
      - final-closure
    tool_profiles:
      - read-only-repository
      - isolated-documents
    relative_cost_class: "high"

  sol-high:
    provider_adapter: "codex"
    requested_model: "gpt-5.6-sol"
    reasoning_effort: "high"
    context_profile: "standard"
    capability_tier: "systemic-semantic"
    allowed_roles:
      - holistic-outcome-review
      - adversarial-falsification
      - difficult-specialist
      - adjudication
      - final-closure
      - cross-document-lineage-review
    tool_profiles:
      - read-only-repository
      - isolated-documents
    relative_cost_class: "very-high"

  opus-high:
    provider_adapter: "claude"
    requested_model: "opus-4.8"
    reasoning_effort: "high"
    context_profile: "standard"
    capability_tier: "complex-semantic"
    allowed_roles:
      - holistic-outcome-review
      - adversarial-falsification
      - adjudication
      - final-closure
    tool_profiles:
      - read-only-repository
      - isolated-documents
    relative_cost_class: "high"

  opus-1m-high:
    provider_adapter: "claude"
    requested_model: "opus-4.8"
    reasoning_effort: "high"
    context_profile: "extended-1m"
    capability_tier: "large-cross-document"
    allowed_roles:
      - large-bundle-outcome-review
      - cross-document-lineage-review
      - final-closure
    tool_profiles:
      - read-only-repository
      - isolated-documents
    relative_cost_class: "very-high"

fallback_policy:
  allow_silent_downgrade: false
  require_equal_or_greater_capability_tier: true
  record_actual_profile: true
```

Add deployment facts that the router needs:

- maximum and preferred input size;
- output allowance;
- tool and image/PDF support;
- structured-output support;
- whether fresh non-forked execution is available;
- provider concurrency and rate limits;
- timeout and cancellation behavior;
- confidentiality, data residency, and retention constraints;
- evaluated reviewer roles;
- evaluation-suite version and last passing run;
- availability and authorized fallback profiles.

Do not encode unverified marketing claims as capabilities. A profile becomes eligible for a role after it passes that role’s local evaluation cases.

### Canonical execution request

The controller should give every provider adapter the same logical request:

```yaml
review_execution_id: "revexec-..."
review_definition:
  id: "independent-outcome-audit"
  version: "..."
model_profile:
  id: "opus-high"
  registry_version: "1.0"
input_contract:
  id: "review-input-..."
  schema_version: "1.0"
  sha256: "..."
workspace:
  mode: "isolated-read-only"
  mounted_artifacts: []
information_flow:
  fresh_context_required: true
  staged_read_order: []
output:
  schema_id: "review-record"
  schema_version: "1.0"
  maximum_bytes: null
execution_policy:
  timeout_seconds: null
  infrastructure_retries: 1
  semantic_retries: 0
```

The adapter returns:

- raw output and trace reference;
- normalized canonical review record;
- requested provider/model/effort;
- provider-confirmed model or snapshot when available;
- response/run ID;
- actual context mode;
- actual tools and permissions;
- token/cost/latency data where available;
- truncation, timeout, fallback, or policy exceptions;
- input and output hashes.

Do not rely solely on an auditor’s prose statement that it used a particular model. Record the controller’s requested profile and provider/runtime response metadata. If the runtime cannot attest the exact snapshot or effort, record that fact as `not-established` rather than converting a requested setting into proven execution provenance.

### Provider adapter interface

A small adapter boundary is sufficient:

```text
interface ReviewModelAdapter:
    validate_profile(model_profile) -> ValidationResult
    estimate(request) -> TokenCostLatencyEstimate
    execute(request) -> RawExecution
    normalize(raw_execution, output_schema) -> CanonicalReviewRecord
    attest(raw_execution) -> ExecutionProvenance
    cancel(execution_id) -> Result
```

The controller flow is:

```text
profile = model_registry.resolve(assignment.model_profile_id)
adapter = adapter_registry.resolve(profile.provider_adapter)
adapter.validate_profile(profile)
raw = adapter.execute(canonical_request)
record = adapter.normalize(raw, canonical_schema)
provenance = adapter.attest(raw)
validate(record, provenance, input_contract)
```

Run provider calls concurrently only for separable assignments. Keep one canonical manifest so results from several providers cannot accidentally be joined by array position or display name; join them by review ID and execution ID.

### Credentials and workspace isolation

- Store provider credentials in the runtime’s secret manager or environment, never in prompts, plans, review records, or traces.
- Create a fresh workspace or explicit artifact projection for every cold execution.
- Mount only source and plan artifacts allowed by the input contract.
- Disable writes for reviewers.
- Record automatically loaded repository instructions, system prompts, skills, memory, and connector availability.
- Use a separate writable workspace only for the reviser.
- Destroy ephemeral workspaces after retaining approved artifacts and provenance.

Provider sessions should not be reused for cold review merely to save startup cost. A warm session with prior plan discussion is not cold.

### Two operating modes

#### Fixed portfolio

Use explicit model assignments for reproducible high-value workflows:

```yaml
assignments:
  - reviewer: "independent-outcome-audit"
    model_profile: "opus-high"
  - reviewer: "repository-grounding"
    model_profile: "terra-medium"
  - reviewer: "database-migration"
    model_profile: "opus-high"
  - reviewer: "final-holistic-closure"
    model_profile: "opus-1m-high"
```

This is appropriate when policy or experience already establishes the necessary capability.

#### Policy-routed portfolio

Let the classifier request capabilities rather than model brands:

```yaml
assignments:
  - reviewer: "independent-outcome-audit"
    required_capabilities:
      minimum_tier: "complex-semantic"
      context_profile: "standard"
      independence: "fresh"
      repository_access: "none"
  - reviewer: "database-migration"
    required_capabilities:
      minimum_tier: "complex-semantic"
      tools:
        - "read-only-repository"
```

The scheduler resolves eligible evaluated profiles, then optimizes for cost, latency, availability, or provider diversity within policy. It must never silently downgrade below the requested capability.

Use fixed assignments for critical gates and policy routing for ordinary work. In both modes, freeze the resolved assignment in the review manifest before execution.

## Complexity-based model routing

### Complexity is not just plan length

Increase capability based on the hardest reasoning requirement, including:

- many inherited or delta documents;
- cross-record or cross-service invariants;
- concurrency, ordering, distributed transactions, or idempotency;
- authentication, authorization, cryptography, privacy, or threat modeling;
- irreversible data migration or compatibility windows;
- complex rollout, rollback, or recovery state;
- incomplete or conflicting authoritative sources;
- novel architecture with weak repository precedent;
- a long critical path whose local phases can pass while the global outcome fails;
- previous audit rounds producing new valid material findings;
- evidence that a lower-tier execution truncated, lost lineage, or failed to integrate distant sections.

A short cryptographic protocol plan may require a stronger model than a long routine CRUD plan.

### Suggested routing bands

| Band | Characteristics | Suggested execution |
|---|---|---|
| B0 — bounded | Small, reversible, one surface, strong deterministic evidence | One evaluated medium profile |
| B1 — material | Normal feature, several files/components, clear source contract | Medium grounded review plus strong cold outcome review |
| B2 — complex | Cross-service/data/security/operations, difficult sequencing, material unknowns | High-reasoning holistic reviewer plus triggered specialists; strong adjudicator |
| B3 — systemic | Large cross-document lifecycle, platform migration, subtle authority/concurrency/lineage invariants | Highest evaluated reasoning profile; consider a dissimilar second model and human/domain adjudication |
| B4 — context-extreme | Exact source bundle cannot fit the evaluated standard-context execution with safe headroom | Extended-context profile or explicit decomposition plus cross-slice synthesis |

Risk triggers can raise the minimum band. Cost policy can choose among profiles inside a band but cannot lower it.

### Extended context is a capacity tool, not an automatic quality tier

Use an extended-context profile such as `opus-4.8-1M-high` when the reviewer truly must compare an exact large bundle in one execution. It is especially useful for:

- many inherited documents with precedence rules;
- cross-component schema consistency;
- lifecycle and state-machine closure;
- long traceability chains;
- a final holistic pass after sliced specialist reviews.

Do not use the largest context merely because it is available. Large irrelevant context can dilute attention and increase cost. First remove non-authoritative material and create role-specific projections. Preserve policy-configured headroom for instructions, tool results, reasoning, and output rather than filling the advertised window.

If the authoritative bundle still exceeds the evaluated safe input:

1. Decompose by end-to-end invariant or lifecycle path, not arbitrary token chunks.
2. Give each slice its exact source and dependency references.
3. Run specialist/slice reviews independently.
4. Run a cross-slice reviewer over the source contract, dependency map, slice findings, and full plan if the selected profile can safely hold it.
5. Mark any unexamined interaction as not established.

## Escalating when the loop is not converging

Do not respond to every new finding by blindly buying a larger model. Diagnose the non-convergence pattern.

| Pattern | Likely cause | Correct response |
|---|---|---|
| New valid cross-document issues appear each round | Initial reviewer lacked integration capability or context | Escalate holistic reviewer tier/context; consider a dissimilar high-tier model |
| The same confirmed issue survives successive edits | Repairer misunderstood, edit scope is constrained, or test does not enforce closure | Fix repair instructions/checks; escalate to human if intent is ambiguous |
| Reviewers contradict each other on requirements | Source ambiguity or authority gap | Human/source decision, not another generic audit |
| Only editorial findings remain | Stopping/severity policy is too permissive | Apply non-material closure rules; do not run indefinitely |
| Output is truncated or distant dependencies disappear | Context capacity or projection problem | Extended context or structured decomposition |
| Findings are numerous but mostly rejected | Reviewer prompt/model is noisy | Re-evaluate reviewer; do not escalate its authority |
| Different models repeat identical unsupported claims | Shared evidence or rubric blind spot | Add grounded evidence or expert oracle |
| Material findings stop decreasing | Workflow is stalled | Block after the configured round budget and require human redesign |

### Capability escalation ladder

Use a configured ladder, for example:

```text
evaluated medium profile
        ↓ material integration miss
evaluated high-reasoning profile
        ↓ large-bundle or systemic miss
evaluated extended-context/high profile
        ↓ unresolved material disagreement
dissimilar high-tier model + human/domain adjudication
```

Escalation starts a new review execution against the same immutable artifact or, after repair, the new immutable version. Preserve the lower-tier result; do not overwrite it.

An escalation is justified when:

- the adjudicator confirms a material failure that the lower tier missed;
- a review returns `not-established` because of reasoning/context capability;
- a required lifecycle/path trace cannot be completed;
- a repaired artifact produces another new material integration defect;
- policy designates the surface high or critical.

It is not justified merely because the planner dislikes the verdict or wants to retry until approved.

### Use the stronger model earlier for known-hard artifacts

Your experience—moving from `gpt-5.6-terra-medium` to `opus-4.8-high` and then an extended-context high profile as a complex specification failed to converge—should become routing data.

Create a regression case representing that artifact class. If evaluation shows that the medium profile repeatedly misses cross-component closure defects while the high-reasoning profile catches them at acceptable precision, update the classifier so future systemic lifecycle specifications start at the higher band. This avoids paying for several weak rounds before selecting the capability the artifact needed from the beginning.

Do not generalize from one artifact to every plan. Promote the routing rule only for the observed failure class, and periodically retest it as models and prompts change.

## Multi-model review portfolios

Use model diversity to cover correlated blind spots, not to create a vote.

### Recommended role allocation

For a complex plan:

```text
frontier drafter
      ↓
high-reasoning cold outcome reviewer from another context/model family
      +
medium grounded reviewers for bounded repository facts
      +
high-reasoning triggered specialists for difficult domains
      ↓
strong independent adjudicator
      ↓
original drafter/reviser
      ↓
dissimilar high-reasoning final closure reviewer
```

The adjudicator may use the same model family as one reviewer when necessary, but should have fresh context, source-first read order, and distinct authority. For high-risk work, model diversity plus distinct evidence is preferable.

### No majority vote

If Terra reports a blocker and Opus rejects it, do not count votes. The adjudicator checks:

- which requirement or invariant governs;
- which artifact version each reviewer inspected;
- whether either reviewer had repository or external evidence;
- whether the failure scenario is concrete and gate-passing;
- whether one result was truncated or not established;
- whether the disagreement is actually a product/authority decision.

The model identity is provenance, not weight by itself.

### Closing review after multi-model repair

After feedback is folded in:

- re-run every lens whose subject changed;
- use a holistic reviewer capable of the complete current artifact;
- prefer a different model/context from the reviser for final closure;
- require a second closing model only when policy, risk, weak evidence, or measured nondeterminism warrants it;
- approve only if all closing records bind the same final hash.

Two models reviewing different plan versions do not provide two closing opinions.

## Cost, concurrency, and failure policy

### Budget before execution

Set:

- maximum cost per lifecycle;
- maximum input and output tokens per lifecycle;
- maximum total model executions;
- maximum wall-clock duration;
- maximum material rounds;
- maximum parallel executions;
- per-role eligible cost classes;
- high-tier escalation budget;
- a protected final-closure reserve;
- human escalation threshold.

If required coverage exceeds the budget, return a decision request. Do not silently omit a lens or downgrade a model.

### Usage budget gate

The controller should evaluate a usage gate before every model dispatch. The gate compares:

- usage already consumed;
- estimated cost of the pending required assignments;
- uncertainty in that estimate;
- usage reserved for adjudication and final exact-artifact closure;
- lifecycle and tier-specific limits.

If the pending work would consume the closure reserve, pause before dispatch and request budget or scope authority. Do not spend the last available high-tier call discovering a defect when no budget remains to review the repaired artifact.

Use several limits because call count alone is misleading:

```yaml
usage_budget:
  maximum_total_executions: 12
  maximum_material_repair_rounds: 4
  maximum_input_tokens: null
  maximum_output_tokens: null
  maximum_cost_units: null
  maximum_wall_clock_minutes: null

  tier_limits:
    bounded-material:
      maximum_executions: 8
    complex-semantic:
      maximum_executions: 4
    systemic-semantic:
      maximum_executions: 2
    large-cross-document:
      maximum_executions: 2

  protected_reserve:
    adjudication_executions: 1
    final_closure_executions: 1
    final_closure_minimum_capability: "complex-semantic"

  on_warning: "finish-current-execution-then-reassess"
  on_limit: "pause-for-authorized-budget-decision"
  on_hard_limit: "block-never-approve"
```

The numbers are starting examples, not universal defaults. A review portfolio may contain several parallel assignments, so maintain both:

- **round counters**, which measure audit → adjudicate → material repair cycles;
- **execution counters**, which measure individual model calls by profile and role.

Infrastructure retries count against usage but not against semantic convergence rounds. A semantically unfavorable result is not a retry.

### `N` base rounds followed by `M` higher-tier executions

This is a reasonable policy when `N` and `M` are circuit breakers rather than claims of sufficiency.

A good starting form is:

```yaml
convergence_escalation:
  base_rounds_before_diagnosis: 2 # N
  promoted_holistic_executions: 2 # M
  absolute_material_round_limit: 4

  promoted_execution_allocation:
    diagnosis_on_current_artifact: 1
    final_closure_on_repaired_artifact: 1

  auto_promote_for:
    - capability-limited-integration
    - context-capacity-limited
    - confirmed-new-material-findings-across-successive-rounds

  do_not_auto_promote_for:
    - ambiguous-or-conflicting-source
    - missing-authoritative-evidence
    - repeated-unfixed-finding
    - required-human-risk-decision
    - reviewer-noise-or-low-precision
    - repair-outside-authorized-scope

  after_promoted_budget_exhausted: "pause-for-human-review"
  approval_on_budget_exhaustion: false
```

With `N = 2` and `M = 2`, the intended path is:

```text
base round 1 → adjudicate → repair
base round 2 → adjudicate
        ↓ still not converging
diagnose non-convergence
        ↓ capability/context issue confirmed
higher-tier execution 1: holistic diagnosis
        ↓ adjudicate → repair
higher-tier execution 2: exact-artifact final closure
        ↓
approve if clean | otherwise pause/block for HITL
```

Do not spend both promoted executions before a repair. One should normally be reserved to inspect the exact repaired artifact.

`N` should count completed **material repair rounds**, not every reviewer in a parallel portfolio. `M` should normally count promoted holistic executions or portfolios, while separate specialist budgets remain explicit. This prevents a database, security, and outcome review launched together from accidentally consuming three “rounds.”

### Non-convergence diagnosis gate

Reaching `N` should invoke a diagnosis step before model promotion:

| Diagnosis | Meaning | Controller action |
|---|---|---|
| `capability-limited-integration` | Lower tier misses or cannot integrate distant, interacting constraints | Promote reasoning tier; consider a dissimilar model |
| `context-capacity-limited` | Required exact bundle truncates or exceeds safe evaluated capacity | Use extended context or structured decomposition |
| `repair-failure` | The same confirmed finding survives revision | Fix reviser instructions/checks or require human repair |
| `source-ambiguity` | Different valid interpretations produce different plans | Pause for authoritative human/source decision |
| `missing-evidence` | Repository, API, owner, or environment fact is unavailable | Obtain evidence or remain blocked |
| `review-noise` | New findings are mostly rejected or preference-based | Re-evaluate/retire the reviewer; do not grant it a larger model automatically |
| `material-redesign` | Closing findings require scope or architecture beyond current authority | Pause for a new approved plan/source decision |

Only the first two, and sometimes repeated **confirmed new** integration findings, justify automatic tier escalation. A stronger auditor does not repair a weak reviser, clarify product intent, supply missing evidence, or authorize risk.

The diagnosis itself may be deterministic when signals are clear:

- provider reports truncation → `context-capacity-limited`;
- same finding ID/failure mechanism remains open after repair → `repair-failure`;
- adjudicator says `needs-decision` because sources conflict → `source-ambiguity`;
- two successive rounds add confirmed cross-component findings → candidate `capability-limited-integration`.

Use a human or strong adjudicator when the cause is uncertain.

### Pre-dispatch reserve algorithm

Before dispatching assignment `A`:

```text
remaining = lifecycle_budget - actual_usage
required_after_A = protected_adjudication + protected_final_closure
estimated_A = estimate(A) + configured_uncertainty_margin

if estimated_A + required_after_A > remaining:
    pause_for_budget_decision()
else:
    dispatch(A)
```

If actual usage unexpectedly crosses a soft limit, allow already-running work to finish when safe, stop launching new work, and reassess. If the hard limit is reached, the lifecycle becomes blocked or waits for authorized budget expansion. It never becomes approved merely because usage is exhausted.

### What happens when the higher tier still finds issues

If the first promoted execution finds valid material issues, adjudicate and repair them, then use the reserved promoted execution for closure.

If the promoted closure finds another material issue:

1. Record and adjudicate it normally.
2. Do not approve the artifact.
3. Do not silently take budget reserved for another lifecycle or downgrade final review.
4. Pause for a human decision to:
   - authorize another bounded repair/closure budget;
   - decompose or rewrite the plan;
   - obtain missing specialist evidence;
   - change the reviewer/model portfolio;
   - cancel or defer the lifecycle.

For high or critical work, the human may require a dissimilar high-tier model or domain expert rather than another execution of the same profile.

### Starting tier can bypass `N`

`N` is not a mandatory cheap-model warm-up. If the initial classifier assigns B2/B3 complexity, or local evaluation shows that a plan class routinely defeats the medium profile, start at `terra-high`, `sol-medium`, `sol-high`, `opus-high`, or an evaluated extended-context profile as appropriate.

The cheapest workflow is often the one that chooses sufficient capability before round one. The escalation gate is a fallback for misclassification or unexpectedly difficult artifacts, not a requirement to prove that a lower tier fails first.

### Parallel scheduling

Run independent discovery lenses across providers in parallel. Keep dependent work sequential:

```text
classification
    ↓
parallel discovery reviews
    ↓
adjudication
    ↓
repair
    ↓
parallel affected-lens re-reviews
    ↓
final closure
```

Respect provider rate limits and record queue delay separately from model latency.

### Retries and fallbacks

- Retry only timeout, transport, or provider infrastructure failures.
- Give each retry a new `review_execution_id`.
- Keep the same frozen artifact and input contract unless the contract itself was invalid.
- Do not retry a semantic `not-established`, blocker, or unfavorable verdict as infrastructure failure.
- A fallback must meet the assignment’s capability, context, tool, isolation, confidentiality, and evaluation requirements.
- Record the requested profile, fallback reason, actual profile, and both execution attempts.
- If no valid fallback exists, block the assignment.

## Evaluating reviewer × model × adapter combinations

A reviewer prompt that performs well on one model may fail on another. Treat the deployable component as:

```text
reviewer skill version
    × model profile
    × provider adapter version
    × tool/permission profile
```

Evaluate each permitted combination on:

- clean plans;
- seeded omissions and infeasibilities;
- cross-document and delta-plan cases;
- weak acceptance oracles;
- specialist triggers;
- noisy pseudo-findings;
- ambiguity requiring abstention;
- context-isolation attacks;
- adapter-equivalence cases;
- historical escapes.

Track:

- material recall;
- confirmed-finding precision;
- false-block rate;
- correct `not-established` behavior;
- unique confirmed yield;
- source/evidence fidelity;
- severity calibration;
- truncation and schema-failure rate;
- cost and latency;
- agreement and error correlation with other profiles.

Do not promote a model profile for a role solely because its aggregate score is higher. It must pass zero-tolerance cases and the risk segments assigned to it.

When a model, effort option, context mode, adapter, system prompt, tool policy, or reviewer skill changes, create a new evaluated component version. Do not assume `opus-high` and `opus-1m-high` behave identically simply because their base model name matches.

## Canonical records to persist

Use a durable directory or record store such as:

```text
runs/
  life-2026-.../
    source/
      authoritative-source-bundle.v1.json
    plans/
      plan.v001.md
      plan.v002.md
    contracts/
      review-input.plan-v001.json
      review-input.plan-v002-final.json
    classification/
      classification.v001.json
      review-manifest.v001.json
    rounds/
      001/
        reviews/
        adjudication.json
        finding-ledger.v001.json
        repair-resolution.json
        deterministic-checks.json
      002/
        reviews/
        adjudication.json
        finding-ledger.v002.json
        final-closure.json
    decisions/
    waivers/
    traces/
```

Persist logical versions and cryptographic hashes inside the records. A filename alone is not artifact identity.

At minimum, retain:

- source bundle;
- every plan version;
- input contracts;
- classification and manifest;
- raw review and finding records;
- model/effort/prompt/skill/adapter/tool provenance;
- adjudication and canonical ledger;
- human decisions and waivers;
- semantic diffs and repair maps;
- deterministic check results;
- final closure.

## Vendor-neutral orchestration pseudocode

```text
function review_to_convergence(source_paths, plan_path, policy):
    lifecycle = create_lifecycle()
    source = freeze_source_bundle(source_paths)
    plan = freeze_plan(plan_path)
    round = 0

    while round < policy.maximum_material_rounds:
        round += 1
        contract = freeze_input_contract(lifecycle, source, plan, policy)
        classification = classify(contract)
        manifest = select_required_reviews(classification, policy)

        assert deterministic_triggers_preserved(manifest, policy)
        raw_reviews = run_in_parallel(
            fresh_execution(assignment, contract)
            for assignment in manifest.assignments
        )
        assert schemas_and_provenance_valid(raw_reviews)

        ledger = independently_adjudicate(
            source_first=true,
            plan=plan,
            reviews=raw_reviews
        )

        if ledger.requires_human_decision:
            decision = wait_for_authorized_human_decision(ledger)
            if decision.rejected_or_deferred:
                return blocked_or_deferred(lifecycle, plan, ledger, decision)
            ledger = apply_decision_to_ledger(ledger, decision)

        if ledger.has_confirmed_open_findings:
            if repair_exceeds_authorized_scope(ledger):
                return blocked_needs_human(lifecycle, plan, ledger)

            candidate = revise_once_coherently(source, plan, ledger)
            checks = run_deterministic_validators(candidate)
            if checks.fail:
                candidate = handle_objective_failures(candidate, checks)

            diff = classify_semantic_diff(plan, candidate)
            plan = freeze_new_plan_version(candidate)

            if diff.editorial_only:
                verify_no_semantic_change(diff)
            else:
                continue

        closure_contract = freeze_final_review_contract(source, plan, ledger)
        closure_reviews = run_affected_and_holistic_reviews(closure_contract)
        closure_ledger = independently_adjudicate(closure_reviews)

        if closure_ledger.has_confirmed_open_findings:
            ledger = merge_ledgers(ledger, closure_ledger)
            continue

        closure = evaluate_final_gates(
            exact_plan_hash=plan.sha256,
            source=source,
            manifest=manifest,
            ledger=closure_ledger,
            deterministic_checks=checks
        )

        if closure.approved and artifact_is_unchanged(plan):
            return approved(lifecycle, plan, closure)

        if closure.requires_human:
            return waiting_for_human(lifecycle, plan, closure)

    return blocked_iteration_budget_exhausted(lifecycle, plan)
```

The production implementation must also handle append-only versions, atomic state updates, execution identity, retries, authority, waiver expiry, and invalidation. The pseudocode shows control flow, not the full record-integrity model.

## Prompt and skill contracts

Keep canonical logic vendor-neutral. Build thin Claude, Codex, or other adapters that translate execution mechanics without changing:

- required read order;
- input identities and hashes;
- review-lens semantics;
- output schema;
- severity definitions;
- abstention behavior;
- authority boundaries;
- stopping gates.

Use separate versioned skills for:

- plan classification and review selection;
- independent outcome audit;
- grounded feasibility and verification;
- adversarial falsification;
- each high-value specialist lens;
- finding adjudication;
- bounded plan repair;
- diff classification;
- final closure.

Do not encode the whole lifecycle in one giant reviewer prompt. The workflow controller owns sequencing and state; skills own bounded cognitive tasks.

## Human-in-the-loop interface

Present decisions as compact packets:

- exact question;
- authoritative source excerpts;
- established facts, inferences, and unknowns;
- affected plan version/hash;
- options and consequences;
- reviewer/adjudicator conclusions;
- dissenting evidence;
- required owner and authority;
- default result if no decision is made.

The safe default for no response is pending or blocked. Never interpret silence as approval.

Human review should focus on intent, trade-offs, authority, and residual risk. Do not make the human reread every raw agent transcript when an evidence-linked ledger can present the real decision.

## Observability and maintenance

Track the loop as a production system:

- number of rounds to closure;
- confirmed findings by lens and severity;
- rejected/noise rate;
- recurring failure classes;
- new material findings discovered after each repair;
- specialist trigger recall;
- deterministic failures caught before semantic review;
- cost and latency per lifecycle;
- human decision time;
- model/provider/prompt/adapter versions;
- escaped defects after implementation;
- false blockers and unnecessary scope growth;
- correlation and duplicate rate between reviewers;
- marginal unique yield by lens.

Seed the evaluation suite with failures the loop previously missed. Include clean plans so reviewers are penalized for manufacturing problems. Re-run evaluation when models, prompts, tools, repository conventions, policies, or source-contract formats change.

Version and promote reviewer changes through the [evaluation and drift harness](../canonical/components/06-evaluation-drift-harness/evaluation-and-drift-harness.md). Do not silently edit the production skill after a bad review.

## Practices to avoid

- One agent alternates between auditor, adjudicator, reviser, and approver.
- Reviewers can mutate the artifact they judge.
- Every raw finding is automatically applied.
- Majority vote substitutes for evidence.
- Reviewer count substitutes for specialist coverage.
- Forked context is labeled cold.
- The next audit sees prior conclusions before forming its own view.
- A retry reuses the same review-execution identity.
- The controller retries semantic failure until a favorable verdict appears.
- A “no issues” string triggers approval without checking artifact hash and ledger state.
- Minor/editorial churn keeps an unlimited loop alive.
- A maximum-round limit silently converts failure to success.
- Risk acceptance, policy exceptions, or production authorization are inferred from agent output.
- The plan is edited after final review without invalidating closure.
- The same prompt is repeatedly run and counted as several independent evidence channels.

## A practical implementation sequence for next time

### Phase 1: File-based minimum viable loop

1. Define JSON/YAML schemas for input contract, classification, review manifest, finding, review record, ledger, decision, repair map, and closure.
2. Write a small deterministic controller that computes hashes and maintains legal states.
3. Create the model registry and one thin adapter for each runtime you use, initially Codex and Claude.
4. Invoke existing classifier and reviewer prompts as fresh subprocess/agent calls through those adapters.
5. Freeze the resolved reviewer-to-model assignments in the review manifest.
6. Enforce read-only reviewer workspaces and a writable reviser workspace.
7. Validate every output and actual execution provenance before accepting it.
8. Pause on `needs-human-decision`.
9. Require a new plan version and final cold review after material repair.
10. Save the full lifecycle under `runs/<lifecycle_id>/`.

This is sufficient to replace a manual copy/paste loop without first building a service.

### Phase 2: Reliability

1. Add deterministic trigger rules and semantic-diff classification.
2. Add atomic state updates and execution-specific retry identities.
3. Add authority and waiver records.
4. Add seeded evaluation cases for known failure classes.
5. Add cost, latency, reviewer-yield, and escape metrics.
6. Add resumability so a human decision or failed execution does not lose state.

### Phase 3: CI and repository integration

1. Trigger the pipeline when a plan/spec changes.
2. Pin repository revisions and evidence manifests.
3. Publish a concise status check linked to the ledger and exact plan hash.
4. Block approval when required reviews, decisions, or re-reviews are incomplete.
5. After implementation, classify the diff and run conformance/release review.
6. Feed production escapes and false positives back into evaluation cases.

## Recommended next-time configuration

For a normal engineering plan:

1. Use the classifier to select the cold outcome and grounded verification reviewers plus triggered specialists and minimum capability tiers.
2. Resolve those capabilities through the evaluated multi-model registry and freeze the assignments.
3. Run reviewers across eligible providers in parallel, fresh and read-only.
4. Use a separate strong adjudicator.
5. Pause only for genuine human decisions.
6. Return confirmed findings to the original drafter for one coherent revision.
7. Run deterministic checks and diff classification.
8. Re-run affected specialists and one cold holistic final audit on a capable, preferably dissimilar model.
9. Approve only the exact unchanged plan hash.
10. Cap automatic material repair rounds at three and escalate if the loop does not converge.

For a complex lifecycle specification like the eight-component system audited here, select high reasoning for the first whole-system semantic audit rather than spending many cheap rounds rediscovering cross-record invariants. Use cheaper agents for bounded specialists and mechanical verification. Even then, every material fix still needs exact-artifact closure; model strength can reduce discovery rounds, but cannot make re-review unnecessary.
