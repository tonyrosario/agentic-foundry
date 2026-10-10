# Audit of the graphify payoff plan

Date: 2026-10-10. Auditor: Claude Fable 5.1, independent session.
Plan under review: /tmp/graphify-payoff-plan.md (prepared at commit 54d9806).
Checkout: /Users/tonyrosario/dev/tealhq-clone, branch main. Working tree clean before and after.
No files in the repository or `local/` were changed. No graph rebuild was run.

## Summary

The plan is well constructed but is not ready to run as written. Four factual claims in
"what is known today" are wrong or unreproducible, one leakage path is unaddressed, the
decision rules have an overlap and a gap, and the budget covers only one of the three
phases that spend agent tokens.

## Verdicts

| # | Criterion | Verdict | Evidence | Revision if refuted |
|---|---|---|---|---|
| 1 | Decision and goal clear, every measure used | REFUTED | Sections 1, 2 and 7 are clear. But M2 (tool calls) and M5 (wasted reads) appear in no acceptance rule. M6 is used only in the "inconclusive" fallback with no threshold. The "safer" leg of the goal (missed dependents while editing) has no measure in Phase 2; Phase 1 is declared descriptive only. | Add M2 and M5 to a rule or label them diagnostic. Give M6 a threshold. State that the "safer" goal is not tested by this plan, or add a bounded full-milestone pair. |
| 2 | Criteria fixed, every result pattern maps to one outcome | REFUTED | Overlap: the B clause "M3/M4 favour the graph by 0.10 while M1 is worse" has no "majority of milestones" condition, so one milestone can satisfy B while C also holds. Overlap: no evaluation order between the arm rules and the "inconclusive" spread rule, so a result can satisfy A and inconclusive at once. Gap: "decide on overhead alone" names no mapping from M6 to A, B or C. | Evaluate the spread rule first. Add "on at least 2 of 3 milestones" to the B trade-off clause. Define the M6 mapping or drop it. |
| 3 | Confounds controlled | REFUTED | Leakage: a git worktree shares refs with the main repo, so `git log --all`, `git branch`, `git reflog` or `git fetch origin` in the worktree exposes the real M15, M16 and M17a commits. The plan controls only the graph build. Model: the plan says build sessions were Opus 5.5, but "go m15" and "go m16" were issued in session e7c59fde, which ran on claude-fable-5-1 (334 assistant turns, 2026-10-09 16:52 to 19:22 UTC; the M15 tick c5178f0 at 17:31 UTC and the M16 tick 9738747 at 18:26 UTC both fall inside it). Only "go m17a" (session a902b56d) ran on Opus. Arm N leaves `.claude/CLAUDE.md`, which names the `/graphify` skill. Stopping point: no rule for a run that never writes PLAN.md or starts editing. Order randomisation and the base-commit graph build are correct. No user-level hook or skill mentions graphify, and no global graphify state exists outside the repo, so the worktree edits do isolate the arms on that front. | Use a fresh clone at the base commit with the remote removed, not a worktree. Scan each transcript for `--all`, branch names or fetches and discard hits. Pick one model and say the historical baseline is mixed. Remove `.claude/CLAUDE.md` in arm N. Add a rule for runs with no PLAN.md. |
| 4 | Measures objective; judgement blinded, raw figure kept | CONFIRMED | Section 6: scripts over transcripts and git. Phase 3 step 2: blind grader gets base commit, spec and item with graphify mentions removed; both scores reported. Note: a plan that cites `graphify-out` paths or graph vocabulary can still reveal its arm. | Strip those too, and record whether the grader guessed the arm. |
| 5 | Honest about power | CONFIRMED | Section 7 last paragraph and section 9 first bullet: 3 milestones x 2 repetitions, no significance tests, ranges reported, inconclusive when spread dominates. | Measuring run-to-run spread from the three existing "start the next milestone" sessions in Phase 0 would help set thresholds. |
| 6 | "What is known today" accurate | REFUTED | Reproduced: 766/766 imports and 0/103 CSS (my grep found 103 CSS-module imports), 260 source files, graphify 0.9.74, no `app/` change between de9d2cf and 54d9806, hook matchers Bash\|Grep and Read\|Glob in `.claude/settings.json`, 13/18 and 14/18 retrieval, 10/10 affected, tool calls (2,353 by my count over a superset of sessions versus 2,329), graph calls (25 versus 22), session date range 2026-10-03 to 2026-10-10. Not reproduced: six claims listed below. | Correct the items below and state the unstated limits. |
| 7 | Cost estimated and approved first | REFUTED | Phase 0 step 2 and section 10 cover Phase 2 only. Phase 1 is headed "no agent runs" yet step 1 uses "an agent working blind". Phase 3's blind grader is also an agent run. Neither is in the budget. | Add Phase 1 and Phase 3 agent costs to the approved budget, and fix the Phase 1 heading. |
| 8 | No hard rule broken | CONFIRMED | Section 10 names the dogfood database, captures, remotes, worktree commits and `graphify update app` from the worktree root. Reviews under `local/` hold no personal data. A remote-less clone (criterion 3 fix) stays within the "one private remote" rule since nothing is added to the main repo. | None. |
| 9 | Missing alternatives or unmeasured failure modes | REFUTED | Cheaper first step: M6 (reminder tokens, query output tokens, CLAUDE.md section) is computable now from saved transcripts with no agent runs. If it is small relative to session cost, A versus B is minor and the real question is B versus C, which the existing accuracy work largely answers. Unmeasured: refresh cost (`graphify update app` twice per milestone, its output tokens and wall time), and misses that appear only while editing. The guide's freshness signal (add, rename, move, delete produce expected graph changes, with refresh delay) is only partly covered by the ghost-file check and three planted defects. | Run the M6 computation as Phase 0 step 0 and let the human decide whether Phase 2 is still worth it. Add refresh cost to M6. |
| 10 | Neutrality | CONFIRMED, one note | Thresholds are symmetric between options and "any other pattern" names no default. One passage tilts: section 7 "decide on overhead (M6) alone" can only count against A, because no benefit measure is paired with it. The task choice (M15 to M17a) has rich build-plan file hints in every arm, which section 9 acknowledges as the intended comparison. | Pair M6 with G1 or a benefit figure in the fallback, or drop the fallback. |

