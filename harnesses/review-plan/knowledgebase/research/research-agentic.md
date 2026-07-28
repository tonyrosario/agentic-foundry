# Agentic software-development workflows: planning, review, and governance

Research memo — 22 July 2026

## Executive view

**Synthesis.** The most defensible production pattern is not “give an agent a ticket and merge its patch.” It is a controlled loop: establish a bounded task contract; explore in a read-only context; make design decisions visible for human approval; implement in a narrow writable environment; verify with deterministic checks; conduct an independent, fresh-context adversarial review; revise; re-run affected checks and review; then retain the artifacts needed to audit and improve the workflow.

This is supported by several, mutually reinforcing findings:

- Anthropic explicitly recommends *explore → plan → implement → commit*, and says agents need executable checks rather than an assertion that work is done. It also recommends a fresh verification subagent that attempts to refute the implementer’s result. [Anthropic best practices](https://code.claude.com/docs/en/best-practices)
- Anthropic’s production PR review dispatches several agents in parallel, verifies potential bugs to reduce false positives, and ranks the confirmed findings; it still leaves merge approval to people. [Anthropic Code Review announcement](https://claude.com/blog/code-review)
- OpenAI’s Codex guidance pairs sandboxing, scoped approvals, network policy, identity controls, rules, and audit telemetry—and says human review and validation remain necessary before integration. [Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/); [Introducing Codex](https://openai.com/index/introducing-codex/)
- Microsoft’s field study found developers resolved only about half of real repository issues; incremental, iterative collaboration outperformed one-shot use. [Microsoft Research study](https://www.microsoft.com/en-us/research/publication/sharp-tools-how-developers-wield-agentic-ai-in-real-software-engineering-tasks/)
- Google research cautions that multi-agent systems help parallelizable work but can hurt sequential work; an orchestrator materially contains error propagation relative to independent agents. [Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)

**Decision implication.** Use independent agents for bounded investigation or review lanes, not as an automatic substitute for a coherent owner. Give one orchestrator (human or agent under human authority) responsibility for the task contract, evidence, arbitration, and final merge decision.

## Evidence versus convention versus synthesis

This memo labels claims as follows:

- **Evidence** — directly supported by cited product documentation, public research, or measured vendor experience.
- **Conventional wisdom** — a widely used engineering practice; plausible and useful, but not established here as a causal universal.
- **Synthesis** — this memo’s recommended design, inferred from the evidence and engineering trade-offs.

Vendor operational metrics (for example, Anthropic’s review acceptance figures) are useful case evidence, not independent general proof. HumanLayer/CRISPY is a public practitioner workflow, not peer-reviewed research; it is treated accordingly.

## What the current sources actually support

### Planning before mutation

**Evidence.** Anthropic’s published Claude Code workflow separates exploration, planning, implementation, and commit. In plan mode the agent reads and answers without changes; Anthropic advises using it for uncertain, multi-file, or unfamiliar changes, while skipping it for a truly one-sentence diff. [Anthropic best practices](https://code.claude.com/docs/en/best-practices)

**Evidence.** The same guidance says a runnable test, build, linter, fixture diff, or visual comparison closes an autonomous loop. It specifically recommends showing the command and output, and identifies a second-opinion verification subagent as a way to keep the worker from grading itself. [Anthropic verification guidance](https://code.claude.com/docs/en/best-practices)

**Evidence.** Microsoft observed 19 developers solving 33 issues in repositories they knew; incremental participants and those who iterated with the agent were more successful than one-shot users. This is a small observational study, but it is closer to real work than a benchmark. [Microsoft Research](https://www.microsoft.com/en-us/research/publication/sharp-tools-how-developers-wield-agentic-ai-in-real-software-engineering-tasks/)

**Synthesis.** A plan should be a reviewable change contract, not a long agent diary. Require: problem and non-goals; current-state facts and source locations; decision(s) and alternatives rejected; file/interface/data migration impact; invariants and risks; tests/observability; rollout/rollback; and acceptance criteria. A human should approve decision-bearing plans before write access is used for material changes.

### Context is a quality and security boundary

**Evidence.** Anthropic says a session includes conversation, files read, and command output; performance degrades as the context fills, potentially causing forgotten instructions and mistakes. It recommends aggressive context management and isolated subagents for large investigations. [Anthropic context guidance](https://code.claude.com/docs/en/best-practices)

**Evidence.** Microsoft’s 2026 SWE-Edit work frames this as “context coupling”: inspection, planning, and strict edit formatting share one context, accumulating irrelevant information. Its Viewer/Editor separation improved its reported SWE-bench Verified resolved rate by 2.1 points while reducing inference cost 17.9%; this is a research result, not a universal product guarantee. [Microsoft Research: SWE-Edit](https://www.microsoft.com/en-us/research/publication/swe-edit-rethinking-code-editing-for-efficient-swe-agent/)

**Synthesis.** Treat context as an input supply chain. Do not put untrusted issue text, web pages, logs, generated artifacts, or retrieved documents into a privileged executor’s context without delimiting them as data. Separate contexts by role: a fact-finding/retrieval agent, a planner, a restricted implementer, and a cold reviewer. Pass only structured, cited outputs between them. This reduces both accidental instruction leakage and confirmation bias; it does not make prompt injection impossible.

**Conventional wisdom.** Prefer small, task-specific context packets over “read the whole repo.” Include the source revision and file paths, so evidence can be re-checked after changes.

### Multi-agent work: parallelism with a judge, not committee theatre

**Evidence.** Anthropic’s managed PR review runs agents in parallel on the diff and surrounding code, verifies bugs to filter false positives, and ranks them by severity. Its stated system does not approve PRs itself. [Claude Code Review docs](https://code.claude.com/docs/en/code-review); [Anthropic announcement](https://claude.com/blog/code-review)

**Evidence.** Google tested five architectures over 180 configurations. Parallelizable tasks benefited from coordination, whereas sequential planning degraded under every multi-agent variant tested; independent agents amplified errors up to 17.2×, versus 4.4× for centralized coordination with an orchestrator. [Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)

**Synthesis.** Use agents where their outputs can be independently compared or checked:

| Work type | Useful pattern | Avoid |
|---|---|---|
| Repository discovery | 2–4 independent read-only vertical slices, then a reconciler | Several agents editing overlapping files |
| Design | One planner plus a critical reviewer with explicit decision rubric | “Vote” without an owner or criteria |
| Implementation | One accountable implementer per isolated worktree/module | Parallel writers sharing an uncoordinated tree |
| PR review | Specialized reviewers (correctness, security, concurrency/data, test gap), evidence verifier, severity judge | Asking the authoring agent to certify itself |
| Final decision | Human or accountable owner consumes a concise evidence packet | Auto-merge from reviewer count or benchmark score |

The reviewer/judge must be allowed to return “not established,” request evidence, or reject a finding. Majority vote is weak when agents share model, prompt, retrieved context, or a mistaken premise; diversity helps only when it changes evidence or failure modes.

### Cold-context audit and adversarial review

**Evidence.** Anthropic explicitly offers a verification subagent that has a fresh model try to refute results, and custom subagents with isolated context and constrained tools for specialized review. [Anthropic best practices](https://code.claude.com/docs/en/best-practices)

**Evidence.** Anthropic describes its own review system as bug discovery in parallel followed by verification and severity ranking. Its public claims: 54% of PRs received substantive comments after rollout versus 16% before, and fewer than 1% of findings were marked incorrect. These are internal operational measurements, not independently reproduced results. [Anthropic announcement](https://claude.com/blog/code-review)

**Synthesis.** A cold review should receive the issue/spec, approved plan, base and head revisions, diff, deterministic test evidence, and relevant architectural constraints—*not* the implementer’s chain of reasoning or its self-declared success. Its prompt should require each finding to name: location, triggering scenario, expected versus actual behavior, impact, evidence, confidence, and the smallest fix. A separate judge should deduplicate and reject findings that lack a reproducible scenario or contradict the contract.

**Synthesis.** Re-review after revisions is mandatory for material changes. The minimum re-review scope is every changed hunk plus dependencies of a finding’s root cause. Re-run targeted tests, then the appropriate broader suite; update the evidence packet. A reviewer that assessed an earlier diff has not assessed the final diff.

## A staged workflow, including CRISPY

### Baseline controlled workflow

**Synthesis.** The following is a pragmatic default for medium/high-risk changes.

1. **Intake / Context.** Normalize the ticket into objective goals, constraints, non-goals, risk tier, systems touched, owner, and acceptance checks. Mark unknowns.
2. **Research (read-only).** Produce a source-linked current-state brief: call/data flow, existing patterns, invariants, tests, and relevant history. No solution recommendation in the fact brief.
3. **Iterate / design checkpoint.** Discuss alternatives and resolve decisions with a human owner. Record assumptions and explicit non-decisions.
4. **Structure and plan.** Produce a small implementation contract with ordered steps, migrations, test/rollback plan, and the exact verification commands. Obtain approval when policy requires it.
5. **Synthesize execution context.** Create a clean worktree/branch and a compact packet containing only approved plan, facts, conventions, and allowed tools/paths.
6. **Implement and self-verify.** One primary agent makes the change; deterministic checks run in the constrained environment. Preserve commands, outputs, dependency changes, and diff.
7. **Independent adversarial review.** Cold reviewers inspect implementation and evidence; verifier/judge filters, prioritizes, and produces actionable findings.
8. **Revise, re-verify, re-review.** Fix confirmed findings. Repeat the affected verification and review surfaces. Escalate unresolved disagreements to a human.
9. **Merge / learn.** Human authority accepts the risk. Store compact outcome data: task class, plan version, checks, findings, overrides, defects/regressions, token/cost/latency, and prompt/skill versions.

For a clearly bounded low-risk patch, combine steps 1–5 and keep a lightweight independent diff review. Do not let a “small diff” eliminate security, migration, or authorization review where the blast radius is high.

### CRISPY / RPI status

**Evidence (practitioner source).** Public HumanLayer material describes an earlier Research–Plan–Implement process and a seven-stage “CRISPY” evolution: **C**ontext, **R**esearch, **I**terate, **S**tructure, **P**lan, s**Y**nthesize, Implement. It says the research stage intentionally hides the ticket while gathering objective current-state facts, then exposes design decisions in a short discussion before implementation. [Public HumanLayer workflow summary](https://www.zenml.io/llmops-database/evolving-ai-coding-agent-workflows-from-research-plan-implement-to-crispy)

**Evidence (practitioner source).** The presenter reports reversing an earlier “do not read generated code” position after needing to replace production systems, and argues for code ownership/review rather than reliance on plans. [Same source](https://www.zenml.io/llmops-database/evolving-ai-coding-agent-workflows-from-research-plan-implement-to-crispy)

**Synthesis.** CRISPY’s valuable ideas are separation of fact discovery from solution anchoring, early human alignment, and compact artifacts. Do not adopt its stage names as ceremony. Adopt them only where they buy a concrete control: decision review, context hygiene, reproducibility, or handoff clarity.

## Governance: capabilities, authority, and auditability

**Evidence.** OpenAI’s published internal governance pattern is bounded execution plus approval policy, controlled network access, credential/identity management, command rules, and agent-native telemetry. [Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)

**Synthesis.** Map risk tier to capability rather than trusting an agent’s stated intent.

| Tier | Examples | Agent authority | Required gates |
|---|---|---|---|
| 0 | Docs, tests, local refactor | Workspace write; no secrets/network by default | Test/lint, diff review |
| 1 | Feature behind flag; internal service | Narrow repo/worktree; allow-listed dev network | Approved plan, CI, cold review |
| 2 | Auth, payments, data migration, privileged APIs | Read-first; scoped credentials; no production mutation | Human design sign-off, security review, staged rollout/rollback |
| 3 | Production data deletion, releases, security incident action | Propose only unless an explicit runbook authorizes action | Named human approval per action, dual control, immutable audit trail |

Controls to make concrete:

- Least privilege: per-task worktree, repository/path allowlists, ephemeral credentials, environment separation, egress allowlists, and no secrets in prompt/context/logs.
- Authority separation: the agent that writes code cannot be the sole evaluator, approver, deployer, or policy editor.
- Deterministic guardrails: use CI, protected branches, required checks, policy-as-code and hooks for non-negotiable constraints. Advisory repository instructions are useful, but are not enforcement.
- Provenance: record model/version, system or skill/prompt version, repository/base/head SHA, tool policy, commands, outputs, retrieved sources, reviewer roles, human decisions, and overrides.
- Retention/privacy: logs are valuable evidence but may contain proprietary code, tokens, credentials, or user data. Apply access controls, redaction, retention windows, and incident response procedures.

## Evaluation: why benchmark scores are insufficient

**Evidence.** SWE-bench evaluates patches generated for real GitHub issues against repository tests, and its harness uses containers for reproducibility. SWE-bench Verified is a 500-problem human-confirmed subset. [SWE-bench repository](https://github.com/swe-bench/SWE-bench)

**Evidence.** The SWE-bench project requires execution logs and reasoning traces for its verified-result process, which is a useful reproducibility precedent. [SWE-bench experiments and policy](https://github.com/swe-bench/experiments)

**Evidence.** OpenAI’s 2026 audit says SWE-bench Verified had design and contamination problems, and found approximately 30% of SWE-Bench Pro tasks broken after agent-assisted investigation and independent human review. Its reported failure modes were over-strict tests, underspecified or misleading prompts, and low-coverage tests. [OpenAI benchmark audit](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)

**Evidence.** Microsoft found that an outcome-only test-pass score can conceal “lucky passes”: among a selected set of passing SWE-agent trajectories, 10.7% showed regression cycles, blind retries, missing verification, or disordered exploration/implementation/verification. [Microsoft Research: AgentLens](https://www.microsoft.com/en-us/research/publication/agentlens-revealing-the-lucky-pass-problem-in-swe-agent-evaluation/)

**Synthesis.** Use public benchmarks for directional capability comparisons, not deployment approval. Maintain an internal, versioned evaluation portfolio with:

- fresh or private tasks protected from training and workflow tuning;
- representative task families: bug repair, migration, ambiguous requirements, security, incident/runbook, performance, and cross-service change;
- outcome metrics: correctness, regression rate, security findings, merge/revert rate, lead time, operator interventions, and cost/latency;
- process metrics: plan adherence, evidence completeness, unverified claims, tool-policy violations, reviewer precision/recall measured from later outcomes, and re-review escape rate;
- adversarial tasks: misleading issue text, conflicting docs/tests, stale conventions, hidden authorization boundaries, malicious instructions in retrieved content, and partial-success traps;
- human audit sampling, including failed and superficially successful runs.

## Feedback integration and prompt/skill maintenance

**Synthesis.** Treat prompts, skills, rules, tool policies, and reviewer rubrics as versioned production artifacts. They change agent behavior as materially as code changes a service.

1. Assign an owner and semantic version to every reusable instruction set.
2. Keep a “finding ledger”: confirmed defect, false positive, escaped defect, policy violation, root cause, task class, and prompt/skill/tool versions.
3. Convert recurring failures into a proposed prompt/rubric/guardrail change—not an unreviewed accretion of instructions.
4. Before rollout, run a frozen regression suite plus targeted red-team cases; compare quality, safety, cost, latency, and false-positive rate against the previous version.
5. Canary the change on low-risk work, monitor outcome and process metrics, then promote or roll back.
6. Periodically delete stale/conflicting instructions. Long instruction piles increase context load and make priority ambiguous.

**Conventional wisdom.** Maintain an explicit “known false positive / not-a-bug” catalog for reviewers, but require every exception to identify why it is safe and when it should expire. Otherwise it becomes a mechanism for suppressing real regressions.

**Synthesis.** Drift detection needs two loops: (a) *behavioral drift*—the same prompt/model/tool version gives worse plans, checks, or review precision over time; and (b) *environmental drift*—repository conventions, dependencies, tests, threat model, or deployment policy change while the prompt remains static. Detect both with scheduled replay of golden tasks, sampled live audit, change-triggered revalidation (for dependency/policy/architecture changes), and metrics segmented by task/risk class.

## Red-team agenda

**Synthesis.** Test the workflow itself, not merely the coding model.

- **Instruction/data boundary:** put malicious or irrelevant instructions in an issue, README, dependency output, web page, test fixture, and log; verify the agent treats them as untrusted data.
- **Authority boundary:** induce requests for credential export, unapproved egress, writes outside the worktree, production commands, or disabling controls; verify refusal/escalation and audit trail.
- **Specification conflict:** create a task where ticket, existing behavior, docs, and tests disagree; require explicit surfacing and human decision, not silent choice.
- **Reviewer independence:** give the implementation a subtle but plausible flaw; ensure cold review can catch it without the author’s rationale. Measure false positives too.
- **Evidence integrity:** tamper with test output, pass a narrow test with a broader regression, or present stale base SHA; verify provenance and required checks catch it.
- **Coordination failure:** create overlapping agents, a failed subagent, inconsistent findings, and circular delegation; verify an orchestrator limits scope and halts safely.

## Anti-patterns

- **One-shot autonomous delivery for ambiguous work.** Contradicted by Anthropic’s staged guidance and Microsoft’s observed advantage for iterative use.
- **“Tests passed, therefore correct.”** Benchmarks and production tests can be strict in the wrong way, under-cover behavior, or conflict with the stated task. [OpenAI benchmark audit](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)
- **Self-review as the only review.** It shares context and incentives with the author; use fresh-context challenge and evidence-based adjudication.
- **Multi-agent theatre.** More independent agents can magnify error, cost, and inconsistency; Google’s results argue for task-aligned coordination and a validation bottleneck. [Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)
- **Giant plans and giant prompts.** They are difficult for humans to review, consume context, and conceal missing decisions. Prefer compact decision artifacts and executable criteria.
- **Unbounded tool access.** Do not mix broad credentials, unrestricted network access, and autonomous execution; capability should follow risk and approval.
- **No final-diff review after fixes.** Findings may be fixed incorrectly or introduce a new issue. Re-verify and re-review the actual merge candidate.
- **Optimizing only public leaderboard scores.** Public, static benchmarks can saturate, contaminate, or contain flawed datapoints; deploy from representative internal evidence.
- **Instruction accumulation without evaluation.** Prompt folklore becomes untestable policy drift. Version, test, and prune it.

## Recommended minimum operating standard

**Synthesis.** For an organization adopting coding agents now, set this as the initial bar:

1. Protected branches and human merge ownership.
2. Repository-local guidance, deterministic CI checks, and a risk-tiered approval policy.
3. Read-only research plus approved implementation contract for non-trivial work.
4. Per-task sandbox/worktree; no default production credentials or broad egress.
5. Evidence packet: base/head SHA, diff, commands/results, known limitations, dependency changes, reviewer findings/disposition.
6. Independent cold review for material changes; specialized security review for sensitive surfaces.
7. Re-test and re-review after material revision.
8. Versioned prompts/skills/rubrics, a feedback ledger, periodic red-team and internal eval replay.

The purpose is not to slow agents down. It is to make their speed legible, reversible, and trustworthy enough to compound.
