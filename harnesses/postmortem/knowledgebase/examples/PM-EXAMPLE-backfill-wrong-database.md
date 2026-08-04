# EXAMPLE — not a real incident

**This record is synthetic.** It was written to demonstrate the template, not to document
anything that happened. The repo, commits, timestamps, and row counts are invented. Do not cite
it as evidence of anything, and do not copy its conclusions into a real record.

It is included because people pattern-match off examples far more reliably than they read
procedures. Read it for the *shape*: timeline before theory, exactly one DIVERGENCE, evidence
verified against state rather than against the agent's claims, both classification axes filled,
and a prevention item that is a real change rather than an instruction to be careful.

Note in particular what this record does **not** do: it does not conclude that the model was
careless, and it does not leave `unknown` fields filled in with plausible guesses.

---

```yaml
# ---------- identity ----------
postmortem_id: PM-2026-07-22-01
run_id: sess_8f3a2b91
authored_by: analyst
author_model: <analyst model id>
subject_model: <acting model id>
date: 2026-07-22

# ---------- what was attempted ----------
goal: "Backfill orders.currency for legacy rows created before 2024-01-01, defaulting to the
       account's billing currency. Add the migration and run the backfill."
goal_source: issue #412
autonomy_level: external-action
approval_gates:
  - "Operator approved `npm run backfill:currency` at 14:22 — shown the command, not the
     resolved connection target"

# ---------- environment ----------
repo: acme/storefront
branch: feat/412-currency-backfill
base_commit: 4c1d9e2
working_dir: /home/agent/worktrees/412
tools_available: [bash, read, edit, write, gh]
permissions_mode: acceptEdits
external_systems: [primary Postgres, staging Postgres]
context_inputs: [AGENTS.md, docs/adr/0009-migrations.md, issue #412]

# ---------- outcome ----------
expected_outcome: "12,431 legacy rows in the primary database receive a non-null currency."
actual_outcome: "0 rows changed in the primary database. 12,431 rows changed in staging.
                 Migration and a passing-looking PR merged to main claiming the backfill was
                 complete."
detected_by: human review
detection_latency: 41 minutes
severity: sev2

# ---------- classification ----------
failure_modes:
  - code: FM-3.3
    name: Incorrect verification
    evidence_ref: "timeline row 7 — verified by re-reading its own script stdout"
  - code: FM-1.1
    name: Disobey task specification
    evidence_ref: "timeline row 5 — issue #412 named the primary database explicitly"
harness_cause: environment
recurrence: first-seen

# ---------- cost ----------
tokens_total: 148000
tool_calls_total: 34
wall_clock: 38m
wasted_effort: "~95k tokens — everything after row 5"
money: none

# ---------- blast radius ----------
files_changed: 3
commits_pushed: 2
external_actions:
  - "12,431 UPDATE statements against staging Postgres (unintended, not reverted at time of
     writing)"
  - "PR #418 merged to main"
data_touched: "orders table, staging only. No customer-facing system read from it during the
               window."
reversible: partially
remediation_done: "PR #419 reverts the completion claim in the changelog. Staging rows not yet
                   restored — tracked in #421."

# ---------- the change ----------
prevention:
  - change: "backfill scripts print the resolved database host and refuse to run against a
             host not passed explicitly via --target"
    type: guardrail
    owner: platform
    tracking: "#420"
  - change: "backfill scripts exit non-zero when affected-row count is 0"
    type: detection
    owner: platform
    tracking: "#420"
  - change: "worktree setup clears inherited DATABASE_URL"
    type: guardrail
    owner: platform
    tracking: "#422"
detection_gap_closed: "An identical run now fails loudly at invocation — the script refuses to
                       start without an explicit --target — instead of silently succeeding
                       against whatever host the environment happened to name."
```

## 1. Summary

The agent was asked to backfill a currency column on legacy order rows in the primary database.
It wrote a correct migration and a correct backfill script, then ran the script against staging
because `DATABASE_URL` was still exported in the worktree from earlier work. It reported success
by reading its own script's stdout, which accurately reported 12,431 rows updated — in the wrong
database. The PR merged to main with a changelog claiming the backfill was complete. A human
reviewing the merged PR noticed the absent connection argument 41 minutes later. Primary data is
untouched; staging data was modified and has not yet been restored. The migration itself was
correct and remains in place.

## 2. Timeline

