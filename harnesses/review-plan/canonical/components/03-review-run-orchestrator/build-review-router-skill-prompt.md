# Prompt: build a canonical review-router skill with runtime adapters

Copy the prompt below into an agent that can create and validate skills. Replace only the variables you care about; the defaults are intentionally generic.

---

## Prompt begins

You are building a reusable agent skill that classifies an engineering plan and selects the smallest sufficient review suite for it.

Build a canonical, vendor-neutral core first. Then create thin adapters for Claude Code and Codex. Do not build two independently designed skills: both adapters must preserve the same routing semantics, risk model, output schema, deterministic policy, and evaluation cases.

### Configuration

Use these values unless I override them:

```yaml
skill_name: select-plan-reviews
display_name: Select Plan Reviews
output_directory: ./select-plan-reviews
supported_adapters:
  - claude-code
  - codex
default_mode: plan-time
baseline_review: independent-outcome
policy_precedence: deterministic-rules-win
semantic_classifier_authority: add-only
```

If a required output location is not supplied and the task would install the skill rather than create source artifacts locally, ask where it should be created. Otherwise build it in `output_directory`.

Use the target environment’s official skill-creation guidance and validation tools. Read those instructions completely before creating files. Do not assume Claude-specific or Codex-specific capabilities in the canonical core.

### Objective

Given a source contract and a candidate engineering plan, produce a machine-readable and human-readable **review manifest** containing:

- risk tier and rationale;
- detected change/risk surfaces;
- required review lenses and why each is required;
- evidence each reviewer needs;
- reviews considered but not selected, with rationale;
- required human decisions or approvals;
- unresolved classification facts;
- re-review triggers;
- provenance for the classification;
- adapter/runtime used.

The classifier must optimize for coverage and distinct evidence, not reviewer count. It may say that one reviewer can cover several compatible low-risk lenses, but it must select lenses before deciding how many reviewer executions are appropriate.

### Required architecture

Implement this logical pipeline:

```text
source contract + plan + optional change evidence
                       ↓
             normalize input manifest
                       ↓
       deterministic policy/risk triggers
                       +
      cold semantic classifier, when required
                       ↓
          union and precedence resolution
                       ↓
               review manifest
                       ↓
       optional review dispatch by adapter
```

Keep these responsibilities separate:

1. **Canonical workflow:** input requirements, stages, precedence, escalation, output contract.
2. **Deterministic policy:** mandatory baseline and risk-triggered lenses.
3. **Semantic classifier:** finds latent risks not captured by paths or keywords.
4. **Runtime adapter:** maps abstract operations to Claude Code or Codex mechanisms.
5. **Evaluation harness:** proves routing behavior and adapter equivalence.

### Canonical behavior

The core must support two classification modes:

#### Plan-time mode

Run before implementation using:

- ticket, issue, PRD, or other source contract;
- proposed plan and inherited/delta documents;
- declared files, services, data stores, interfaces, dependencies, permissions, and deployment effects;
- optional read-only repository inspection;
- organizational review policy.

Select plan-review lenses.

#### Diff-time mode

Run after implementation using:

- the same source contract and approved plan;
- actual changed files and dependency changes;
- actual schemas, migrations, permissions, infrastructure, API, test, and deployment changes;
- plan deviations.

Reclassify risk and select implementation/diff reviews. Diff-time classification must be capable of escalating beyond the plan-time result when implementation touches undeclared surfaces.

### Baseline and risk model

Require at least one outcome-focused review for every material plan. Permit a no-review result only for explicitly configured trivial classes such as spelling-only edits, and record the deterministic rule that allowed it.

Define four default tiers:

```text
Tier 0 — low: local, reversible, no boundary or behavior risk
Tier 1 — normal: bounded product/code behavior with ordinary rollback
Tier 2 — high: sensitive boundary, migration, public contract, broad blast radius, or difficult recovery
Tier 3 — critical: irreversible production effects, safety/legal incident action, or foundational high-consequence change
```

Tier is not determined by document length. Base it on consequence, reversibility, novelty, coupling, blast radius, evidence quality, and recovery.

Provide default risk triggers for at least:

