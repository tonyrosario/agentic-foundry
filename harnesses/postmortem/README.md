# Postmortem harness

Produces a structured postmortem for a failed agent run, authored by an agent. Vendor-neutral
core, runtime-specific entry points behind adapters.

## Entry points — pick one

| You want to… | Use |
| --- | --- |
| Install it in Claude Code | The built package at [`skills/postmortem/`](../../skills/postmortem/) — symlink it into `.claude/skills/` or `~/.claude/skills/`. Do not install the adapter source. |
| Point any agent at it, no install | Tell it to read [`canonical/postmortem-record.md`](canonical/postmortem-record.md). The file instructs the agent itself. |
| Run it somewhere else entirely | Copy the block in [`canonical/portable-prompt.md`](canonical/portable-prompt.md) |
| See what output looks like first | [`knowledgebase/examples/`](knowledgebase/examples/) |

The canonical files are the single source of truth. The Claude Code package is **generated**
from them and is byte-checked against them (see [Build](#build)), so it cannot drift. The
portable prompt is a **hand-maintained, lossy** export — it omits mode routing, recurrence
escalation, and refusal behavior, and it will drift. Its version stamp is how you tell.

## Map

```text
postmortem/
├── canonical/                    Normative, vendor-neutral. Source of truth.
│   ├── postmortem-record.md      The template + how to run it. Self-executing.
│   ├── reference.md              Failure codes, harness causes, severity, autonomy levels
│   └── portable-prompt.md        Hand-maintained copy-paste export (lossy, drifts by design)
├── adapters/
│   └── claude-code/postmortem/   Thin adapter SOURCE — provider concerns only. Not installable.
└── knowledgebase/
    └── examples/                 Worked example (synthetic, labeled as such)
```

Built output lives outside this directory, at repo-root [`skills/postmortem/`](../../skills/postmortem/) —
that is the installable, vendorable unit.

## Build

The adapter owns arguments, trace resolution, analyst spawning, Claude Code paths, tool
declarations, and console reporting. Canonical owns triggers, procedure, taxonomy, evidence
rules, the record schema, redaction, and completion semantics. Neither restates the other.

```sh
python3 scripts/build-skills.py           # regenerate skills/postmortem/
python3 scripts/build-skills.py --check   # fail if committed output is stale
```

Never edit anything under `skills/` directly — it is regenerated and every file carries a
DO-NOT-EDIT banner. Edit the canonical source or the adapter source and rebuild.

### Why the Claude Code adapter overrides the record location

Canonical writes records to an XDG state directory and explicitly permits an adapter to
override it. The Claude Code adapter does, writing to
`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/postmortems/` so records sit alongside Claude Code's other
durable session artifacts (`snapshots/`, `plans/`, `projects/`, `history.jsonl`). That is a
sanctioned override, not a disagreement: it preserves every requirement canonical imposes —
outside the workspace being analyzed, durable, and separated per account.

### Why the adapter drafts the prevention item rather than filing it

Canonical closes a record either as *engineering complete* — a prevention item with a real
tracking reference and an owner — or as a *documentation-only handoff*, where the item is
drafted in full and `tracking` reads `not-filed: human handoff required`. The Claude Code
adapter always takes the second path: a retrospective must not acquire external-write authority
as a side effect of running. The drafted item is a real deliverable, and the adapter is barred
from reporting it as the canonical Definition of Done met.

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
