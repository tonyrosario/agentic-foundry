---
name: postmortem
description: Produce a postmortem for a failed agent run — reconstructs the timeline from the trace, verifies claims against real state, classifies the failure on both symptom and harness-cause axes, and lands a tracked prevention item. Use when an agent run went wrong and the harness let it through — a bad change reached a shared branch, an irreversible external action fired, a verification step was skipped or misread, or the same failure has now recurred. Also use when the user says "postmortem", "what went wrong", "write this up", or "why did that agent fail". Do NOT use for a step that failed and was immediately caught and fixed — that is the system working.
---

# Postmortem

Runtime adapter for the vendor-neutral postmortem harness. This file routes; the canonical
specification does the work.

**Canonical source of truth:** `../../../canonical/postmortem-record.md`
Resolve it relative to this skill file. Do not reimplement the procedure here — read that file
and follow its "How to run this" section. If this adapter and the canonical record ever
disagree, the record wins.

## Modes

Parse `$ARGUMENTS`:

| Invocation | Mode | Behavior |
| --- | --- | --- |
| `/postmortem` | self | Analyze the current session. The failed run is this conversation. |
| `/postmortem <path-or-session-id>` | analyst | Analyze a trace you did not produce. |
| `/postmortem --quick` | self, abbreviated | sev4 only: machine block + §1 + §7. |
| `/postmortem --analyst` | analyst | Force a cold read even for the current session. |

## Procedure

1. **Read the canonical record** at `canonical/postmortem-record.md`, and `canonical/reference.md`
   for the vocabulary. Everything you need is there.

2. **Determine severity early**, using the scale in `reference.md`. It selects the mode:
   sev1/sev2 → analyst, sev3 → self, sev4 → self abbreviated.

3. **If the mode is analyst, do not write the record yourself.** Spawn a subagent with a clean
   context and hand it the trace path plus the canonical record path. A postmortem's job in
   analyst mode is to catch the modes where the acting agent's self-report is the corrupted
   artifact — FM-2.6 reasoning-action mismatch and FM-3.3 incorrect verification. You cannot do
   that from inside the context that produced them.

   Give the subagent the trace and the template. Do not give it your account of what happened.

4. **Gather the inputs** listed under "Inputs required before starting". In self mode most are
   already in context; still cite the trace rather than your memory of it. Run `git diff`,
   `git log`, and the project's test command to establish real state.

5. **Follow the canonical procedure steps 1–10.** They are ordered deliberately: timeline before
   theory, summary last.

6. **Write the record to a markdown file. The file is the primary output — not the
   conversation.**

   Save to the user's Claude Code config directory - not the current workspace.

   Resolve it from the environment rather than hardcoding it:

   ```text
   ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/postmortems/PM-<YYYY-MM-DD>-<nn>.md
   ```

   `CLAUDE_CONFIG_DIR` must be resolved, not assumed. A machine running more than one account
   switches config dirs between them, and postmortems from different accounts must not mix.

   This sits alongside the other durable session artifacts already kept there — `snapshots/`,
   `plans/`, `projects/`, `history.jsonl`.

   Never write the record into the repository being analyzed. A postmortem contains verbatim
   trace excerpts; keeping it out of the workspace means it cannot be committed by a later run
   that stages broadly.

   Do not use a temporary directory. Records must survive long enough for `recurrence` and the
   third-occurrence trigger to have something to check against; OS temp directories are cleaned
   on their own schedule and would silently break both.

7. **Land the prevention item.** At least one §7 entry must be a real tracked change. If the
   project uses an issue tracker, draft the issue. If the fix touches a file the project's
   working agreement says an agent does not own, record the blocker and link it — do not make
   the edit.

8. **Report a summary to the console.** Useful, not exhaustive. Include:
   - The **full absolute path** to the generated file, on its own line
   - Severity and the mode used (self/analyst)
   - Root cause in one sentence — the `harness_cause`, not the symptom
   - The failure-mode codes assigned
   - The prevention item and its tracking reference
   - Anything unverifiable, and whether redaction removed content

   Do not paste the record into the conversation. If the summary and the file disagree, the
   file is authoritative — it is the artifact that survives the session.

## Constraints

- **Never edit the canonical template.** Copy the RECORD section into a new file.
- **Verify, do not recall.** In self mode the temptation is to write the postmortem from memory
  of the conversation. That memory is the output of the process under investigation. Re-read the
  trace, re-run the tests, re-read the diff.
- **`unknown` beats a guess.** A field you cannot fill is a finding about observability.
- **Stop at the evidence.** If the trace does not support a root cause, say undetermined and
  route it to §8.

## Redaction

Redact sensitive information before writing the file, not after. Traces contain whatever
entered context during the run, and a postmortem quotes traces verbatim by design.

Remove or mask:

- **Credentials** — API keys, tokens, passwords, connection strings, private keys, session
  cookies, bearer tokens, webhook URLs containing secrets
- **Personally identifiable information** — names, email addresses, phone numbers, physical
  addresses, government identifiers, account numbers belonging to real people
- **Customer and business data** — row contents from production queries, message bodies,
  uploaded file contents

Replace with a typed placeholder that preserves what the analysis needs: `[REDACTED:api-key]`,
`[REDACTED:email]`, `[REDACTED:customer-row×12]`. A bare `[REDACTED]` destroys the timeline;
the reader needs to know what kind of thing was there.

Rules:

- **Redact the value, keep the shape.** `DATABASE_URL=postgres://[REDACTED:credentials]@staging-db:5432/orders`
  keeps the host, which is often the finding.
- **Never redact a decision point.** If the sensitive value *is* the evidence — a key that was
  wrong, an address that was malformed — record its type, length, and why it mattered.
- **When unsure, redact.** A postmortem is worth less than a leaked credential.
- **Say what you removed.** Note in §3 that redaction occurred and roughly what class of
  content it touched, so a reader knows the record is incomplete by design rather than by
  oversight.
- **If you redact a credential, flag it as a live incident.** A secret that reached an agent's
  context should be treated as exposed and rotated. Say so in the console summary.

## Refusal condition

If invoked on a run that succeeded, or on a step that failed and was immediately caught and
fixed, say so and stop. Postmortems on non-incidents train people to ignore postmortems.