- database/schema/state migration, backfill, reconciliation, retention;
- authentication, authorization, sessions, permissions, secrets, trust boundaries;
- privacy, sensitive data, legal or policy obligations;
- payments, billing, entitlements, irreversible user effects;
- public or cross-team APIs, schemas, queues, protocols, webhooks;
- distributed ordering, concurrency, retries, replay, idempotency;
- infrastructure, deployment topology, SLOs, capacity, operational ownership;
- performance and cost changes requiring a workload model;
- external dependencies or platform behavior;
- accessibility or user-segment impact;
- agent permissions, credentials, network access, or instruction/data boundaries;
- broad customer impact, weak rollback, or missing observability;
- contradiction among ticket, docs, code, and tests;
- missing or low-quality evidence.

Map triggers to focused review lenses. Include at least:

- `independent-outcome`;
- `grounded-feasibility`;
- `requirements-traceability`;
- `adversarial-falsification`;
- `verification-quality`;
- `security`;
- `privacy-legal`;
- `data-migration`;
- `interface-compatibility`;
- `sequencing-reversibility`;
- `operational-readiness`;
- `performance-cost`;
- `accessibility-product-policy`;
- `prototype-rehearsal`;
- `final-plan-rereview`;
- `implementation-conformance`.

Use the canonical lens catalog version and normalize deprecated human labels before emitting records. Unknown or ambiguous aliases are invalid; `security/privacy` expands to both `security` and `privacy-legal`.

### Precedence and authority rules

Enforce these invariants:

1. Baseline reviews and deterministic mandatory reviews cannot be removed by the semantic classifier.
2. The semantic classifier may add lenses, raise risk, request evidence, or return `not established`.
3. The semantic classifier may recommend consolidation of compatible lenses into one reviewer execution, but may not erase the underlying lens requirements.
4. Human policy may add reviews.
5. Waiving execution of a mandatory lens requires an explicit human waiver containing owner, rationale, scope, and expiry/review date; the lens remains selected and visible.
6. Unknown high-impact facts escalate; they are never silently interpreted as low risk.
7. A reviewer/model majority cannot override evidence or deterministic policy.
8. Runtime adapters cannot silently alter canonical routing rules.

Use two explicit sets:

```text
selected_lenses =
    baseline
  ∪ deterministic triggers
  ∪ semantic additions
  ∪ human additions

execution_required_lenses =
    selected_lenses
  − lenses with explicit valid execution waivers
```

Never subtract a waived lens from `selected_lenses`. The manifest records it as selected-and-waived so evaluation and feedback can measure the unexecuted coverage.

### Semantic classifier contract

Define an abstract operation such as `classify_semantic_risks` without binding it to one vendor.

The semantic classifier must:

- run read-only;
- start with fresh/non-forked context when the runtime supports it;
- receive only the source contract, plan, policy, declared/observed change manifest, and relevant authoritative evidence;
- avoid the drafter’s conversation, self-assessment, or previous reviewer verdicts;
- distinguish observed fact, inference, and unknown;
- cite plan, repository, or authoritative documentation evidence for material classifications;
- recommend additions only;
- be allowed to return `no semantic additions`;
- be allowed to return `not established` and list missing evidence;
- not judge whether the plan itself is correct; it only routes review.

Skip semantic classification for deterministic Tier 0 cases when policy explicitly permits it. Run it by default for Tier 1 and above, missing evidence, or ambiguous surface declarations.

### Reviewer consolidation

After selecting lenses, determine the minimum safe execution portfolio.

Permit one reviewer to combine lenses only when:

- the risk is low or normal;
- the lenses require substantially the same evidence;
- combining them does not overload the review prompt;
- no policy requires specialist independence;
- the manifest retains each lens and its exit criteria separately.

Do not consolidate specialist independence away for Tier 2/3 security, privacy, data migration, payments, or other policy-designated surfaces.

Example expectations:

