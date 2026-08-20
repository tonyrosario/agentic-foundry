<!-- GENERATED FILE — DO NOT EDIT.
     Built by scripts/build-skills.py from harnesses/postmortem/canonical/reference.md
     Edit that file and re-run the build. Direct edits here are lost and will
     fail `python3 scripts/build-skills.py --check`. -->

# Reference lists

Normative vocabulary for [`postmortem-record.md`](./postmortem-record.md). Vendor-neutral.

## Failure modes (`failure_modes[].code`)

Adapted from MAST — [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657),
NeurIPS 2025. Records what the trace **shows**.

### FC1 — Specification issues

| Code | Name |
| --- | --- |
| FM-1.1 | Disobey task specification |
| FM-1.2 | Disobey role specification |
| FM-1.3 | Step repetition |
| FM-1.4 | Loss of conversation history |
| FM-1.5 | Unaware of termination conditions |

### FC2 — Inter-agent misalignment

| Code | Name |
| --- | --- |
| FM-2.1 | Conversation reset |
| FM-2.2 | Fail to ask for clarification |
| FM-2.3 | Task derailment |
| FM-2.4 | Information withholding |
| FM-2.5 | Ignored other agent's input |
| FM-2.6 | Reasoning-action mismatch |

### FC3 — Task verification

| Code | Name |
| --- | --- |
| FM-3.1 | Premature termination |
| FM-3.2 | No or incomplete verification |
| FM-3.3 | Incorrect verification |

**FC2 applies only where a subagent, tool-as-agent, or handoff was involved.** For a solo run,
leave FC2 empty rather than stretching the codes. MAST is a multi-agent taxonomy; the stretch is
tempting and destroys comparability.

**Local extension.** MAST has no code for an agent successfully manipulated by content it read.
Until a validated taxonomy covers it, use:

| Code | Name |
| --- | --- |
| FM-X.1 | Untrusted-content influence (prompt injection via read data) |

Marked `X` because it is ours, not MAST's. Do not report it as a MAST finding.

## Harness causes (`harness_cause`)

Records why the harness **permitted** the failure. Exactly one, the most actionable.

| Class | Meaning |
| --- | --- |
| `model-reasoning` | Wrong plan, wrong assumption, missed constraint — with the spec and tools adequate |
| `prompt-spec` | Success criteria were ambiguous, contradictory, or absent |
| `tool` | A tool returned bad data, timed out, or hid an error |
| `environment` | Dependencies, credentials, network, branch, or test data were wrong |
| `policy` | An action proceeded that should have required approval |
| `verification` | The check was not run, or its output was misread |
| `reporting` | The final answer omitted risk or overstated success |
| `context-management` | Needed information was compacted, truncated, or never retrieved |

Both axes are required. A code alone is not actionable; a cause alone is not comparable across
runs.

## Severity (`severity`)

| Sev | Meaning | Default author |
| --- | --- | --- |
| sev1 | Irreversible external effect, or damage to shared/production state | Analyst |
| sev2 | Reversible external effect, or bad state merged to a shared branch | Analyst |
| sev3 | Contained to the run's own branch/worktree; caught before review | Self |
| sev4 | No state change; wasted budget or a wrong answer delivered and corrected | Self, abbreviated |

Severity keys on **blast radius and reversibility**, not on how wrong the agent was. A
confidently wrong answer that changed nothing is sev4. A correct-looking change pushed to a
shared branch is sev2.

## Autonomy levels (`autonomy_level`)

| Level | Meaning |
| --- | --- |
| `read-only` | Could observe but not act |
| `tool-using` | Could call tools with no persistent effect |
| `code-editing` | Could modify files in its own workspace |
| `external-action` | Could affect systems or people outside the workspace |
| `scheduled` | Ran unattended, with no human present to interrupt |

## Provenance

Severity scale, `harness_cause` list, and FM-X.1 are this harness's own constructions, not
drawn from validated external work. See the knowledgebase for what is evidenced and what is
borrowed judgement.
