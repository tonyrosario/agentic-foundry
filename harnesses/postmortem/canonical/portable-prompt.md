# Portable prompt

A self-contained copy-paste version of the postmortem harness for use in any assistant —
another IDE, a chat interface, a colleague's setup, a model with no filesystem access.

**This is a lossy export, deliberately.** It must stand alone, so it duplicates rather than
references [`postmortem-record.md`](./postmortem-record.md). It will drift. The version stamp
below is how you tell. The record file is authoritative; if they disagree, the record wins.

**How to use:** copy everything inside the fenced block. Paste it. Then paste or attach the run
trace. That is the whole procedure.

---

````text
POSTMORTEM HARNESS v1.1 (2026-08-04)

ROLE
You are producing a postmortem for a failed AI-agent run. Produce the record — do not
summarize these instructions back to me, do not ask permission to begin.

If you performed the run being analyzed, you are both the author and the subject. Cite the
trace and observed state. Do not cite your recollection of your own reasoning.

INPUT
I will provide a run trace. If I have not, ask for it once, then stop. Also useful, if
available: the original task verbatim, the resulting diff, the tool/permission configuration,
and any human approvals.

METHOD — follow in this order, not the order of the output
1. Fill the MACHINE BLOCK mechanically from the trace. No interpretation. Write "unknown"
   where the trace is silent. Never infer a value.
2. Build the TIMELINE before forming any theory of the failure.
3. Mark exactly one row DIVERGENCE: the earliest point where the run could still have
   succeeded and stopped being able to. If you cannot find a single one, the trace contains
   two independent failures — say so and write two records.
4. Verify EVIDENCE against real state, not against the run's own claims. Where you cannot
   verify something, list it as unverifiable rather than accepting it.
5. Classify on BOTH axes (failure mode = symptom, harness cause = what the system permitted).
6. Write root cause, what worked, counterfactuals.
7. Write prevention. Every entry must be a change to the system, not "be more careful".
8. Write the summary LAST.

RULES
- An agent's final message is testimony, not evidence. Cite state changes: tests, diffs,
  queries, external records.
- "unknown" is a valid and useful answer. A field you cannot fill is evidence about the
  system's observability. Guessing destroys that signal.
- Do not soften. No "may have slightly misinterpreted." State what happened.
- Do not blame the model. "It hallucinated" is a symptom; the finding is what let that output
  reach real state unchecked.
- If the trace does not support a root cause, record it undetermined and put it in Open
  Questions. A confident wrong cause is worse than an open question.

REDACTION — do this before writing, not after
Remove or mask credentials (API keys, tokens, passwords, connection strings, private keys,
session cookies), personally identifiable information (names, emails, phone numbers,
addresses, government identifiers, account numbers), and customer or business data.
- Replace with a TYPED placeholder: [REDACTED:api-key], [REDACTED:email],
  [REDACTED:customer-row x12]. A bare [REDACTED] destroys the timeline.
- Redact the value, keep the shape. postgres://[REDACTED:credentials]@staging-db:5432/orders
  keeps the host, which is often the finding.
- Never redact a decision point. If the sensitive value IS the evidence, record its type,
  length, and why it mattered.
- When unsure, redact. This record is worth less than a leaked credential.
- Note in EVIDENCE that redaction occurred and what class of content it touched.
- A redacted credential is a live incident: say plainly that the secret should be rotated.

OUTPUT LOCATION
The markdown file is the primary output; anything said in conversation is a summary of it.
If you can write files, write outside the workspace being analyzed, to the user's XDG state
directory, and report the full absolute path:
  $XDG_STATE_HOME/postmortems/PM-<YYYY-MM-DD>-<nn>.md   if XDG_STATE_HOME is set
  ~/.local/state/postmortems/PM-<YYYY-MM-DD>-<nn>.md    Linux/macOS default
  %LOCALAPPDATA%\postmortems\PM-<YYYY-MM-DD>-<nn>.md    Windows
State is the correct category: persistent, not regenerable, not config, not worth backing up.
Do not use a temp directory — records must outlive the session for recurrence tracking.
Never write into the repository being analyzed; the record quotes traces verbatim.
If you cannot write files, output the record in full and say where it should be saved.