- A spelling-only plan may require no plan review if explicit Tier 0 policy permits it.
- A small local behavior change normally gets one combined outcome/feasibility/testability reviewer.
- A bounded multi-file feature gets outcome plus grounded code/test review.
- A database schema change gets baseline outcome plus data/migration review.
- A live migration with mixed-version deployment gets outcome, data/migration, and sequencing/operational review.
- An authorization change gets outcome plus security review even if the diff is small.
- A payment migration may require outcome, security, data/migration, compatibility, operations, and accountable human approval.

### Review-manifest schema

Define and validate a stable machine-readable schema similar to:

```yaml
schema_version: "1.0"
lifecycle_id: "life-..."
input_contract_id: "review-input-..."
classification_id: "..."
review_manifest_id: "manifest-..."
review_manifest_version: "..."
mode: plan-time | diff-time
adapter: canonical | claude-code | codex
lens_catalog_version: "1.0"
parent_records:
  - record_type: review-input-contract
    record_id: "review-input-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: dispatch-input
  - record_type: classification-record
    record_id: "class-..."
    record_sub_id: null
    schema_version: "1.0"
    logical_record_version: null
    record_sha256: "..."
    lifecycle_id: "life-..."
    role: governing-classification
source:
  authoritative_source_bundle:
    id: "..."
    schema_version: "1.0"
    version: "..."
    path: "..."
    sha256: "..."
  candidate:
    id: "..."
    path: "..."
    sha256: "..."
  repository_revision: null
  policy_version: "..."
risk:
  tier: 0 | 1 | 2 | 3
  consequence: low | medium | high | critical
  reversibility: easy | bounded | difficult | irreversible
  novelty: known | adapted | new
  coupling: local | boundary | multi-system | organizational
  evidence_quality: executable | cited | inferred | missing
surfaces:
  - id: "..."
    evidence: []
selected_lenses:
  - lens_id: independent-outcome
    source: baseline | deterministic | semantic | human
    reason: "..."
    evidence_needed: []
    independence_required: false
    waiver_id: null
execution_required_lens_ids:
  - independent-outcome
execution_portfolio:
  - review_id: "rev-..."
    lens_ids: []
    isolation: fresh | inherited | not-applicable
    capability: standard | strong | domain-expert | human
    evidence_projection_id: "projection-..."
    review_execution_ids: []
not_selected:
  - lens_id: "..."
    reason: "..."
unknowns: []
human_gates: []
waivers: []
rereview_triggers: []
provenance:
  classifier_prompt_version: "..."
  model: null
  tools: []
integrity:
  hash_profile: "canonical-json-sha256-v1"
  manifest_sha256: "..."
  supersedes_review_manifest_id: null
```

The human-readable rendering must explain why every lens was selected or omitted. Do not output only a numeric score. Require every record to follow the canonical lifecycle’s lineage, immutable artifact binding, and manifest-to-review identifier semantics.

### Canonical skill structure

Follow the target skill-authoring standard. Keep the canonical `SKILL.md` concise, imperative, and progressively disclosed. Put detailed policy, schemas, and examples in directly linked resources.

Prefer a structure equivalent to:

```text
select-plan-reviews/
├── SKILL.md
├── references/
│   ├── risk-model.md
│   ├── review-lenses.md
│   ├── manifest-schema.md
│   ├── adapter-contract.md
│   ├── default-policy.json
│   └── eval-cases.json
├── scripts/
│   ├── collect_signals.*
│   ├── apply_policy.*
│   ├── validate_manifest.*
│   └── run_evals.*
└── [runtime metadata required by the installed target]
```

Do not add auxiliary README, installation guide, changelog, or process diary inside the skill. Include only files needed for execution or validation.

Use deterministic scripts for policy application, schema validation, and evaluation when practical. Avoid nonstandard dependencies unless justified. Test all scripts by running them.

### Adapter contract

Define the canonical capabilities adapters must implement:

- locate/read source contract and plan;
- inspect repository read-only;
- collect changed paths and declared/actual surfaces;
- invoke deterministic policy;
- spawn or invoke a fresh read-only semantic classifier;
- capture model/runtime provenance;
- render and optionally dispatch the review manifest;
- enforce permissions and waivers;
- report unsupported capabilities rather than simulating them.

Create thin adapter artifacts outside or alongside the canonical core so an installed runtime receives only its relevant adapter.