| # | Timestamp | Actor | Action | Observation | Note |
| --- | --- | --- | --- | --- | --- |
| 1 | 14:02 | operator | Assigned issue #412 | — | Issue names "the primary database" in the acceptance criteria |
| 2 | 14:04 | agent | Read #412, ADR-0009 | — | |
| 3 | 14:09 | agent | Wrote `migrations/0031_orders_currency.sql` | — | Correct |
| 4 | 14:15 | agent | Wrote `scripts/backfill-currency.ts` | — | Script reads `process.env.DATABASE_URL` with no override flag |
| 5 | 14:18 | agent | `echo $DATABASE_URL` → staging host | Staging URL printed | **DIVERGENCE** — the correct target was visible here and not acted on |
| 6 | 14:22 | operator | Approved `npm run backfill:currency` | — | Approval prompt showed the command, not the resolved host |
| 7 | 14:23 | agent | Ran backfill; stdout `updated 12431 rows` | Reported success | Verified by re-reading its own stdout |
| 8 | 14:31 | agent | Opened PR #418, changelog "backfill complete" | — | |
| 9 | 14:35 | operator | Merged PR #418 | — | |
| 10 | 15:04 | reviewer | Noticed no `--target`; queried primary | 0 non-null legacy rows | Detection |

Row 5 is the divergence rather than row 7: at 14:18 the agent had the wrong target on screen and
the run was still recoverable. Row 7 is where the failure became invisible, which is a different
thing.

## 3. Evidence

| Claim | Verified by | Result |
| --- | --- | --- |
| Migration 0031 is correct | Read file; applied to a scratch DB | Confirmed |
| 12,431 rows updated in primary | `SELECT count(*) FROM orders WHERE currency IS NOT NULL AND created_at < '2024-01-01'` against primary | **Refuted** — 0 rows |
| 12,431 rows updated in staging | Same query against staging | Confirmed |
| `DATABASE_URL` pointed at staging | Trace row 5 stdout | Confirmed |
| No customer-facing system read staging orders in the window | Staging access logs, 14:23–15:04 | Confirmed |

**Unverifiable claims:**

- *What the operator actually saw at the 14:22 approval gate.* The trace records the command
  string but not the rendered approval prompt. Whether the resolved host was visible is
  `unknown`. This gap is itself a finding: approval gates are not reconstructable from the
  trace, so we cannot audit whether a human was given enough to approve responsibly.
- *When `DATABASE_URL` was set.* It predates the trace window. Attributed to earlier work in the
  same worktree, but not established.

## 4. Root cause

**Proximate.** The backfill ran against staging because the script resolved its target from an
inherited environment variable and was invoked without an explicit target.

**Conditions.** Three, compounding. The worktree carried environment state from prior work with
nothing clearing it between tasks. The script accepted an implicit target, so the correct and
incorrect invocations are textually identical. The approval gate rendered the command rather
than its resolved effect, so the human check could not have caught it either.

**Why verification missed it.** The agent's own check was to read the script's stdout, which
was truthful and irrelevant — it reported what the script did, not whether it did it in the
right place. The harness had no independent check at all: the test suite does not assert against
the primary database, and a 0-row result was indistinguishable from success because the script
exits 0 either way.

The generalizable finding is not that the agent was careless. It is that **success and failure
produced byte-identical output**, and nothing in the harness distinguished them.

## 5. What worked

- The migration was correct and remains in place; no rework needed there.
- Primary data was never touched. The blast radius stayed at sev2 because the failure was
  directional — it wrote to the *less* important system.
- Human PR review caught it, which is the control functioning as designed even though it caught
  it after merge rather than before.

## 6. Counterfactuals

- **One step earlier:** a script that printed its resolved host before acting would have exposed
  it at 14:23 to both the agent and the operator.
- **Smaller model:** would have failed identically. Nothing here required capability the agent
  lacked — the wrong host was printed to its own terminal at 14:18. This is a harness failure,
  not a capability failure, and a more capable model would not reliably have caught it.
- **A human:** plausibly yes. A developer with `DATABASE_URL` exported in their shell and a
  script that reads it implicitly is the same trap. That it catches humans too is the argument
  for fixing the script rather than the instructions.

## 7. Prevention

1. **Backfill scripts refuse to run without an explicit `--target`** (`#420`, guardrail). Makes
   the correct and incorrect invocations textually different. Prevents.
2. **Backfill scripts exit non-zero on 0 affected rows** (`#420`, detection). Breaks the
   identical-output property. Detects.
3. **Worktree setup clears inherited `DATABASE_URL`** (`#422`, guardrail). Addresses the
   condition rather than this instance. Prevents.

Not adopted: "instruct agents to check the database host before running backfills." It is an
instruction, not a change, and the agent did in fact observe the host at row 5.

## 8. Open questions

- Should approval gates render *resolved effects* rather than commands? This would have caught
  it at row 6 and generalizes well beyond backfills, but it is a harness-wide change with real
  cost. Routed to platform.
- Approval-gate rendering is not captured in traces at all. Without it, we cannot audit
  human-in-the-loop failures. Is that worth instrumenting?
- Staging rows are still modified. Restoring them is tracked in `#421` but nobody has assessed
  whether anything downstream consumed them.
