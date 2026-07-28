# Evidence and source guide

This is a curated map, not an exhaustive bibliography. Prefer the linked primary or first-party source over summaries when updating the knowledgebase.

## Agentic development and evaluation

- [Anthropic — Claude Code best practices](https://code.claude.com/docs/en/best-practices): staged exploration/planning/implementation, executable verification, fresh verification agents.
- [Anthropic — Subagents](https://code.claude.com/docs/en/sub-agents): context isolation, tool restriction, parallel research, and limits of inherited/forked context.
- [Anthropic — Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system): strong breadth-first results, orchestrator-worker pattern, context separation, and substantial token cost; not evidence that every coding task benefits.
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): outcome/trajectory evaluation, deterministic/model/human graders, multiple trials, maintenance, and drift.
- [OpenAI — Introducing Codex](https://openai.com/index/introducing-codex/): verifiable evidence, configured environments, and continuing need for human review.
- [OpenAI — Harness engineering](https://openai.com/index/harness-engineering/): repository legibility, enforceable boundaries, agent-to-agent review loops, and feedback converted into tooling.
- [OpenAI — Coding evaluation methodology](https://openai.com/index/separating-signal-from-noise-coding-evaluations/): independent human judgment, flawed test/oracle risks, and benchmark audit.
- [Microsoft — Sharp tools](https://www.microsoft.com/en-us/research/publication/sharp-tools-how-developers-wield-agentic-ai-in-real-software-engineering-tasks/): small real-repository study favoring iterative collaboration over one-shot use.
- [Microsoft — AgentLens](https://www.microsoft.com/en-us/research/publication/agentlens-revealing-the-lucky-pass-problem-in-swe-agent-evaluation/): successful final outcomes can conceal problematic trajectories.
- [Google Research — scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/): task topology and orchestration determine whether multiple agents help or amplify error.
- [SWE-bench Verified](https://www.swebench.com/verified.html) and [SWE-bench Live](https://arxiv.org/abs/2505.23419): executable agent evaluation plus the need for human validation, freshness, and contamination resistance.
- [METR — task time horizons](https://metr.org/time-horizons/): task length predicts agent reliability in its tested suites; do not infer that a long plan is reviewable merely because a model can stay active for hours.

## Critique, self-correction, debate, and judges

- [Self-Refine](https://arxiv.org/abs/2303.17651): iterative self-feedback improved measured outputs across several tasks; not a general correctness guarantee.
- [Reflexion](https://arxiv.org/abs/2303.11366): revision tied to environmental/task feedback.
- [Multiagent Debate](https://arxiv.org/abs/2305.14325): gains on selected reasoning/factuality tasks; transfer to repository plans is unproven.
- [Large Language Models Cannot Self-Correct Reasoning Yet](https://deepmind.google/research/publications/48252/): intrinsic self-correction can fail or degrade reasoning without external feedback.
- [When Can LLMs Actually Correct Their Own Mistakes?](https://aclanthology.org/2024.tacl-1.78/): review of conditions under which self-correction does and does not work.
- [MT-Bench / LLM-as-judge](https://arxiv.org/abs/2306.05685): useful human-preference agreement with documented position, verbosity, and self-enhancement biases.
- [Systematic position-bias study](https://arxiv.org/abs/2406.07791): position effects across judges/tasks.
- [Correlated Errors in LLMs](https://arxiv.org/abs/2506.07962): shared errors remain substantial across many models.
- [Apple — Nine Judges, Two Effective Votes](https://machinelearning.apple.com/research/correlated-llm-evaluation-panels): scaling panel size did not recover independence in tested judge panels.

## Requirements, inspection, security, and operations

- [ISO/IEC/IEEE 29148](https://www.iso.org/standard/72089.html): requirements-engineering foundation.
- [NASA SWE-087](https://swehb.nasa.gov/spaces/SWEHBVB/pages/32604573/SWE-087%2B-%2BSoftware%2BPeer%2BReviews%2Band%2BInspections%2Bfor%2BRequirements%2BPlans%2BDesign%2BCode%2Band%2BTest%2BProcedures): peer review of requirements, plans, design, code, and test procedures.
- [NIST SSDF](https://csrc.nist.gov/Projects/ssdf): risk-based secure development and qualified independent design review.
- [Microsoft secure design](https://learn.microsoft.com/en-us/azure/security/develop/secure-design): design-time threat modeling and STRIDE.
- [AWS ADR process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html): durable context, decision, consequences, and supersession.
- [AWS Operational Readiness Reviews](https://docs.aws.amazon.com/wellarchitected/latest/operational-readiness-reviews/wa-operational-readiness-reviews.html): lifecycle review questions learned from incidents.
- [Google SRE canarying](https://sre.google/workbook/canarying-releases/): partial rollout, evaluation signals, and limitations of pre-production testing.
- [Google code-review practices](https://google.github.io/eng-practices/review/reviewer/): broad context, major design first, useful tests, severity clarity, and small changes.
- [DORA — streamlining change approval](https://dora.dev/capabilities/streamlining-change-approval/): peer review and automation close to work; risk-based escalation rather than universal heavyweight gates.

## Company and practitioner reports

- [Uber — First-pass AI PRD Reviewer](https://www.uber.com/gb/en/blog/first-pass-prd/): contextual knowledge collection, risk-calibrated depth, structured scorecards, and AI upstream of human judgment. Early internal adoption is company-reported, not controlled causal proof.
- [Uber — RFCs for services](https://www.uber.com/en-CA/blog/building-tincup-microservice-implementation/): high-level service purpose/architecture/dependencies reviewed by domain engineers.
- [Shopify — Engineering program guide](https://shopify.engineering/running-engineering-program-guide): focused async RFCs, deadlines, decision rights, risks, and explicit exclusions.
- [Shopify — Roast](https://shopify.engineering/introducing-roast): discrete structured agent steps, guardrails, shared context, and session replay.
- [Shopify — Under the River](https://shopify.engineering/under-the-river): reproducible environments, public durable traces, skills, and compounding organizational learning; a first-party account, not an independent study.
- [DORA 2025 State of AI-assisted Software Development](https://dora.dev/research/2025/dora-report/): AI as an amplifier of existing organizational strengths/weaknesses and the importance of platforms and clear workflows.
- [Addy Osmani — specs for AI agents](https://addyo.substack.com/p/how-to-write-a-good-spec-for-ai-agents): practitioner synthesis on plan-first, bounded specs, and iteration.
- [Pragmatic Engineer — choosing AI developer tools](https://newsletter.pragmaticengineer.com/p/measuring-ai-dev-tools): field reports on local shootouts and measured comment usefulness; useful practice evidence, not a controlled cross-company ranking.

## Books and long-lived frameworks

- [*Software Engineering at Google*](https://research.google/pubs/software-engineering-at-google/) by Winters, Manshreck, and Wright: sustainability over time and scale, tradeoffs, code review, testing, and organizational engineering. Its practices come from Google and should be adapted rather than copied as universal rules.
- *Accelerate* by Forsgren, Humble, and Kim, together with the continuing [DORA research program](https://dora.dev/research/): empirical framing for fast feedback, small batches, delivery stability, and measuring systems rather than output volume. Use DORA capabilities as hypotheses and system-level indicators, not as a scorecard for individual agents.
- Gary Klein’s [“Performing a Project Premortem”](https://hbr.org/2007/09/performing-a-project-premortem) and *Sources of Power*: prospective hindsight makes dissent and latent failure stories easier to surface. Premortems discover plausible risks; they do not estimate probability or authorize every mitigation.
- Skelton and Pais’s [*Team Topologies*](https://teamtopologies.com/): team boundaries, cognitive load, interaction modes, and platform responsibilities are useful when a plan crosses ownership boundaries. It cautions indirectly against treating a technically complete plan as organizationally executable.
- Google’s *Site Reliability Engineering* and *SRE Workbook*, available through [sre.google](https://sre.google/): error budgets, SLOs, canaries, incident learning, and operational readiness give concrete review questions for rollout and recovery.
- Gene Kim, Jez Humble, Patrick Debois, and John Willis’s *The DevOps Handbook*: reinforces feedback, flow, telemetry, and continual learning. Prefer current DORA/SRE sources for claims that depend on newer evidence.

These books are best used as lenses and vocabulary. None establishes a validated recipe for agentic plan review.

## Transfer limits

- QA, math, and preference-judging results do not directly measure engineering-plan review.
- Code review and inspection evidence does not automatically transfer from humans to correlated model copies.
- Company blogs report practices and internal measurements under unique infrastructure; they are not universal causal evidence.
- Public benchmarks select bounded, testable tasks and may underrepresent ambiguous product policy, long migrations, and organizational coordination.
- Practitioner newsletters provide current workflow detail but often lack reproducible data and independent validation.

The proper stance is triangulation: use empirical results to identify known failure modes, industry practice to identify durable mechanisms, and local evaluation to decide whether a custom review actually works in your environment.
