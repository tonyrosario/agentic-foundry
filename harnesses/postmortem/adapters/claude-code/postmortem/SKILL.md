---
name: postmortem
argument-hint: "[path-or-session-id | --quick | --analyst]"
compatibility: "Claude Code. Requires ${CLAUDE_SKILL_DIR} substitution (v2.1.129+)."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
disable-model-invocation: true
description: Produce a postmortem for a failed agent run — reconstructs the timeline from the trace, verifies claims against real state, classifies the failure on both symptom and harness-cause axes, and drafts a tracked prevention item for a human to file. Use when an agent run went wrong and the harness let it through — a bad change reached a shared branch, an irreversible external action fired, a verification step was skipped or misread, or the same failure has now recurred. Also use when the user says "postmortem", "what went wrong", "write this up", or "why did that agent fail". Do NOT use for a step that failed and was immediately caught and fixed — that is the system working.
---

# Postmortem

Claude Code adapter for the vendor-neutral postmortem harness. This file owns **provider
concerns only**: argument parsing, trace resolution, analyst spawning, Claude Code paths, and
console reporting.

**Everything else is canonical and lives elsewhere.** Triggers, procedure, taxonomy, evidence
rules, the record schema, redaction, and completion semantics are defined in
`../../../canonical/postmortem-record.md` and `../../../canonical/reference.md`. Do not
reimplement any of it here. If this adapter and the canonical record disagree on anything
canonical owns, the canonical record wins.

## Modes

Parse `$ARGUMENTS`:

| Invocation | Mode | Behavior |
| --- | --- | --- |
| `/postmortem` | self | Analyze the current session. The failed run is this conversation. |
| `/postmortem <path-or-session-id>` | analyst | Analyze a trace you did not produce. |
| `/postmortem --quick` | self, abbreviated | sev4 only: machine block + §1 + §7. |
| `/postmortem --analyst` | analyst | Force a cold read even for the current session. |

## Trace resolution

Resolve `$ARGUMENTS` to a concrete trace before doing anything else. A postmortem written
without the trace in hand is testimony, which is the thing this harness exists to distrust.

| Argument shape | Resolution |
| --- | --- |
| A path that exists | Use it directly. |
| A bare session UUID | `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/<project-slug>/<uuid>.jsonl`. The slug is the project path with `/` replaced by `-`. Glob across `projects/` if the project is not known. |
| Absent (current session) | The conversation itself is the trace. In `--analyst` mode it must be **exported to a file** before the subagent is spawned — the subagent cannot see this conversation. |

If the trace cannot be located, say so and stop. Do not proceed from recollection.

## Procedure

1. **Read the canonical record** at `../../../canonical/postmortem-record.md`, and
   `../../../canonical/reference.md` for the vocabulary. Everything you need is there. A worked
   example of a finished record is at
   `../../../knowledgebase/examples/PM-EXAMPLE-backfill-wrong-database.md`.

2. **Determine severity early**, using the scale in `../../../canonical/reference.md`. It selects the mode:
   sev1/sev2 → analyst, sev3 → self, sev4 → self abbreviated.

3. **If the mode is analyst, do not write the record yourself.** Gather the inputs first (step
   4), then spawn a subagent with a clean context. A postmortem's job in analyst mode is to
   catch the modes where the acting agent's self-report is the corrupted artifact — FM-2.6
   reasoning-action mismatch and FM-3.3 incorrect verification. You cannot do that from inside
   the context that produced them.

   Hand the subagent the resolved trace, the canonical record path, and the gathered inputs.
   **Do not give it your account of what happened.**

   When it returns, validate its output against the canonical Definition of Done before
   reporting. An unvalidated subagent result is the same unchecked testimony in a fresh voice.

4. **Gather the inputs** listed under "Inputs required before starting" in the canonical record.
   In self mode most are already in context; still cite the trace rather than your memory of it.
   Run `git diff`, `git log`, and the project's test command to establish real state.

5. **Follow the canonical record's procedure steps 1–10.** They are ordered deliberately:
   timeline before theory, summary last.

6. **Write the record file. It is the primary output — not the conversation.**

   Write it here, overriding the canonical record's XDG state directory:

   ```text
   ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/postmortems/PM-<YYYY-MM-DD>-<nn>.md
   ```

   The record must stay outside the workspace being analyzed. `CLAUDE_CONFIG_DIR` must be
   resolved, not assumed — a machine switches config dirs between accounts, and records from
   different accounts must not mix.

   Allocate `<nn>` by listing the directory and taking the next free index for that date.

7. **Draft the prevention item; do not open it.** Running this skill grants no authority to
   create an item in an external tracker. Draft it in full using the prevention item template in
   the canonical record, set `tracking` to `not-filed: human handoff required`, and present it
   for a human to file. That is the canonical **documentation-only handoff** — a valid artifact,
   and not engineering completion. Only an item filed during the run, with a real tracking
   reference and an owner, meets the canonical Definition of Done.

8. **Re-open the record file and validate it** against the canonical Definition of Done before
   reporting anything. Confirm the machine block parses and the required sections are present.
   A drafted, unfiled prevention item is a valid documentation-only handoff — check that §1 says
   the postmortem is documentation rather than engineering, and do not report the Definition of
   Done as met. If validation fails, fix the file; do not report success.

9. **Report a console summary of at most 8 lines**, covering:
   - The **full absolute path** to the record file, on its own line
   - Severity, the mode used (self/analyst), and the failure-mode codes assigned
   - Root cause in one sentence — the `harness_cause`, not the symptom
   - The drafted prevention item, where it should be filed, and that it remains unfiled
   - Anything unverifiable, and whether redaction removed content

   Do not paste the record into the conversation. If the summary and the file disagree, the
   file is authoritative — it is the artifact that survives the session.

## Redaction

Canonical, and non-optional: see the **Redaction** section of the canonical record. Apply it
before writing the file. If it caused a credential to be redacted, surface that in the console
summary as a live incident.

## Triggers, evidence rules, and completion

Canonical. See "When to trigger", "Rules for the authoring agent", and "Definition of done" in
the canonical record — including its two closing outcomes, engineering complete and
documentation-only handoff.
