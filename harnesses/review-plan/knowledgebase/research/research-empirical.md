# Empirical evidence memo: adversarial review of AI-generated engineering plans

**Scope.** This memo distinguishes evidence about evaluating or improving *model outputs* from evidence that an AI-only review process makes an engineering plan trustworthy. The former is substantial but task-bound; the latter is much thinner. A plan is an intermediate artifact: it needs both semantic scrutiny and external, repository-specific verification.

## Bottom line

1. Critique, reflection, and multi-agent debate can improve outputs on measured tasks, but they are not independent verification by default. They are search procedures whose value depends on feedback quality and error diversity.
2. A same-model (or closely related) author and critic can share blind spots. Treat agreement as a weak signal unless critics have different evidence, different model families/context, or mechanical checks.
3. Use an LLM judge to prioritize and explain review work, not as the sole acceptance authority. It has measured position, style/length, and self-preference biases.
4. Anchor every plan claim to inspectable evidence: requirement/source → proposed file/symbol/change → test or other verification. Then run the verification where possible. This is stronger than asking several agents whether the prose “looks complete.”
5. Stop review based on *coverage and residual risk*, not a fixed number of agreeable agents or self-reported confidence. Escalate unresolved high-impact assumptions, contradictory reviews, and non-verifiable claims.

## 1. What critique, reflection, and debate demonstrably do—and do not establish

### Positive results are real, but conditional

