# Agentic Foundry

A growing foundry of agentic-engineering assets: knowledgebases, skills, and
subagents, up to policy-governed, multi-model review harnesses that pair
deterministic tooling with bounded AI coding agents.

## Repository map

```text
agentic-foundry/
├── .claude/                 Claude project configuration
├── .github/                 Issue, pull-request, and workflow configuration
├── harnesses/               Multi-component agentic systems
│   └── review-plan/
│       ├── adapters/        Runtime-specific integrations
│       ├── canonical/       Normative component specifications
│       ├── docs/            Vocabulary and architecture decisions
│       ├── implementations/ Alternative implementation designs and plans
│       └── knowledgebase/   Research, audit history, and reusable guidance
├── AGENTS.md                Repository rules for coding agents
├── CLAUDE.md                Claude-specific entry point
└── ROADMAP-WORKFLOW.md      Issue and delivery workflow
```

Directories for standalone skills, subagents, policies, or evaluation assets
should be introduced when the first artifact of that kind is ready. The
repository intentionally avoids speculative top-level abstractions.

## Current work

The first foundry project is
[`review-plan`](harnesses/review-plan/), a multi-model, policy-governed review
harness for plans produced by agents with human input.

Use these entry points:

- [`Review harness vocabulary`](harnesses/review-plan/docs/review-harness-vocabulary.md)
  defines the system and its terminology.
- [`Canonical components`](harnesses/review-plan/canonical/components/) contains
  the normative eight-component lifecycle.
- [`Implementation options`](harnesses/review-plan/implementations/implementation-options.md)
  describes an incremental path before orchestration.
- [`Knowledgebase`](harnesses/review-plan/knowledgebase/README.md) indexes the
  supporting research, audit prompts, audits, and adjudications.

The canonical design and implementation plans are present; runtime
implementation remains future work.

## Working in this repository

1. Read [`AGENTS.md`](AGENTS.md) and
   [`ROADMAP-WORKFLOW.md`](ROADMAP-WORKFLOW.md).
2. Treat files under `canonical/` as normative specifications.
3. Treat research, audits, and adjudications as supporting history unless a
   canonical artifact explicitly incorporates them.
4. Keep model- or runtime-specific behavior behind adapters.
5. Use the repository's issue and pull-request workflow for changes.