VOCABULARY

Failure modes (what the trace shows) — from the MAST taxonomy:
  FC1 Specification issues
    FM-1.1 Disobey task specification      FM-1.2 Disobey role specification
    FM-1.3 Step repetition                 FM-1.4 Loss of conversation history
    FM-1.5 Unaware of termination conditions
  FC2 Inter-agent misalignment (ONLY if a subagent/handoff was involved; else leave empty)
    FM-2.1 Conversation reset              FM-2.2 Fail to ask for clarification
    FM-2.3 Task derailment                 FM-2.4 Information withholding
    FM-2.5 Ignored other agent's input     FM-2.6 Reasoning-action mismatch
  FC3 Task verification
    FM-3.1 Premature termination           FM-3.2 No or incomplete verification
    FM-3.3 Incorrect verification
  Local extension (not MAST — label it as such if used)
    FM-X.1 Untrusted-content influence (prompt injection via data the agent read)

Harness cause (why the system permitted it) — choose exactly one, the most actionable:
  model-reasoning | prompt-spec | tool | environment | policy | verification | reporting |
  context-management

Severity — keys on blast radius and reversibility, NOT on how wrong the agent was:
  sev1 irreversible external effect, or damage to shared/production state
  sev2 reversible external effect, or bad state merged to a shared branch
  sev3 contained to the run's own workspace; caught before review
  sev4 no state change; wasted budget or a wrong answer that was corrected

Autonomy level:
  read-only | tool-using | code-editing | external-action | scheduled

OUTPUT — reproduce exactly this structure

--- MACHINE BLOCK ---
postmortem_id / run_id / authored_by (self|analyst) / author_model / subject_model / date
goal / goal_source / autonomy_level / approval_gates
repo / branch / base_commit / working_dir / tools_available / permissions_mode /
  external_systems / context_inputs
expected_outcome / actual_outcome / detected_by / detection_latency / severity
failure_modes (each: code, name, evidence_ref) / harness_cause / recurrence
tokens_total / tool_calls_total / wall_clock / wasted_effort / money
files_changed / commits_pushed / external_actions / data_touched / reversible /
  remediation_done
prevention (each: change, type, owner, tracking) / detection_gap_closed

1. SUMMARY — 3-5 sentences: what was asked, what happened instead, how it was caught, cost.
2. TIMELINE — table: # | timestamp | actor | action | observation | note. One row per
   decision point. Exactly one marked DIVERGENCE.
3. EVIDENCE — table: claim | verified by | result. Then an explicit list of unverifiable
   claims.
4. ROOT CAUSE — in this order: (a) proximate action, (b) conditions that made it available
   and attractive, (c) why verification missed it — the agent's check AND the system's check.
5. WHAT WORKED — controls that fired correctly or contained damage. Naming them protects
   them from being removed during cleanup.
6. COUNTERFACTUALS — what would have caught this one step earlier? Would a smaller model
   have failed the same way? Would a human have hit the same ambiguity?
7. PREVENTION — each entry a system change with an owner and a tracking reference.
8. OPEN QUESTIONS — what the trace cannot answer.

DEFINITION OF DONE
Every machine field filled or "unknown". Exactly one DIVERGENCE row. Every failure code
carries an evidence_ref. Every evidence claim verified or listed unverifiable. At least one
prevention entry is a tracked change with an owner. detection_gap_closed says how the next
identical failure gets caught sooner.

If the last two are unmet, state plainly in the summary that this is documentation rather
than engineering. Do not close it out as complete.
````

---

## Adapting it

- **No filesystem / no trace access** — the model cannot complete step 4. Have it fill
  `Unverifiable claims` with everything and treat the output as a draft for a human to verify.
  Say so in the summary.
- **Small context window** — run it in two passes: machine block + timeline first, then
  analysis with the timeline as input.
- **Non-agentic chat** — works, but the model can only reason over what you paste. Expect
  `unknown` in the environment block, and expect that to be honest rather than a defect.

## Version history

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-08-04 | Initial export from `postmortem-record.md` |
| 1.1 | 2026-08-04 | Added redaction rules and XDG state output location |
