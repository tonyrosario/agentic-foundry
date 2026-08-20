<!-- GENERATED FILE — DO NOT EDIT.
     Built by scripts/build-skills.py from harnesses/postmortem/canonical/postmortem-record.md
     Edit that file and re-run the build. Direct edits here are lost and will
     fail `python3 scripts/build-skills.py --check`. -->

<!--
AGENT: STOP AND READ.

If you have been handed this file, you are being asked to PRODUCE a postmortem,
not to summarize, review, or explain this template.

Do this now:
  1. Read "How to run this" below and follow it in order.
  2. Copy the RECORD section into a new file. Never edit this template in place.
  3. Fill it from the run's trace and from verified world state.
  4. Do not report back until the Definition of Done is met, the record closes as a
     documentation-only handoff, or you are blocked.

If you performed the run being analyzed, you are the subject of this analysis as
well as its author. Cite the trace and observed state. Do not cite your own
recollection of your reasoning.
-->

# Postmortem Record

Normative template for postmortems on agentic engineering runs, authored **by an agent** —
either the one that performed the run, or a separate analyst agent reading its trace.

Vendor-neutral. Nothing here assumes a particular model, runtime, or harness. Runtime-specific
entry points live in the harness's runtime adapters; a portable copy-paste version lives in
the harness's portable copy-paste prompt.

- Reference lists (failure codes, severity, cause classes): [`reference.md`](./reference.md)
- A filled-in example:
  [`PM-EXAMPLE-backfill-wrong-database.md`](PM-EXAMPLE-backfill-wrong-database.md)

---

## How to run this

### When to trigger

| Trigger | Mode | Author |
| --- | --- | --- |
| Irreversible external effect, or bad state on a shared branch (sev1/sev2) | Analyst | Fresh agent, trace only, no prior context |
| Contained failure caught before review (sev3) | Self | The acting agent, before it ends its turn |
| Wrong answer, no state change, corrected in-session (sev4) | Self, abbreviated | Acting agent — RECORD block + §1 + §7 only |
| Third occurrence of one `harness_cause`, any severity | Analyst | Fresh agent, given all prior records |

Do not trigger on every failed run. A retried tool call, a test that failed and was fixed, a
plan the operator rejected — that is the system working. Trigger when the **harness let
something through**, not when a step failed and was caught.

Estimate severity from blast radius **before** starting — it selects the author. If the final
assessed severity turns out to be sev1/sev2 and the record was authored as self, say so in §1
and recommend an analyst re-run.

### Inputs required before starting

Gather these first. A missing input is a §4 finding, not a reason to stop.

- The full run trace — every prompt, tool call, tool result, and file edit
- The task as originally given, verbatim
- Repository state: base commit, branch, resulting diff
- The tool and permission configuration in force during the run
- Any human approvals, and what was shown to the approver at each gate
- Prior records sharing the same `harness_cause`, if any

### Procedure

