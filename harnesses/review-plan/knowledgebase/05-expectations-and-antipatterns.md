# Realistic expectations and practices to avoid

## What good reviews help with

### Earlier discovery of missing work

Reviewers can map a source contract across user surfaces, interfaces, data paths, tests, and operations. Uber’s first-pass PRD evaluator reports value from finding unsupported assumptions, adjacent impacts, missing guardrails, prior experiments, and cross-functional dependencies before expensive review forums ([Uber](https://www.uber.com/gb/en/blog/first-pass-prd/)).

### Separation of fact, assumption, and decision

A grounded critic can expose where fluent planning prose rests on an unverified repository or platform claim. This is especially important because agents only know context made legible to them. OpenAI’s agent-first engineering account emphasizes repository-local, versioned knowledge and enforceable checks ([OpenAI](https://openai.com/index/harness-engineering/)).

### Stronger tests and rollout criteria

Adversarial review can construct wrong implementations that pass weak checks, reveal missing failure injection, and force operational success/failure signals into the plan. Google SRE notes that test environments and tests cannot cover all real production behavior, motivating staged canaries and observable evaluation ([Google SRE](https://sre.google/workbook/canarying-releases/)).

### Better sequencing and cheaper failure

Reviews can move uncertain integration, permissions, migration, or performance work earlier and preserve compatible intermediate states. Google’s code-review guidance recommends surfacing major design problems first because downstream work may otherwise be wasted ([Google](https://google.github.io/eng-practices/review/reviewer/navigate.html)).

### More useful human decisions

Structured reviews can clear factual and completeness work so humans focus on tradeoffs, policy, and risk acceptance. Uber explicitly describes AI review as improving the artifact entering human review, not replacing expert judgment.

### Reusable organizational learning

Confirmed recurring findings can become tests, linters, templates, platform defaults, or narrowly targeted review lenses. Google and AWS use post-incident learning to improve future review and readiness mechanisms.

## What reviews do not guarantee

### They do not prove correctness or completeness

Unknown requirements, inaccessible systems, stale sources, and shared model blind spots remain. A clean audit means “no material problem found under these inputs and methods,” not “no problem exists.”

### They do not create missing product authority

An agent can identify that messaging/groups policy is unresolved; it cannot legitimately decide the policy unless authorized. Evaluation cannot substitute for governance, a limitation also emphasized in Google research on evaluation boundaries ([Google Research](https://research.google/pubs/on-the-limits-of-evaluation/)).

### They do not validate runtime reality without external evidence

A plan can be coherent while deployment credentials, traffic shape, data quality, or third-party behavior differ. Tests, prototypes, staged rollout, telemetry, and operator validation remain necessary.

### They do not ensure reviewer independence

Cold context reduces anchoring but does not change shared training or missing evidence. Same-model copies can converge on the same mistake.

### They do not make every finding useful

LLM critics can produce false positives, preferences, duplicates, and plausible but impossible scenarios. Adjudication is required. OpenAI recommends Codex review as an additional reviewer rather than a replacement for human review ([OpenAI Codex review](https://openai.com/index/introducing-upgrades-to-codex/)).

### They do not automatically save time

Agent review has cost: context construction, false-positive adjudication, revision, and re-review. METR’s early-2025 randomized study found experienced open-source developers took 19% longer with the tested AI tools on their own repositories, illustrating that benchmark capability does not imply workflow acceleration in every setting ([METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)). Current tools have changed since that snapshot; the methodological lesson remains.

## Practices to avoid

### Review before reading the source contract

The plan’s structure anchors the reviewer. Require independent success criteria from the ticket/spec first when performing an outcome audit.

### Empty-directory review as the only review

It protects framing independence but cannot discover unlisted routes, files, dependencies, conventions, or platform constraints. Pair it with grounded review for material work.

### Self-review as acceptance

Self-refinement can improve outputs, but intrinsic self-correction can also fail or degrade reasoning without external feedback ([Self-Refine](https://arxiv.org/abs/2303.17651); [Huang et al.](https://deepmind.google/research/publications/48252/)). Treat self-review as draft improvement, not independent assurance.

### Generic “be adversarial” prompts

They optimize for criticism volume. Give a falsifiable question, evidence requirements, severity schema, and permission to return no findings.

### Majority vote

Votes assume error independence that LLM panels often lack. Resolve findings against sources and evidence.

### Same-agent author, judge, and reviser

This preserves coherence but concentrates blind spots and incentives. Separate at least finding validation and final approval.

### Raw feedback folded directly into the plan

Reviewers disagree and overreach. Adjudicate first; maintain an explicit ledger.

### Reviewer identity or prior verdict anchoring

Hide author/model identity where practical. For comparisons, blind labels and reverse order. Position and familiarity biases are measured problems in LLM judging.

### One enormous review prompt

Combining requirements, architecture, security, data, operations, tests, and style leads to uneven attention and noisy output. Route only triggered specialist lenses.

### Giant plans

Length can conceal missing decisions and overload both human and model attention. Decompose into coherent, end-to-end slices and retain a short decision/traceability spine.

### Checklist theater

Filled boxes are not evidence. Require links, tests, metrics, or explicit accepted risks. Allow “not applicable” with rationale.

### Treating tests as infallible

Tests can encode the same misunderstanding as the plan, reject valid behavior, or under-cover acceptance criteria. Review the oracle and inspect failures.

### All findings treated as blockers

Severity inflation makes the reviewer unusable. Separate ticket failure and safety risk from optimization and preference.

### Central review board for every plan

DORA reports no evidence that heavyweight external approval improves change-failure rates for ordinary work and warns that delay can increase batch size. Use local peer review and automation, escalating by risk ([DORA](https://dora.dev/capabilities/streamlining-change-approval/)).

### Reviewer swarm for sequential work

Parallel agents help separable breadth-first tasks; tightly dependent planning needs an owner and coherent synthesis. Anthropic reports multi-agent systems use far more tokens, while Google research found some multi-agent arrangements amplify errors on sequential work ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system); [Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)).

### No re-review after fixes

This approves an obsolete artifact. Re-review the final version whenever commitments changed.

### Prompt accumulation

Adding a rule for every false positive or escaped defect creates conflicting, stale instructions. Convert repeat problems into the simplest enforceable control, test changes, and prune.

### Optimizing vanity metrics

Comment count, agent agreement, verbosity, token spend, and raw “issues found” reward noise. Measure confirmed material findings, escaped defects, downstream rework, review time, and decision usefulness.

## Healthy language for conclusions

Prefer:

- “Achieves the stated goal under these verified assumptions.”
- “Achieves the goal with these material gaps and accepted residual risks.”
- “Does not achieve the source contract because…”
- “Not established from the supplied evidence.”

Avoid:

- “Guaranteed correct.”
- “Three agents agreed, therefore safe.”
- “All tests pass, therefore the ticket is solved.”
- “The frontier model is confident.”
