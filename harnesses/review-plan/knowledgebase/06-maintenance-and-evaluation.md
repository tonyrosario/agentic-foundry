# Maintaining and evaluating review prompts

Treat audits, reviewer prompts, skills, tool policies, and rubrics as versioned production systems. Their model, context, repository, threat environment, and users drift.

Anthropic recommends keeping agent evaluation suites healthy through clear ownership, multiple grader types, transcript inspection, regression/capability separation, and ongoing task contribution. It warns that automated evals can create false confidence when they stop matching real use ([Anthropic evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).

## What to version

Every review execution should record:

- review type and prompt/skill semantic version;
- model, model snapshot if available, provider, effort/temperature;
- source-contract and plan version/hash;
- repository base SHA and relevant external-doc retrieval date;
- supplied files/context manifest and order;
- tool and permission policy;
- reviewer role and whether context was fresh, forked, or inherited;
- raw findings, citations/evidence, and adjudicated disposition;
- revision and final-review version;
- cost, latency, failures, and human overrides.

Without provenance, model changes or source drift can look like prompt improvements.

## Build a review gold set

Create a representative, human-adjudicated corpus from historical and synthetic plans:

- strong plans with no material defect;
- plans that omit a ticket requirement;
- plans with unrequested scope;
- technically infeasible repository assumptions;
- weak tests that pass a wrong implementation;
- bad migration/deployment sequence;
- hidden auth/privacy/data boundary;
- stale documentation or conflicting sources;
- ambiguous requirements where “needs decision” is correct;
- noisy pseudo-defects that a good reviewer should reject;
- final revisions that fix one finding while introducing another.

Each case needs expected material findings, acceptable alternate formulations, non-findings, severity, evidence, and adjudication rationale. Keep a private holdout so prompt authors cannot optimize only to visible examples.

## Evaluation metrics

### Finding quality

- **Precision:** confirmed material findings / all material findings reported.
- **Seeded-defect recall:** seeded defects found / seeded defects present.
- **Escape recall proxy:** known post-approval defects the reviewer could have found / total such defects.
- **Severity calibration:** agreement with expert severity and action threshold.
- **Evidence validity:** findings whose cited source actually supports the claim.
- **Source fidelity:** findings based on supplied authoritative artifacts rather than invention.
- **False-block rate:** good plans incorrectly declared non-achieving.
- **`not established` quality:** appropriate escalation rather than guessed answers.

True recall is unknowable on live plans because undiscovered defects are unobserved. Use seeded cases, later implementation/release defects, and periodic expert audits as complementary estimates.

### Workflow value

- confirmed new findings per reviewer-minute and per dollar;
- time from draft to approved plan;
- rework avoided before implementation;
- findings discovered only after implementation or release;
- percentage of plans materially changed by review;
- human adjudication burden and disagreement rate;
- review-induced scope growth;
- re-review escape rate;
- author/reviewer usefulness ratings tied to concrete decisions, not satisfaction alone.

### Stability and bias

- repeated-run consistency;
- plan-order swap consistency in comparisons;
- author/model identity sensitivity;
- verdict consistency across equivalent paraphrases;
- performance by task/risk class rather than aggregate only;
- correlation and duplicate rate among reviewers.

## Evaluate outcome and trajectory

Final verdict alone can conceal lucky reasoning, fabricated evidence, or policy violations. Review a sample of traces for:

- whether the ticket was read before the plan;
- whether cited files/docs were actually inspected;
- unsupported assumptions;
- instruction conflicts or prompt injection obedience;
- evidence that does not support the finding;
- early convergence on another reviewer’s framing;
- repeated low-value criticism;
- unsafe tool or permission attempts.

Microsoft’s AgentLens work reports “lucky pass” trajectories where outcome-only scoring concealed regressions, blind retries, missing verification, or disordered work. The transferable lesson is to inspect both outcome and process ([Microsoft AgentLens](https://www.microsoft.com/en-us/research/publication/agentlens-revealing-the-lucky-pass-problem-in-swe-agent-evaluation/)).

## Drift model

| Drift | Example | Detection |
|---|---|---|
| Model drift | Provider silently updates behavior; new model is more verbose or less skeptical | Frozen gold-set replay and repeated trials |
| Prompt drift | Accreted rules conflict or suppress legitimate findings | Version diff, ablation, gold/holdout results |
| Repository drift | Architecture, conventions, test commands, ownership change | Change-triggered revalidation; repo-guidance ownership |
| Requirement drift | Product policy or source-of-truth location changes | Owner review and source manifest refresh |
| Tool/harness drift | Search, sandbox, MCP, or permissions change | Harness integration tests and provenance checks |
| Threat drift | New prompt-injection or supply-chain route | Scheduled workflow red team |
| Population drift | Audit now handles migrations/security instead of UI features | Metrics segmented by task/risk class |
| Evaluator drift | Human labels or LLM adjudicator become inconsistent | Double-label samples and calibration reviews |

## Cadence

Use both event-driven and scheduled maintenance.

Revalidate when:

- model/provider/effort changes;
- prompt, skill, rubric, context packet, or tool policy changes;
- repository architecture or mandatory engineering policy changes;
- a material false positive or escaped defect occurs;
- review responsibilities expand to a new task/risk class.

On a schedule:

- sample live reviews and adjudications monthly or at a volume-based interval;
- inspect trend metrics and false-positive catalog quarterly;
- run gold and red-team suites before every reviewer release;
- reassess task distribution and retire stale cases at least twice yearly;
- re-baseline after major model generations rather than assuming old thresholds transfer.

Adjust cadence to volume and risk; a small team need not imitate a large platform organization.

## Finding ledger and learning loop

Maintain one durable ledger containing:

- confirmed defect;
- rejected/duplicate finding;
- escaped defect or post-release incident;
- task/risk class;
- root cause: prompt, missing context, capability, tool, source, or governance;
- review versions involved;
- action and owner;
- whether the remedy became prompt guidance, a deterministic check, a template change, training/example data, or no change.

Prefer deterministic enforcement for objective recurring rules. A practitioner report from Claude Code creator Boris Cherny describes logging repeated review comments and converting recurring patterns into lint rules; regardless of exact threshold, this is a sound direction: automate stable invariants and reserve agents for judgment ([Pragmatic Engineer interview summary](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny)).

Do not add a prompt rule for every incident. Ask:

1. Is the failure recurring and material?
2. Is the rule general without harming legitimate cases?
3. Can a test/linter/schema/policy enforce it more reliably?
4. What existing instruction conflicts with it?
5. What case will demonstrate improvement and what case protects against overcorrection?
6. Who owns expiry or future review?

## Change procedure for an audit prompt

1. Open a change record with hypothesis and target failure class.
2. Freeze baseline model/harness and run the current prompt on gold plus holdout.
3. Make the smallest coherent prompt/rubric change.
4. Run multiple trials where nondeterminism matters.
5. Compare precision, recall proxies, severity, evidence validity, cost, and latency.
6. Manually inspect disagreements and traces; do not choose solely by aggregate score.
7. Shadow on live plans without affecting decisions.
8. Canary on low-risk work with human adjudication.
9. Promote, roll back, or revise; record the decision.
10. Monitor escapes and false positives by risk class.

## Avoid evaluation contamination

- Keep a private holdout.
- Do not include gold answers in normal reviewer context.
- Rotate fresh cases from new plans and failures.
- Separate prompt-development and final-adjudication responsibilities where possible.
- Blind human adjudicators to reviewer variant during comparative evaluation.
- Track whether public benchmark or template examples are likely present in model training.

SWE-bench Live and other continuously refreshed benchmarks exist partly because static tasks risk contamination and overfitting ([SWE-bench Live](https://arxiv.org/abs/2505.23419)). Local plan audits need the same defense.

## Retirement criteria

Retire or redesign a review when it:

- cannot achieve acceptable precision without suppressing major defects;
- duplicates deterministic tooling at higher cost;
- no longer matches current artifacts or architecture;
- adds no unique confirmed findings over a cheaper review;
- has become saturated and cannot distinguish stronger behavior;
- relies on unsupported model confidence or unverifiable evidence;
- causes more harmful scope/rework than it prevents.

Keep historical versions and results so a regression can be traced and an earlier version restored.