* [Self-Refine (Madaan et al., 2023)](https://arxiv.org/abs/2303.17651), published March 2023, has the same LLM generate feedback on its draft and revise. Across seven evaluated tasks, human preference and automatic metrics improved by roughly 20 absolute points on average over one-shot generation. This is evidence that a structured second pass can improve *measured output quality*, especially presentation and task-local correctness; it is not proof that the model can detect its own unknown factual or architectural error.
* [Reflexion (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366), March 2023, reported gains in decision-making, coding, and reasoning by retaining verbal reflections tied to task feedback; it reported 91% pass@1 on HumanEval under its setup. Its central design includes feedback from the environment, not merely introspection. The actionable distinction is important: a failing test, compiler output, or repository search is qualitatively stronger feedback than “please reconsider.”
* [Multiagent Debate (Du et al., 2023)](https://arxiv.org/abs/2305.14325), May 2023, reported better mathematical/strategic reasoning and factual validity when multiple model instances propose and debate answers. This supports debate as a candidate-generation and error-discovery technique, but its benchmarks do not demonstrate reliable review of long-horizon, repository-specific engineering plans.
* [ReAct (Yao et al., ICLR 2023)](https://arxiv.org/pdf/2210.03629) demonstrates why grounding matters: interleaving reasoning with actions against a Wikipedia API or interactive environments reduced hallucination/error propagation and improved task success. For plan review, the analogue is inspectable repository/tool evidence, not a longer internal discussion.

### The critical counter-evidence: feedback generation is the bottleneck

* [Large Language Models Cannot Self-Correct Reasoning Yet (Huang et al., 2024)](https://deepmind.google/research/publications/48252/), first posted October 2023 and published at ICLR 2024, found intrinsic self-correction of reasoning difficult and sometimes performance-degrading when no external feedback is supplied. The study explicitly warns against assuming a revise loop is a correctness mechanism.
* [When Can LLMs Actually Correct Their Own Mistakes? (Kamoi et al., TACL 2024)](https://aclanthology.org/2024.tacl-1.78/) critically reviewed the literature and concluded that no prior work had reliable general-task evidence of successful prompted-LLM self-correction; reliable external feedback, large-scale fine-tuning, or unusually decomposable tasks were the recurring favorable conditions. This is the best high-level caution against equating “reflection” with “verification.”
* [LLMs cannot find reasoning errors, but can correct them given the error location (Tyen et al., Findings ACL 2024)](https://aclanthology.org/2024.findings-acl.826/) separates locating a mistake from repairing it. Models generally struggled to locate even objective logical errors, but correction improved when given the true location. For plan review, assign critics a concrete search target (missing requirement mapping, changed public API, untested failure path) and furnish relevant evidence rather than asking for an unconstrained critique.
* This literature is not uniformly negative. [ProCo (Wu et al., EMNLP 2024)](https://aclanthology.org/2024.emnlp-main.714/) uses a focused condition-verification prompt and reported improvements over a basic self-correction baseline (+6.8 exact match on open-domain QA, +14.1 accuracy on arithmetic, +9.6 on commonsense). The implication is *structured, checkable subclaims* help; it does not validate open-ended self-review broadly.

**Design implication.** Make reviewers test falsifiable propositions, each with an evidence request: “Does every user-visible requirement map to an implementation site and executable/observable test?” is better than “Is this plan sound?” Maintain a defect ledger with evidence links and disposition, rather than letting a debate transcript substitute for a record.

## 2. LLM-as-judge: useful evaluator, insufficient independent authority

### Empirical limitations

* [Judging the Judges: Position Bias (Shi et al., 2024/2025)](https://arxiv.org/abs/2406.07791) tested 12 judges on more than 100,000 pairwise instances across MT-Bench and DevBench. It found systematic position bias, varying by judge and task, not mere random noise. A plan judged “better” should therefore be order-swapped and, where practical, evaluated in blinded form.
* [Self-Preference Bias in LLM-as-a-Judge (Wataoka, Takahashi & Ri, 2024)](https://arxiv.org/abs/2410.21819) found GPT-4’s evaluations significantly favored lower-perplexity/familiar outputs relative to human evaluators, whether or not the output was literally self-generated. Fluent, conventional plans can therefore receive inflated ratings despite weak project fit.
* [Beyond the Surface: Measuring Self-Preference in LLM Judgments (Chen et al., EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.86/) sharpens the measurement issue: apparent self-preference can be confounded with candidate-output quality. This is a methodological warning: do not report raw judge agreement or “the reviewer preferred it” as evidence of independent validity without controlled comparisons/human or objective ground truth.
* [Learning LLM-as-a-Judge for Preference Alignment (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/hash/09fd990b19b2e69cc4d20e9969e43f09-Abstract-Conference.html) finds that training/rubric design can improve robustness relative to scalar evaluators. It supports explicit rationales and criteria, but does not eliminate the need to validate a judge against the specific plan-review task.

### Operational safeguards

* Blind author identity and randomize plan order; run A/B then B/A and flag flips.
* Demand criterion-level verdicts with cited repository evidence; prohibit a global 1–10 score as the decision rule.
* Use a model family/configuration different from the planner where feasible; more importantly, diversify *information sources* (tests, static analysis, docs, issue history, code search). Different roles with the same prompt/context do not assure independent errors.
* Maintain a small, human-adjudicated holdout set of past plans/defects. Measure per-criterion precision/recall, order consistency, and agreement with adjudication whenever the judge model/prompt changes.

## 3. Calibration, disagreement, and stopping rules

### Confidence should not be accepted at face value

* [Calibrating the Confidence of LLMs by Eliciting Fidelity (Zhang et al., EMNLP 2024)](https://aclanthology.org/2024.emnlp-main.173/) reports that RLHF models can be overconfident: expressed confidence need not match correctness. It proposes calibration methods/metrics, but the baseline fact is decisive for workflow design—“90% confident the plan is complete” is unvalidated unless calibrated on comparable plans.
* [APRICOT (Ulmer et al., ACL 2024)](https://aclanthology.org/2024.acl-long.824/) shows a separate model can estimate confidence using generated input/output text alone and can detect incorrect answers competitively in closed-book QA. It supports using confidence as a *triage feature*, not an acceptance proof; calibration is task/distribution dependent.
* [Cascaded Selective Evaluation (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/file/08dabd5345b37fffcbe335bd578b15a0-Paper-Conference.pdf) studies routing uncertain judgments to a stronger evaluator and reports better calibration/failure prediction. A practical analogue is cost-sensitive escalation: cheap mechanical checks first, then a heterogeneous reviewer, then human/domain-owner review for uncertain high-risk items.

### A defensible stopping policy

No primary source establishes a universal “N AI reviewers” or “three rounds” rule for engineering plans. The number should be a function of unclosed risk and review coverage, not artifact length alone.

Use a gate such as:

| Gate | Evidence required to stop | If it fails |
|---|---|---|
| Scope coverage | Every requirement/acceptance criterion has an implementation and verification mapping, or is explicitly deferred | Return to planner/owner |
| Grounding | Material file/symbol/dependency claims are backed by repository/docs/tool evidence | Research or ask owner; do not infer |
| Risk coverage | Security, data migration, compatibility, operations, and rollback considered when applicable | Add a perspective-specific review |
| Verification | Proposed checks can actually discriminate the change from a plausible wrong implementation | Strengthen tests/observability |
| Independence | At least one review channel has distinct evidence/model/context or a mechanical oracle | Add independent review |
| Residual uncertainty | No unresolved high-impact assumption; lower-impact items logged with owner/date | Escalate high-impact uncertainty |

Stop when those gates pass and incremental review rounds yield no *new, evidence-backed, material* defects—not when agents converge rhetorically. Continue/escalate on disagreement about a high-severity item, unverified external dependency, unclear requirement, or when expected cost of a missed defect exceeds human review cost. Log review yield (new confirmed defects per reviewer-minute/round) so the policy can be tuned locally.

## 4. Software-engineering-specific evidence: plans need traceability and observable verification

* [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) is the requirements-engineering standard; its IEEE summary says it defines good requirements and their attributes/characteristics across iterative life-cycle processes ([IEEE listing](https://standards.ieee.org/ieee/802.1Q/6937/)). It supports a plan format that identifies requirements and verification method, rather than prose-only intent.
* NASA’s [SWE-087 peer-review guidance](https://swehb.nasa.gov/spaces/SWEHBVB/pages/32604573/SWE-087%2B-%2BSoftware%2BPeer%2BReviews%2Band%2BInspections%2Bfor%2BRequirements%2BPlans%2BDesign%2BCode%2Band%2BTest%2BProcedures) applies reviews to requirements, plans, design, code, and test procedures. It calls for stakeholder-based team composition and checklists relevant to each inspector’s perspective. This supports deliberately different review lenses (e.g., API compatibility, security, operations), rather than generic duplicate critics.
* NASA’s [inspection handbook guidance](https://swehb.nasa.gov/pages/viewpage.action?navigatingVersions=true&pageId=73106126) offers a pragmatic human-review heuristic of four to six participants and reports more defects when size/document heuristics are followed. NASA’s [formal-inspection standard](https://standards.nasa.gov/sites/default/files/standards/NASA/Baseline/1/nasa-std-87399_with_change_1.pdf) also recommends no more than six and notes perspective-based preparation. **This is not evidence to run 4–6 AI agents:** AI agents can be highly correlated. It is evidence for bounded, perspective-based inspection with adequate preparation and recorded outcomes.
* [SWE-bench Verified](https://www.swebench.com/verified.html) was a human-validated set of 500 real GitHub issues, constructed because task clarity, test correctness, and solvability need validation. Yet OpenAI’s [2026 audit](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) found that, among a 27.6% audited subset commonly failed by models, at least 59.4% had flawed tests that rejected functionally correct submissions. Even a respected “verified” automated coding benchmark can have invalid or incomplete oracles. Therefore passing tests are necessary evidence but must be paired with requirement/behavior review; conversely, a failed test must be diagnosed rather than mechanically treated as plan failure.
* OpenAI’s [coding-evaluation methodology](https://openai.com/index/separating-signal-from-noise-coding-evaluations/) describes forming an independent human judgment from problem statement, tests, and reference patch before using pipeline analysis/transcripts as supporting evidence. The transferable principle is an anti-anchoring control: an adjudicator should independently inspect the artifact and relevant evidence before seeing prior agents’ persuasive rationale.

## 5. Recommended review protocol for an AI-generated engineering plan

1. **Plan schema first.** Require: goal/non-goals; assumptions; requirement IDs; exact proposed files/symbols; interfaces/data changes; migration/rollback; risk; verification; observability; owner/open questions. A requirement-to-change-to-test matrix is the core artifact.
2. **Ground the first review.** Let a reviewer inspect the repository, tests, ADRs/specs, and dependency/API docs. Its only job is to challenge unsupported mappings and missing constraints. Require citations or command/test evidence for every material claim.
3. **Run orthogonal perspectives, not clone votes.** Use focused critics: requirements/traceability; architecture/compatibility; testability/operations; security/privacy as applicable. Isolate initial reviews to reduce anchoring, then reconcile from a defect ledger.
4. **Use an adversarial pass with a concrete threat model.** Ask: “construct the smallest plausible implementation that follows this plan but violates each acceptance criterion”; “what repository fact would falsify the change map?”; “what failure would tests miss?” This turns critique into falsification attempts.
5. **Mechanically verify what can be verified.** Repository search, type/build, test discovery, API/schema compatibility, static analysis, and executable tests should challenge the plan before implementation and validate it afterward. Do not replace these with an LLM score.
6. **Adjudicate disagreement independently.** A final reviewer starts from the source requirement and artifact evidence before reading earlier reasoning. Record whether the issue is confirmed, rejected, deferred, or needs human decision—and why.
7. **Risk-route and stop.** Use calibrated historical data if available; otherwise assume verbal confidence is uncalibrated. Escalate high-impact unresolved items to an accountable human. End when the gates above pass and the latest independent pass finds no material, evidence-backed defect.

## Evidence limits and research gaps

* Most cited LLM studies use QA, reasoning, generation, or bounded coding benchmarks—not design plans for a live codebase. Transfer is an informed workflow inference, not direct proof.
* Multi-agent studies commonly use shared base models/prompts and benchmark ground truth; their observed improvement cannot be interpreted as a general guarantee of independent review.
* Engineering-inspection guidance is human-process evidence. It supports structured, perspective-based review and traceability, but does not provide an experimentally validated agent-count formula.
* “Plan quality” has no single stable oracle. A plan can be coherent yet wrong about the repository, or complete yet choose an unacceptable product trade-off. Define local acceptance criteria and collect outcome data (defects escaped, rework, review yield, implementation success) to calibrate the process.

## Suggested local experiment

Before standardizing a workflow, run a preregistered historical-study or shadow-study on representative plans/issues. Compare (A) one grounded reviewer, (B) same-model multi-agent critique, and (C) heterogeneous/perspective-based critique plus mechanical checks. Blind the adjudicator to condition. Measure requirement-coverage recall, confirmed-defect precision/recall, order-swap stability, time/cost, and defects discovered after implementation. Stratify by risk/size and report confidence intervals. Adopt the cheapest configuration that meets a predeclared error budget; do not extrapolate a benchmark win rate into a universal review-count rule.