## Claims I could not reproduce

1. **Graphify adoption relative to M2** (section 8, Phase 1). The plan says it was adopted
   after M2 and that M0 to M2 predate it. Commit 516a393 added graphify at 22:05 UTC on
   2026-10-03. The M2 review covers range 6345758..300c53f, and every commit in it is later.
   Only M0 and M1 predate the graph.
2. **"20 saved reviews" at `local/M*-review/review.md`.** That glob matches 19. The twentieth
   is `local/M0-review-haiku-build/review.md`, which the pattern misses.
3. **Reminders, 1,056** (section 3.2). Deduplicating hook attachments by tool-use ID across
   all 50 transcript files (27 main sessions plus subagents) gives 917. Both the Bash and the
   Read hook texts contain "MANDATORY" and both were counted. The plan's figure is higher
   than a count over a superset of sessions, so the dedup key differs. The ratio of roughly
   40 to 50 reminders per graph call holds either way.
4. **74/670 app files committed in a session window** (section 3.2). A date-range count over
   2026-10-03 to 2026-10-10 gives 904 file-commit entries and 357 unique files under `app/`.
   Neither matches 670. The definition needs stating before the number is reused.
5. **Calls table** (section 3.1). Seven call questions are reported as 4/5 plus 0/3. C5 (a
   test body calling its own same-name `settle`) is counted in both rows.
6. **Model of the build sessions** (section 8, controls). Stated as Opus 5.5. M15 and M16
   were built on Fable 5.1 in one session. M17a was started on Opus at 17:04 UTC on
   2026-10-10 after an earlier session overran its context, and all M17a commits land
   between 17:14 and 17:25 UTC, so its baseline orientation cost is not a clean
   single-session figure.

Unchecked: the 13/20/18/49 percent "first named by" split, and the 25-session count. I
count 27 transcripts, which includes the audit session and the session that wrote the plan.

## Coverage of the validation guide

- Claim 1 (graph correct): covered by section 3.1 with a maintainer-written answer set and
  planted defects. Freshness is covered only for deletions after the fact, not for
  add/rename/move with measured refresh delay.
- Claim 2 (integration used): covered by section 3.2.
- Claim 3 (workflow improves): Phase 2 addresses it, but stops at orientation. The guide's
  "paired tasks with reviewed outcomes and behavioural tests" is not reached.
- Economics: agent cost is budgeted; indexing and refresh cost is not separated out.
- Failures: the guide asks to report variation and failures, not only successful runs. The
  plan has no rule for failed runs.

## Recommendation

Not ready as written. Before Phase 2, in this order:

1. Correct section 3 as listed above and add the model and session-restart limits.
2. Replace worktrees with remote-less clones at the base commit, and add the transcript
   scan for ref leakage.
3. Fix the acceptance rules: spread rule first, majority condition on the B trade-off
   clause, a defined M6 mapping, and a rule for runs that never write PLAN.md.
4. Put Phase 1 and Phase 3 agent costs into the approved budget.
5. Compute M6 from existing transcripts first. If the overhead is small, the human may
   decide Phase 2 is not needed and the decision is between B and C on accuracy alone.

Phases 0 and 1 are safe to run once item 1 is done. Phase 2 should wait for all five.