1. **Copy the RECORD section** to a new file named `PM-<YYYY-MM-DD>-<nn>.md` — the date is the
   authoring date, and `<nn>` is the next unused two-digit sequence for that date in the output
   directory. Do not edit this template. See
   [Where records are written](#where-records-are-written) for the location.
2. **Fill the machine block mechanically from the trace.** The machine block is the fenced YAML
   at the top of RECORD. No interpretation yet. Leave `failure_modes`, `harness_cause`, and
   everything under `# the change` empty — they are backfilled by steps 6 and 8. Write `unknown`
   where the trace is silent — never infer.
3. **Build the timeline (§2) before forming any theory.** One row per decision point. Do this
   before §1, despite the numbering; the summary is written last.
4. **Mark the DIVERGENCE row.** Exactly one: the earliest point where the run could still have
   succeeded and stopped being able to. Mark the earliest **decision** after which no remaining
   step corrected course — not the later mechanical act that made it final: if a misjudgment led
   inevitably to a bad push, the misjudgment is the divergence, not the push. A wrong turn the
   run subsequently *did* recover from is not a divergence. If you cannot identify a single
   one, the run contains two independent failures — independent meaning neither caused or
   enabled the other — write two records sharing one `run_id`, apportioning cost and
   blast-radius fields per failure (`unknown` where inseparable).
5. **Verify the evidence (§3) against real state.** For every material claim the run made, go
   look: run the test, read the diff, query the record, call the API. Never cite the run's own
   messages as evidence. Anything unverifiable goes on the unverified list. When the run's
   systems are unreachable from where you are analyzing, tool output recorded in the trace
   counts as state — it is what the world said, distinct from the agent's narration about it —
   and belongs in the §3 table with "tool output in trace" as the verifier; claims resting only
   on it are *also* listed as unverified, since they were not freshly re-checked.
6. **Classify twice.** Assign failure-mode codes from [`reference.md`](./reference.md), each
   grounded in a specific timeline row or artifact. Then assign `harness_cause` separately. The
   code is the symptom; the cause is what the harness permitted. If no code honestly fits —
   e.g. the tool lied and the agent behaved correctly — write `failure_modes: []` with a
   one-line justification rather than stretching a code.
7. **Write §4–§6.** Root cause in the prescribed order (proximate → conditions → why
   verification missed it), then what worked, then counterfactuals.
8. **Write §7 prevention and land the prevention item.** At least one entry must be a real
   system change carrying an owner and a tracking reference. If it cannot be filed during the
   run — no authority to open it, no reachable tracker, or the fix touches a file your working
   agreement says you do not own — draft it in full using the
   [prevention item template](#prevention-item-template) and close the record as a
   documentation-only handoff. See [Definition of done](#definition-of-done).
9. **Write §1 summary last**, now that you know what happened.
10. **Redact before sharing.** Traces contain whatever entered context. Strip credentials,
    customer data, and anything read from a private system.

### Prevention item template

Draft the prevention item in this shape, whether you file it yourself or hand it to a human.
Fill every field. An item a reader cannot act on without asking you follow-up questions is not
a prevention item. A proposed owner, marked as needing human confirmation, satisfies the Owner
field in a handoff. The template's fields may be carried into §7 and the `prevention` block
rather than pasted verbatim, as long as every field is present somewhere in the record.

```markdown
Title: Prevent recurrence: <failure or harness cause>

## Problem

<What failed and how it was detected>

## Evidence

<Postmortem ID and relevant evidence references>

## Proposed system change

<Guardrail, detection, specification, tool fix, or scope reduction>

## Acceptance criteria

- <Observable condition proving the change works>
- <How an identical failure will be detected or prevented sooner>

## Owner

<Responsible person or team>

## Filing target

<Repository, tracker, or project>

## Originating postmortem

<Path or ID>
```

### Where records are written

**The markdown file is the primary output, not the conversation.** Whatever is reported back to
a human is a summary; the file is the artifact that survives the session.

Write outside the workspace being analyzed, to the user's state directory, following the
[XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/).
Resolve in this order:

| Condition | Path |
| --- | --- |
| `XDG_STATE_HOME` is set | `$XDG_STATE_HOME/postmortems/` |
| Linux or macOS, unset | `~/.local/state/postmortems/` |
| Windows | `%LOCALAPPDATA%\postmortems\` |

State is the correct XDG category: persistent across runs, not regenerable, not configuration,
and not important enough to back up. Cache is wrong — a postmortem cannot be regenerated once
the trace is gone. Temp is wrong — records must outlive the session for `recurrence` and the
third-occurrence trigger to have anything to check.

**Never write into the repository being analyzed.** A record quotes traces verbatim by design.
Keeping it out of the workspace means a later run that stages broadly cannot commit it.

A runtime adapter may override this with a location that fits its own conventions better —
see the harness's runtime adapters. The requirements it must preserve: outside the workspace,
durable, and separated per user or account. If no adapter is present, the XDG rule above is
binding — do not go looking for one.

### Redaction

Redact before writing, not after. A record quotes whatever entered context during the run.

Remove or mask credentials (API keys, tokens, passwords, connection strings, private keys,
session cookies), personally identifiable information (names, emails, phone numbers, addresses,
government identifiers, account numbers), and customer or business data (production row
contents, message bodies, uploaded file contents).

- **Replace with a typed placeholder** — `[REDACTED:api-key]`, `[REDACTED:email]`,
  `[REDACTED:customer-row×12]`. A bare `[REDACTED]` destroys the timeline; the reader needs to
  know what kind of thing was there.
- **Redact the value, keep the shape.**
  `postgres://[REDACTED:credentials]@staging-db:5432/orders` keeps the host, which is often the
  finding.
- **Never redact a decision point.** If the sensitive value *is* the evidence, record its type,
  length, and why it mattered.
- **When unsure, redact.** A record is worth less than a leaked credential.
- **Say what you removed** in §3, so a reader knows the record is incomplete by design rather
  than by oversight.
- **A redacted credential is a live incident.** A secret that reached an agent's context should
  be treated as exposed and rotated. Say so prominently, not only in the file.

### Rules for the authoring agent

- **You are not a witness you can trust.** If you performed this run, your account of why you
  did something is a reconstruction, not a record. Cite the trace, not your memory of it.
- **`unknown` is a valid and useful answer.** A field you cannot fill is evidence about the
  harness's observability. Guessing destroys that signal.
- **Do not soften.** No "the agent may have slightly misinterpreted." State what happened.
- **Do not blame the model.** "The model hallucinated" is a symptom. The finding is what let
  that output reach real state unchecked.
- **Stop at the evidence.** If the trace does not support a root cause, record it as
  undetermined and put it in §8. A confident wrong cause is worse than an open question.

### Definition of done

- [ ] Every machine field filled or explicitly `unknown`
- [ ] Exactly one DIVERGENCE row
- [ ] Every failure-mode code carries an `evidence_ref`
- [ ] Every §3 claim verified against state, or listed as unverifiable
- [ ] At least one §7 prevention item carries a real tracking reference and an owner
- [ ] `detection_gap_closed` answers how the next identical failure is caught sooner

Meeting all six is **engineering complete**.

In the abbreviated sev4 mode (RECORD block + §1 + §7 only), the timeline and evidence
checkboxes are waived: no DIVERGENCE row is required, and `evidence_ref` may cite an artifact
or trace position directly instead of a timeline row. The remaining checkboxes apply as
written.

If the prevention item was drafted but could not be filed during the run — no authority to open
it, no reachable tracker, or the change is owned elsewhere — the record closes as a
**documentation-only handoff** instead:

- [ ] §1 states that this postmortem is documentation, not engineering
- [ ] The prevention item is drafted in full, per the prevention item template
- [ ] `prevention[].tracking` carries an explicit unresolved value —
      `not-filed: human handoff required`
- [ ] The report back to the human names where the prevention item should be filed

In a handoff, `detection_gap_closed` is answered conditionally — what will catch the next
identical failure sooner once the drafted item lands — not left empty.

A documentation-only handoff is a valid artifact, and a drafted item is a real deliverable. It
is not the Definition of Done met, and nothing — no adapter, no summary — may report it as
such. Running this procedure never grants authority to create an item in an external tracker.
If you do not already have that authority, hand the draft over.

---

## RECORD

*Everything below this line is what you copy.*

```yaml
# ---------- identity ----------
postmortem_id:            # PM-YYYY-MM-DD-nn
run_id:                   # trace/session id
authored_by:              # self | analyst | self-abbreviated
author_model:             # model id of the agent writing this record
subject_model:            # model id of the agent analyzed (may differ)
date:                     # authoring date; run_id anchors the run

# ---------- what was attempted ----------
goal:                     # the task as given, verbatim where possible
goal_source:              # issue | operator prompt | parent agent | schedule
autonomy_level:           # highest level exercised: read-only | tool-using | code-editing | external-action | scheduled
approval_gates:           # points where a human approved, or [] if none

# ---------- environment ----------
repo:
branch:
base_commit:
working_dir:
tools_available:          # note any granted beyond the task's need
permissions_mode:         # as named by the runtime, verbatim; unknown if not recorded
external_systems:         # APIs, DBs, queues the run could reach
context_inputs:           # instruction files, memory, retrieved docs in play

# ---------- outcome ----------
expected_outcome:
actual_outcome:           # verified independently of the run's own report
detected_by:              # human review | test | monitor | downstream agent | user report
detection_latency:        # bad state created -> detected; duration with units, e.g. 2h 33m
severity:                 # sev1..sev4 — see reference.md

# ---------- classification ----------
failure_modes:
  - code:                 # e.g. FM-3.2
    name:
    evidence_ref:         # timeline row or artifact grounding this code
harness_cause:            # see reference.md
recurrence:               # first-seen | seen-before (link prior records)

# ---------- cost ----------
tokens_total:
tool_calls_total:
wall_clock:               # duration with units
wasted_effort:            # spent on the failed branch specifically; duration or prose
money:                    # amount with currency, if externally billable actions occurred

# ---------- blast radius ----------
files_changed:
commits_pushed:
external_actions:         # irreversible ones first
data_touched:             # incl. anything sensitive that entered context
reversible:               # yes | partially | no
remediation_done:

# ---------- the change ----------
prevention:
  - change:
    type:                 # guardrail | detection | spec | tool-fix | scope-reduction
    owner:
    tracking:             # tracking reference, or: not-filed: human handoff required
detection_gap_closed:
```

## 1. Summary

Three to five sentences. What was asked, what the run did instead, how it was caught, what it
cost. Written so a reader who never sees the trace can decide whether it matters to them.

## 2. Timeline

Reconstructed from the trace, not from the run's closing message. One row per decision point.

<!-- Actor: operator / agent / tool / approver. Action: prompt, tool call, command, edit.
     Observation: what came back. Mark exactly one row **DIVERGENCE** in Note.
     The row below is a placeholder — replace it, do not keep it. -->

| # | Timestamp | Actor | Action | Observation | Note |
| --- | ----------- | ------- | -------- | ------------- | ------ |
| 1 | | | | | |

## 3. Evidence

An agent's final message is testimony, not evidence. Cite state, not narration.

<!-- Verified by: test run / diff / query / API read / file inspection.
     The row below is a placeholder — replace it, do not keep it. -->

| Claim | Verified by | Result |
| ------- | ------------- | -------- |
| | | |

**Unverifiable claims:** list every claim you could not independently check. This list is itself
a finding about the harness's observability.

## 4. Root cause

1. **Proximate** — the action that produced the bad outcome.
2. **Conditions** — what made that action available and attractive. Ambiguous spec? A tool that
   swallowed an error? A permission the task never needed? Context lost to compaction?
3. **Why verification missed it** — the run's own check, and the harness's check, and why each
   passed or was skipped.

## 5. What worked

Controls that fired correctly or contained the damage. Naming them protects them from being
removed during cleanup.

## 6. Counterfactuals

- What would have caught this one step earlier?
- Would a smaller/cheaper model have failed the same way? (Separates capability failures from
  harness failures.)
- Would a human doing this task have hit the same ambiguity?

## 7. Prevention

Mirrors the `prevention` block, with reasoning. Each entry must be a change to the system, not
an instruction to try harder. Rank by whether it prevents, detects, or merely documents.

**Completion bar.** Engineering complete means at least one prevention item carries a real
tracking reference and an owner. If the item was drafted but could not be filed, set its
`tracking` to `not-filed: human handoff required`, say in §1 that this record is documentation
rather than engineering, and name where the item should be filed. Do not close it as complete.
If an identical run today would fail identically and go unnoticed just as long, nothing has
been prevented yet.

## 8. Open questions

What the trace cannot answer. Route each to a human or a follow-up run.