#### Claude Code adapter

Map the canonical contract to current Claude Code skill/subagent mechanisms after checking official documentation. In particular:

- use a fresh custom subagent rather than a fork when coldness is required;
- restrict tools to read/search and other explicitly allowed non-mutating tools;
- use plan/read-only permission behavior;
- account for automatically loaded `CLAUDE.md`, memory, or repository instructions in the provenance and coldness claim;
- define how the skill invokes the classifier and how the manifest is returned;
- keep Claude-specific paths, frontmatter, commands, and permission details out of canonical policy.

#### Codex adapter

Map the canonical contract to current Codex skill/subagent mechanisms after checking official documentation. In particular:

- create the required Codex skill metadata deterministically;
- use a fresh subagent without inherited turns when coldness is required;
- constrain the classifier to read-only behavior and scoped tools;
- define how deterministic scripts and repository evidence are accessed;
- record model, effort, tool policy, and context-fork mode;
- keep Codex-specific metadata, paths, commands, and orchestration details out of canonical policy.

If either runtime cannot guarantee a claimed isolation or permission property, state the limitation in its output and downgrade the manifest’s isolation field. Never label a context cold merely because it is a subagent.

### Evaluation requirements

Build a small deterministic routing suite covering at least:

1. spelling-only edit;
2. local reversible refactor;
3. normal multi-file feature;
4. new database table without backfill;
5. destructive or difficult-to-reverse migration;
6. authorization logic change hidden inside a UI task;
7. public API breaking change;
8. retry/idempotency change;
9. infrastructure/SLO change;
10. sensitive-data retention change;
11. payment or entitlement migration;
12. plan-time low risk that becomes higher risk in the actual diff;
13. missing evidence requiring `not established`;
14. semantic classifier attempts to remove a deterministic lens;
15. human waiver with and without required metadata.

For each case, assert:

- minimum tier;
- mandatory lenses;
- lenses that require independence;
- human gates;
- whether semantic classification runs;
- expected escalation or abstention.

Run the same canonical cases through both adapters and demonstrate semantic equivalence of the resulting required lenses and risk tier. Adapter-specific provenance may differ; policy results must not.

Forward-test the completed skill on realistic raw ticket/plan artifacts using fresh contexts. Do not give the test agents expected answers. Inspect both routing output and whether the skill followed the intended evidence/order/permission behavior.

### Acceptance criteria

Do not declare completion until:

- the canonical skill passes its official validator;
- all deterministic scripts run successfully;
- manifest validation rejects malformed output;
- deterministic rules cannot be removed by semantic output;
- missing evidence escalates safely;
- both adapters pass canonical routing cases;
- adapter outputs identify actual isolation and provenance accurately;
- plan-time and diff-time modes both work;
- no adapter-specific behavior has leaked into canonical policy;
- the canonical `SKILL.md` remains concise and references detailed resources only when needed;
- a user can invoke the skill on a plan and receive a justified review manifest without manually selecting reviewers first.

### Final delivery

Return:

1. Paths to the canonical skill and each adapter.
2. A compact architecture summary.
3. The default risk-to-lens routing table.
4. Example plan-time and diff-time manifests.
5. Validation and evaluation commands with results.
6. Known runtime limitations and any isolation claims that could not be guaranteed.
7. The exact steps needed to install or package each adapter, but do not perform external installation unless explicitly authorized.

## Prompt ends

---

## Suggested customization variables

The canonical prompt is usable as written. For an organization-specific build, append:

```yaml
organization_policy_sources:
  - ./AGENTS.md
  - ./docs/architecture/
  - ./docs/security/review-policy.md
mandatory_review_owners:
  security: security-team
  data-migration: database-team
  privacy-legal: privacy-team
trivial_change_policy:
  allow_no_review: false
custom_risk_triggers:
  - condition: touches-regulated-export-data
    minimum_tier: 3
    selected_lens_ids: [security, privacy-legal]
```

Keep organization-specific triggers in policy overlays rather than editing the canonical workflow. That makes the Claude and Codex adapters easier to compare and upgrade.
