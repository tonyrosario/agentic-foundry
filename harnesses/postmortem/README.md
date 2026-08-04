# Postmortem harness

Produces a structured postmortem for a failed agent run, authored by an agent. Vendor-neutral
core, runtime-specific entry points behind adapters.

## Entry points — pick one

| You want to… | Use |
| --- | --- |
| Run it in Claude Code | `/postmortem` — see [`adapters/claude-code/postmortem/`](adapters/claude-code/postmortem/SKILL.md) |
| Point any agent at it, no install | Tell it to read [`canonical/postmortem-record.md`](canonical/postmortem-record.md). The file instructs the agent itself. |
| Run it somewhere else entirely | Copy the block in [`canonical/portable-prompt.md`](canonical/portable-prompt.md) |
| See what output looks like first | [`knowledgebase/examples/`](knowledgebase/examples/) |

All four produce the same record. The canonical template is the single source of truth; the
adapters route to it and the portable prompt is a version-stamped export of it.

## Map

```text
postmortem/
├── canonical/                    Normative, vendor-neutral
│   ├── postmortem-record.md      The template + how to run it. Self-executing.
│   ├── reference.md              Failure codes, harness causes, severity, autonomy levels
│   └── portable-prompt.md        Self-contained copy-paste export (lossy by design)
├── adapters/
│   └── claude-code/postmortem/   /postmortem skill
└── knowledgebase/
    └── examples/                 Worked example (synthetic, labeled as such)
```

## What it is for

Not every failed run. Trigger when the **harness let something through** — a bad change reached
a shared branch, an irreversible external action fired, verification was skipped or misread, or
the same failure has recurred. A step that failed and was caught is the system working.

## The two ideas doing the work

**Testimony is not evidence.** An agent's closing summary is the output of the same process
under investigation. The record requires claims to be verified against real state — tests,
diffs, queries, external records — and requires unverifiable claims to be listed as such. That
list is a finding about observability.

**Classify twice.** The failure-mode code records what the trace *shows*; `harness_cause`
records what the system *permitted*. A code alone is not actionable. A cause alone is not
comparable across runs.

## Status

Design complete, unvalidated. Nothing here has been filled out against a real incident. The
severity scale, the `harness_cause` classes, and the FM-X.1 injection extension are this
harness's own constructions rather than validated external work — see
[`canonical/reference.md`](canonical/reference.md).

Supporting research, source captures, limitations, and open questions currently live in the
`allocation-decision-engine` repository at `kb/postmortem-methods/`. Consolidating that into
[`knowledgebase/`](knowledgebase/) here is outstanding.

## Provenance

The failure-mode taxonomy is adapted from
[MAST](https://arxiv.org/abs/2503.13657) (NeurIPS 2025). Timeline/action-item discipline is
standard SRE postmortem practice. The autonomy-level and evidence-over-testimony framing comes
from practitioner work; the machine-block field names track
[OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/blog/2026/genai-observability/).
Full source list and confidence assessment in the research knowledgebase.
