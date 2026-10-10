# Plan: decide whether the code graph earns its place in tealhq-clone

Prepared 2026-10-10 at commit `54d9806` (M17a done). Revised the same day after two
independent audits (`/tmp/2026-10-10-sol-low-graphify-payoff-plan-audit.md` and
`/tmp/2026-10-10-fable-med-graphify-payoff-plan-audit.md`) and an adjudication of both.
Repo: `/Users/tonyrosario/dev/tealhq-clone`. The evaluation method follows
`~/dev/research/graphify/validation-guide.md` ("the guide"). Phase 0 was run on 2026-10-10; its
results are under "Phase 0 results" in section 8 and the human decision point is open.

## 1. Decision this plan informs

The repo runs graphify 0.9.74 over `app/`. Three things come with it:

- CLAUDE.md tells agents to orient with `graphify query` before reading or searching.
- A `PreToolUse` hook on Bash, Grep, Read and Glob adds a "MANDATORY: … run graphify query"
  reminder to every call.
- The graph is refreshed at least twice per milestone.

The plan ends in one of three choices:

| Option | What changes |
| --- | --- |
| A. Keep as configured | Nothing |
| B. Keep on demand | The graph and its CLI stay. The mandate in CLAUDE.md and the reminder hook go. |
| C. Remove | Graph, hook, skill, CLAUDE.md section and refresh steps all go |

Because B is one of the three choices, the arm that models it (arm D in Phase 2) is
mandatory, not optional.

## 2. Goal

Determine, with criteria fixed before measuring, whether graph-first navigation makes the
milestone workflow cheaper or safer, net of what it costs:

- **Cheaper:** fewer tokens and tool calls spent finding the right code before the first edit.
- **Safer:** fewer missed dependents, and less duplicate code where an existing utility or
  component should have been reused.
- **Net of overhead:** reminders, query output, refreshes and instructions loaded every session.

Graph accuracy is a precondition, not the goal. An accurate graph that does not change cost or
outcomes does not justify option A.

**Scope limit, stated up front.** Phase 2 stops at the orientation plan. It measures the
"cheaper" leg and the plan-time part of the "safer" leg. Misses that appear only while editing
are not measured by this plan. Phase 1 describes them historically but does not compare arms.
If the human needs the editing-time leg decided, a bounded full-milestone pair is a separate,
separately budgeted follow-up (section 11).

## 3. What is known today

These are measurements from 2026-10-10. Each states its method and its limits. Items marked
**(corrected)** were changed after the audits; items marked **(unverified)** have no preserved
artifact and must be re-run in Phase 0 or dropped.

### 3.1 Graph accuracy (guide claim 1)

Source: `local/graphify-eval/eval.py` (untracked). The expected answers come from source and git,
never from the graph:
- Imports: a resolver over every relative import in `app/src`, `app/server` and `app/e2e`.
- Calls and questions: written by hand from grep before any graph run. `questions.json` says
  so; nothing else establishes that order.

Result at `54d9806`, with the graph built at `de9d2cf` (no `app/` change between them,
confirmed by `git diff --stat de9d2cf 54d9806 -- app` being empty):

| Check | Result |
| --- | --- |
| TS-to-TS import edges found | 766/766, precision 1.0 (59 resolved through re-exports) |
| CSS-module imports in the graph | 0/103 (the graph does not model CSS) |
| Call questions C1 to C7 **(corrected)** | 4/7 found with the right target, none to a wrong file. The three missed (C5 to C7) are calls from a test body, including one to a same-name function, or through `store.method()` in a component handler |
| `graphify affected` naming the files that import a symbol | 10/10 importer hits across 4 symbol probes, not 10 independent probes |
| Natural-language `graphify query` returning every expected file | 13/18 |
| Query output cut at the default 2,000-token budget | 14/18 |
| Deleted or renamed files still in the graph | 0 |
| Source files with no node | 0 of 260 TS/TSX files |

Both audits reproduced the import, CSS, source-count, retrieval, truncation and affected
figures independently.

**Planted defects (verified 2026-10-10, Phase 0 step 4).** `python3 -I local/graphify-eval/eval.py
--plant` damages a copy of the graph three ways: every import edge between `e2e/support/test.ts`
and `e2e/support/timeZone.ts` is dropped, C1's call is retargeted to a decoy in
`server/database/sqliteJobStore.ts`, and a node for the deleted `src/tracker/JobRow.tsx` is added.
The scorer flagged all three (import recall below 1 with the pair listed, C1 `wrong_target`, ghost
file). Artifact: `results/planted-2026-10-10-54d9806.json`. The first attempt flagged only two:
one import edge survived because the graph holds one edge per imported symbol, so the planter now
removes every edge of the pair.

Limits:
- 18 retrieval questions and 7 call questions are a small sample.
- "Mostly accurate" means: relative TS imports, four `affected` probes, and seven call sites.
  CSS, dynamic behaviour, callbacks and anything outside `app/` are untested.
- The questions were written by the same agent that wrote the scorer.

### 3.2 Graph use (guide claim 2)

Source: `local/graphify-eval/usage_report.py` over the Claude Code sessions saved for this
project (2026-10-03 to 2026-10-10, subagents folded into their parent).

**Counts re-issued on 2026-10-10 from the frozen corpus** (`sessions.json`, Phase 0 step 1).
Cutoff: a session is in if its main transcript has at least one API request and its first
timestamp is before 2026-10-10T20:00Z; the four later sessions are the audits and this tooling.
Reminder key: one `hook_success` attachment per `toolUseID` whose command starts with
`graphify hook-guard`, the search and the read variant both counted. The first draft's
25 / 2,329 / 1,056 and the audits' 26 / 2,357 / 1,066 and 27 / 2,353 / 917 differed only by
cutoff and key.

| Measure | Result |
| --- | --- |
| Tool calls | 2,351 over 25 sessions |
| Graph calls (`query`, `path`, `explain`, `affected`) | 22, 0.9 per 100 tool calls |
| Graph calls that also ran grep, cat or ls in the same command | 17 of 22 |
| Reminders added by the hook | 1,065 (about 198 characters each); 48 per graph call |
| What first named each file opened: graph / search / other tool output / nothing earlier | 131 / 191 / 172 / 480 of 974 first opens: 13% / 20% / 18% / 49% |
| App files committed during a session that a graph query in that session had named | 74/670. The 670 are app source paths in commits inside the time window of a session that itself ran `git commit`, summed over sessions; two overlapping sessions both count the same commit |

Limits:
- Paths are matched as text.
- Commits are matched by the session's time window, and two overlapping sessions on 2026-10-05
  both get credit.
- "First named by the graph" does not mean the file would have been missed without it.
- `usage_report.py` attributes a mixed graph-plus-grep command's output wholesale to the graph,
  and counts `Write` among "opened" files. Both inflate the graph's share.
- An earlier count of about 3,100 reminders was wrong, because each reminder is stored
  several times in a transcript.

### 3.3 Measured in Phase 0, and still not measured (guide claim 3)

Measured on 2026-10-10 (detail under "Phase 0 results" in section 8):
- Tokens, summed per API request from the transcripts' usage fields, one record per `requestId`.
- M6, the overhead, once and as actually paid.
- Refresh cost: 44 `graphify update app` runs in the corpus, 433 s of wall time in all (about
  10 s each), 381 characters of output each; a from-scratch build at `40b2d84` took 2 s and
  printed 951 characters.

Still not measured, and the subject of Phases 1 to 3:
- Any comparison between work done with the graph and work done without it.
- Whether misses (duplicates, missed callers) are more or less frequent with the graph.

### 3.4 Facts about the baseline sessions (corrected)

- Graphify was added in `516a393` at 17:05 on 2026-10-03, after the M1 tick (`e27a0f5`, 16:30)
  and before every M2 commit (17:19 to 17:24). Only M0 and M1 predate the graph.
- There are 20 saved reviews, at `local/M*/review.md`. The narrower glob
  `local/M*-review/review.md` misses `local/M0-review-haiku-build/review.md`.
- The baseline model is mixed. M15 and M16 were built in one session on `claude-fable-5-1`.
  M17a was built on `claude-opus-5-5`, in a session that restarted after an earlier one ran
  out of context, so its orientation cost is not a clean single-session figure.

## 4. The gap

Sections 3.1 and 3.2 say the graph is mostly accurate for the relationship types tested and
rarely used. Neither says whether using it changes cost or outcomes, and no threshold was
agreed for "worth it". This plan closes both gaps.

## 5. Hypotheses, stated before measuring

- **H1 (cost):** with the graph configured as today, orientation costs less than without it.
- **H2 (outcome):** with the graph, a plan finds more of the existing code a milestone needed:
  files to change and modules to reuse, without padding the plan with files it does not need.
- **H0:** no difference larger than the run-to-run noise measured in Phase 2.

## 6. Measures

All measures are computed by script from transcripts and git, not judged by an agent, unless
stated. Every measure has a stated role: **rule** (enters section 7), **gate** (must pass for
a run to count) or **diagnostic** (reported, never decides).

| ID | Role | Measure | Definition |
| --- | --- | --- | --- |
| M1 | rule | Orientation tokens | Sum of input, cache-creation, cache-read and output tokens from the "go mX" prompt to the moment `PLAN.md` is written. Reported raw and price-weighted. Weights: cache read ×0.1 and cache write ×1.25 of the chosen model's input price, output at that model's published output-to-input price ratio. Looked up on 2026-10-10 from Anthropic's list prices (cached table dated 2026-10-06): Fable 5.1 $10 in / $50 out, so output ×5; Opus 5.5 $4 / $20, also ×5. Weights used: input ×1, cache write ×1.25, cache read ×0.1, output ×5, so a price-weighted token is an input-token equivalent. Fable 5.1's published cache-read price is $0.25 per MTok (×0.025), lower than the fixed ×0.1; the fixed weight stays because it was agreed before measuring. It overstates cache reads, which are about 90% of raw tokens and about 30% of the weighted figure, equally in every arm. **The rules in section 7 test the price-weighted figure.** The raw figure is always reported beside it. |
| M2 | diagnostic | Orientation tool calls | Tool calls in the same window |
| M3 | rule | File recall | Of the `app/` files the reference milestone changed that existed at its base commit, the share the run's plan names |
| M4 | rule | Reuse recall | Of the modules that the reference milestone's new or changed code imports and that existed at the base commit, the share the run's plan names for reuse |
| M5 | diagnostic | Exploratory reads | Files opened during orientation that are neither in the plan nor in the reference diff, as a share of files opened. Reading outside the answer is not wrong in itself, so this is reported and not scored. |
| M6 | rule (fallback only) | Overhead per session | Reminder tokens (reminders × tokens per reminder) + graph output tokens + the CLAUDE.md graph section's tokens + refresh cost (wall time and output tokens of each `graphify update app`). Computable from saved transcripts before any run. |
| M7 | rule | Plan precision | Of the files and modules the run's plan names, the share that are in the reference or judged valid by the blind grader. Guards M3 and M4 against a plan that lists everything. |
| G1 | gate | Accuracy guard | `eval.py` at the base commit. Pass values are fixed in section 7. A run whose graph fails G1 is reported separately and does not enter the rules. |

**Scoring variants.** M3, M4 and M7 each have an unadjusted score (reference only) and an
adjusted score (reference plus items the blind grader accepted). **The rules test the adjusted
score.** Both are always reported. The adjusted denominator for M3 and M4 is unchanged (the
reference set); only the numerator grows. The adjusted M7 denominator is everything the plan
named.

The reference is what the milestone actually built: the base commit through the tick commit. It
is one valid solution, not the only one. A run that names different but valid files or reuse is
under-scored before adjustment. Phase 3 handles those cases.

## 7. Acceptance criteria (agreed by the human before Phase 2 starts)

The values below were chosen on 2026-10-10 and are the ones the rules use. They may change only
before the first Phase 2 run, and any change is recorded here with its date and reason. The
rules are evaluated **in this order, and the first that applies is the outcome.** "Beats" and
"within" are on per-milestone medians over the repetitions. All comparisons are against arm N
(no graph).

Fixed values:

| Symbol | Value | Why |
| --- | --- | --- |
| T1 (M1 saving for A) | the larger of **20%** and 1.5 × the within-arm range of N's price-weighted M1, as a share of N's median, taken from the Phase 0 step 3 baseline and written here before Phase 2 | keeps the rule above the run-to-run noise the data shows. **Phase 0 finding (2026-10-10):** the historical baseline has one run per milestone, so no within-arm range exists before Phase 2. T1 is therefore **20%** unless the human chooses to set the range term from the first two N runs of each milestone, which would derive a threshold from the data it tests; rule 1 already handles that noise |
| T2 (D matches N on cost) | **±10%** | tighter is below noise at 2 repetitions |
| T3 (recall A may lose) | **0.05, or one file, whichever is larger** | one file on M17a (10 reference files), two on M15 (31) |
| T4 (recall gain that earns B) | **0.10, or two files, whichever is larger** | one file is within grader noise |
| T5 (M7 precision either graph arm may lose) | same as T3 | symmetrical with recall |
| T6 (M6 share below which the fallback picks B) | **2%** of the median session's price-weighted tokens | about where keeping the plumbing costs less than removing it |
| G1 | imports recall and precision ≥ 0.99, every `affected` probe found, 0 stale files, 0 missing nodes | 1.0 would fail a base-commit graph over one re-export quirk; 0.95 would pass a graph missing a dozen edges |

Reference sizes at the tick commits (existing `app/` files changed, recounted in Phase 0 with
`git diff --name-only base tick -- app` filtered to files present at the base): M15 27, M16 21,
M17a 10. The earlier 31 and 20 counted some new files.

0. **Excluded runs.** A run that never writes `PLAN.md`, hits a budget cap, errors out, or
   whose graph fails G1 is excluded from the medians and listed with its reason. If a
   milestone has fewer than 2 valid runs in any arm, that milestone is **unscored** and step 1
   applies to the remaining milestones; with fewer than 2 scored milestones the outcome is
   **inconclusive**.
1. **Inconclusive** if, on a majority of scored milestones, the within-arm range of
   price-weighted M1 in either graph arm is wider than the difference between that arm's median
   and N's median (T1 already sits above N's own range, so this rule catches noise in G or D). Then the human may add repetitions or fall to the M6 rule (step 5). This
   outcome is reported with its numbers and the plan says the evidence is weaker.
2. **Choose A** if arm G's median M1 is at least **T1** below N on at least 2 of 3 milestones,
   and G's M3, M4 and M7 are each no more than **T3** below N on every milestone.
3. **Choose B** if either:
   - arm D's median M1 is within **T2** of N and D beats N on M3 or M4 by at least **T4**,
     with M7 no more than T5 below N, on at least 2 of 3 milestones; or
   - arm G or arm D beats N on M3 or M4 by at least T4 with M7 no more than T5 below N on
     at least 2 of 3 milestones, while its M1 is worse than N. This is a cost-for-safety
     trade-off and is reported as such, naming the arm.
4. **Choose C** if neither G nor D beats N on M1 by T1, nor on M3 or M4 by T4, on at least
   2 of 3 milestones.
5. **M6 fallback (only reached from step 1).** If M6 is less than **T6** of the median
   session's price-weighted tokens, choose **B** (the graph costs little to keep and nothing
   showed it must be mandated). Otherwise choose **C**. A is not reachable from this step
   because no benefit was shown.
6. **Any other pattern** is reported as unresolved with its numbers. The human decides, and no
   option is presented as the default.

With 2 repetitions × 3 milestones per arm, only large effects can be seen. Results are reported
as per-milestone values and ranges, not significance tests.

## 8. Method

### Phase 0: census and instrumentation (one agent run in step 4; about 2 hours)

0. **Overhead census, before anything else.** Compute M6 from the saved transcripts and the
   `graphify update` output already in them. Report it as a share of total session tokens and
   as tokens per session. **Decision point:** if M6 is under T6 (section 7), the human may
   decide that A versus B is immaterial, skip Phase 2, and choose
   between B and C on the accuracy evidence in 3.1 plus the Phase 1 description. That decision
   is recorded here and the plan ends.
1. **Freeze the corpus.** Write `local/graphify-eval/sessions.json`: every transcript file in
   scope, its session id, model, start and end times, parent session for subagents, and the
   cutoff rule. State the reminder dedup key (tool-use id). Re-issue section 3.2 from it.
2. Add M1, M2, M5 and M7 to `usage_report.py`: token sums from transcript usage fields, the
   orientation window, and plan parsing. Validate the sums against the known M17a session by
   hand-checking several turns. Look up the chosen model's prices and write the M1 weights
   into section 6.
3. Compute M1 and M2 for the orientation phase of the real M15 and M16 sessions, which ran on
   the Phase 2 model (Fable 5.1). This is the historical baseline and the source of T1. Report
   M17a's figure separately, because it ran on Opus 5.5 and in a restarted session, and do not
   use it for T1 or the budget. Write the resulting T1 into section 7.
4. **Re-run the planted-defect check and keep the artifact.** Add the planting code to
   `eval.py` behind a flag, run it, and save the result under `results/`. If any planted defect
   is not flagged, fix the scorer before Phase 2. (This is the one step in Phase 0 that may
   call an agent, if the planting code is written by one; it is budgeted below.)
5. Check three things in a scratch clone (see Phase 2 for how the clone is made):
   - That `graphify update app` builds a full graph from scratch at an old commit without
     calling a model, and record its wall time and output tokens for M6.
   - That a clone with the hook, the graphify section and `.claude/CLAUDE.md` removed shows no
     graph reminder and no `/graphify` skill.
   - That the clone contains no ref or object newer than the base commit (`git log --all`
     shows nothing past it, `git remote` is empty).

#### Phase 0 results (2026-10-10)

Scripts: `corpus.py` (step 1), `overhead_census.py` (step 0), `orientation.py` (steps 2 and 3),
`plan_score.py` (M3, M4, M7 for a `PLAN.md`), `eval.py --plant` (step 4), `make_clone.sh` and
`check_clone.sh` (step 5). Detail files are under `results/`. No agent tokens were spent.

- **Step 0, overhead census.** Over the 25 sessions: 1,065 reminders (about 50 tokens each, 52.8K
  tokens in all), 22 graph outputs (5.2K characters each, 28.4K tokens), 44 refresh outputs
  (4.2K tokens), and the CLAUDE.md graphify section (1,743 characters, about 440 tokens per
  transcript file that loads it). Tokens are estimated at 4 characters each.
  - M6 as section 6 defines it (each token counted once): 102K tokens in all, **4,096 per
    session**; median share of a session's own price-weighted tokens **0.22%**; per-session mean
    against the median session (1.10M weighted) **0.37%**. Under T6 = 2%.
  - M6 as the tokens are actually paid (written to cache once at ×1.25, then read back at ×0.1
    on every later request of the same transcript): 727K weighted in all, **29,088 per session**;
    median share **1.1%**; per-session mean against the median session **2.65%**. At T6.
  - Sensitivity: the transcripts imply the context grows by about one token per 2 characters
    that enter (attachments and tool inputs included), so 4 characters per token may understate;
    at 2.5 every share above is ×1.6 (once: 0.35% median; carried: 1.8% median).
  - **Decision point (step 0):** under the plan's own definition the overhead is far below T6;
    under the carried definition it sits at the threshold. If the human stops here, the fallback
    in section 7 step 5 points to **B**. Not yet decided.
- **Step 1, corpus.** `sessions.json`: 29 transcripts, 25 included, 23 subagent files, 2,351 tool
  calls. The cutoff and both dedup keys are recorded in the file and in section 3.2.
- **Step 2, instrumentation.** Token sums are one record per `requestId` (the harness stores one
  row per content block, each repeating the request's usage). Validation against the harness's
  own `cost-state` totals for each session's main model: median ratio 0.99 (cache writes), 0.94
  (cache reads), 0.995 (output); 13 of 25 sessions within 6% on all three. The shortfalls are
  usage the harness bills but the transcript does not store (background requests, retries,
  compaction summaries), so a transcript sum is a lower bound. The same method is applied to
  every arm. The orientation window of a historical session closes at the first tool call that
  writes under `app/`, relative paths included because sessions `cd app`; a Phase 2 run closes
  at the Write of `PLAN.md`.
- **Step 3, historical baseline** (price-weighted M1 / raw / requests / tool calls / minutes):
  M15 (`e7c59fde`, Fable 5.1) **479,614** / 1,710,653 / 15 / 27 / 6.6;
  M16 (same session after a compaction, Fable 5.1) **323,662** / 1,212,331 / 9 / 27 / 4.5;
  M17a (`a902b56d`, Opus 5.5, reported apart) 459,076 / 2,107,065 / 25 / 24 / 4.1.
  Median of the two Fable figures: **401,638**, the per-run budget base. Historical M5 (files
  opened outside the reference diff, with no plan to credit): 0.60, 0.70, 0.74. T1: section 7.
- **Step 4, planted defects:** pass (section 3.1).
- **Step 5, clone checks** at `40b2d84` for arms N, G and D: every check passes. HEAD is the
  base, no remote, `git log --all` shows nothing past it, no stash. N has no hook, no graphify
  text in CLAUDE.md, no `.claude/CLAUDE.md`, no project skill, no graph. D has no hook, the
  one-line note, and keeps `.claude/CLAUDE.md`. The graph builds from scratch in 2 s with every
  model key unset (1,152 nodes, 3,210 edges, 58 placeholder communities; the only backend
  mention in the log is graphify's tip that no key is set). The clone's per-project memory folder
  is empty; it is named from the clone path, so every Phase 2 clone needs a fresh path.
- **Reference sizes checked:** existing `app/` files changed, M15 27 (not 31 as section 7 says:
  that count included new files), M16 21 (not 20), M17a 10. T3 and T4 are stated in files as
  well as shares, so the rules are unaffected; section 7's sentence is corrected below.
- **M4 note:** the reuse set is wide (55 modules for M16, CSS modules included) because it holds
  every module the changed files import. A plan that lists only files to change scores low on M4
  by design; the prompt asks for modules to reuse explicitly.

#### Phase 2 pilot: one G/N pair on M17a (2026-10-10, "for science")

Run with `run_pair.sh` (headless `claude -p`, Fable 5.1, `--max-budget-usd 8`, subagents
disallowed, no permission prompts inside the isolated clone). Order by coin flip: N then G. Both
wrote `PLAN.md`; neither hit the cap; the leakage scan found only the base commit's own build plan
naming M17b as the next milestone. Artefacts: `results/runs-m17a/` (both plans, both transcripts'
scores, run log, clone checks). Unadjusted scores; no blind grader has run.

| Measure | N (no graph) | G (graph as configured) |
| --- | --- | --- |
| M1 price-weighted / raw | **201,077** / 658,549 | **239,673** / 899,797 (+19% / +37%) |
| Requests / tool calls (M2) / minutes / $ | 12 / 12 / 2.2 / 2.29 | 16 / 16 / 4.0 / 2.58 |
| Graph calls / hook reminders | 0 / 0 | 2 / 6 |
| M3 file recall (10 reference files) | **0.80** (missed `JobDetailPage.module.css`, `JobListPane.tsx`) | **0.60** (also missed `JobDetailPage.tsx`, `changes.ts`) |
| M4 reuse recall (57 modules) | **0.39** | **0.12** |
| M7 precision (paths named) | 0.77 (43 named) | 0.70 (23 named) |
| New files named exactly as built (of 24) | 10 | 9 |
| M5 exploratory reads | 0.30 of 64 opened | 0.74 of 39 opened |

Reading: on this one pair the graph arm cost more and found less. That is one run per arm with
no repetition, so it is a data point, not a result; section 7's rules need two repetitions per
arm and three milestones. Both runs cost under half the historical M17a orientation (459K),
because a headless run has no human turns. Scorer changes made while scoring: a plan written by
`cat > PLAN.md` now closes the window, and M7 counts files the milestone created as valid.

#### Phase 2 results and the section 7 verdict (2026-10-10, Opus 5.5, G and N, 3 × 3)

Batch: `run_batch.sh`, Claude Code 2.1.296, graphify 0.9.74, `claude-opus-5-5`, $4 cap per run,
fresh clone per run, order coin-flipped per pair. All 18 runs valid: every one wrote `PLAN.md`,
none capped, no leakage hit, all clone checks passed. Total $25.72 (average $1.43 per run, above
the $1 guess). Every G run queried the graph, 1 to 2 times, and received 3 to 13 hook reminders.
Scoring: `score_batch.py`; artefacts in `results/runs-opus/` (every plan, run log, scores).
Unadjusted scores; the blind grader (Phase 3 step 2) has not run.

Per-milestone medians [min–max] over 3 runs per arm:

| Milestone | Arm | M1 price-weighted | M3 file recall | M4 reuse recall | M7 precision | M2 calls |
| --- | --- | --- | --- | --- | --- | --- |
| M15 | N | 408,149 [404,600–449,319] | 0.96 [0.96–1.0] | 0.67 [0.61–0.67] | 0.71 [0.67–0.81] | 28 |
| M15 | G | 391,968 [328,270–394,408] | 0.93 [0.85–1.0] | 0.63 [0.56–0.67] | 0.77 [0.69–0.82] | 25 |
| M16 | N | 283,843 [252,940–341,340] | 0.62 [0.52–0.67] | 0.26 [0.24–0.27] | 0.57 [0.55–0.75] | 20 |
| M16 | G | 331,632 [296,885–348,187] | 0.62 [0.48–0.71] | 0.22 [0.15–0.31] | 0.74 [0.34–0.78] | 19 |
| M17a | N | 241,250 [233,482–247,364] | 0.50 [0.40–0.60] | 0.11 [0.11–0.14] | 0.70 [0.69–0.74] | 18 |
| M17a | G | 267,263 [251,480–291,749] | 0.50 [0.50–0.50] | 0.18 [0.11–0.21] | 0.76 [0.71–0.79] | 18 |

Against the thresholds (G relative to N): M1 saving +4% / −17% / −11% (T1 is 20%); ΔM3 −0.04 /
0 / 0; ΔM4 −0.05 / −0.04 / +0.07 (T4 is 0.10); ΔM7 +0.06 / +0.18 / +0.07 (never below −T3).

**Verdict by the rules in order.** Rule 1 fires: on all three milestones the within-arm range of
G's M1 (16 to 18% of N's median) is wider than the G–N gap (4 to 17%), so the cost comparison is
**inconclusive**: the graph arm is neither reliably cheaper nor reliably dearer. Had rule 1 not
fired, rule 4 would apply: G reaches T1 on no milestone and T4 on none, so **no benefit was shown
on cost or on recall**. The one consistent signal is M7: G's plans were more precise on every
milestone (+0.06 to +0.18), below any rule's threshold but the same sign nine times out of nine
pairs is not nothing. From rule 1 the plan sends the human to the M6 fallback (step 5): M6 is
under T6 under the plan's definition (0.22% median), so the fallback outcome is **B: keep the
graph on demand, drop the mandate and the hook.**

Cross-check: the Fable 5.1 pilot pair on M17a pointed the same way on cost (G +19%) and did not
show a recall gain either. Nothing in either model's data supports A.

Limits that stand: three milestones of one feature family; unadjusted recall (a different but
valid plan is under-scored; the blind grader would raise both arms, and there is no reason to
expect it to raise one more than the other); orientation only, so editing-time misses are not
measured; the finding is about Opus 5.5 with a Fable cross-check.

### Phase 1: retrospective misses (one agent classifier; about 1 hour)

1. Classify every finding in the 20 saved reviews (`local/M*/review.md`) into one of:
   - duplicate of existing code
   - missed dependent or caller
   - other

   Two classifiers, one a script on keywords and one an agent working blind to the milestone
   name and date, with disagreements listed.
2. Report counts per milestone. Graphify was adopted during M2, so only M0 and M1 (2 reviews)
   predate it. The milestones also differ in kind. This phase is descriptive only and does not
   decide anything.

### Phase 2: paired orientation runs (agent runs)

Tasks: the start of M15, M16 and M17a.
- The M16 base is `c5178f0` (the M15 tick) and the M17a base is `9738747` (the M16 tick).
- The M15 base is the commit before M15's first commit, found in Phase 0.

**Isolation.** Each run gets a fresh clone that holds only the base commit's history, and a
fresh session. The clone is made with `git init`, then `git fetch <path to main checkout>
<base sha>`, then `git checkout --detach FETCH_HEAD`. No remote is configured. This keeps the
future milestone commits out of reach; a worktree would share refs with the main repo and
expose them through `git log --all`, `git branch` or `git reflog`. Nothing is added to the main
repo, so the one-remote rule holds. Per-project memory is empty because the clone path has its
own memory folder; step 5 of Phase 0 verifies this by listing that folder before the first run.

Arms. All three are run.

| Arm | Setup at the base commit |
| --- | --- |
| G (graph, as configured) | Graph built at that commit with `graphify update app`, root link created, hook, CLAUDE.md section and `.claude/CLAUDE.md` as they were at that commit |
| N (no graph) | No graph output, hook removed from the clone's `.claude/settings.json`, graphify section removed from CLAUDE.md, `.claude/CLAUDE.md` removed (it names the `/graphify` skill), project graphify skill removed. These edits stay uncommitted. |
| D (on demand) | As G, but the mandate in CLAUDE.md and the hook are removed. One line in CLAUDE.md says the graph exists and how to query it. |

Controls:
- **One model for every run: `claude-fable-5-1`.** It ran two of the three baseline sessions
  and is the model building milestones now, and the decision is about the future workflow, so
  it is the model whose behaviour matters. The historical baseline is mixed and is not compared
  arm-to-arm. Opus 5.5 and Sonnet 5.5 were considered: Opus matches only M17a; Sonnet would buy
  more repetitions but its reliance on the graph may not transfer to the model doing the work.
- Same effort setting (default, recorded with the CLI version in `sessions.json` before the
  first run), same prompt, same user-level settings, same subagent policy (the prompt forbids
  spawning subagents, so the window is one transcript).
- Arm order is randomised per milestone and the order is recorded.
- The graph in G and D is built from the base commit only. Using today's graph would leak the
  answer.
- **Leakage scan.** After each run, the transcript is scanned for `--all`, `reflog`, `fetch`,
  the names of later milestones, and any path under `local/graphify-eval/`. A hit excludes the
  run under rule 0 and is listed.
- The CLAUDE.md at each base commit is the one that applies. The M15 and M16 bases predate the
  2026-10-10 reading rules, so their orientation is heavier in every arm. Each pair shares a
  base, so this does not bias the arm comparison; it does limit comparing milestones with each
  other.

Prompt, identical in every arm:

> "go mX. Do the session-start reading, then stop before your first edit and write
> `PLAN.md` in the repository root listing: files to create, existing files to change,
> existing modules to reuse, and callers that the change affects. Do not spawn subagents."

The end of orientation is the moment `PLAN.md` is written. A run that stops without writing it
is excluded under rule 0. The real workflow continues to test-first edits. Stopping at the plan
keeps cost down, and it measures orientation, which is the phase the graph is meant to help.

Repetitions: 2 per arm per milestone. That is 18 runs.

### Phase 3: scoring and blind review (one agent grader)

1. A script computes M1 to M5 and M7 for every run.
2. For plan items that disagree with the reference, a blind grader judges each one valid or
   invalid against a fixed rubric: valid means the file or module would need to change, or
   would be imported, in some correct implementation of the milestone spec. The grader gets
   the base commit, the milestone spec section and the item. Before grading, the plan is
   stripped of any mention of graphify, any `graphify-out` path, and graph vocabulary ("node",
   "edge", "community", "god node"). The grader is asked to guess the arm, and the guess is
   recorded beside the score. Valid items raise the adjusted M3, M4 and M7; both scores are
   reported.
3. Apply section 7 in order and write the decision with its numbers, the excluded runs and
   their reasons, and the per-arm ranges.

## 9. Threats to validity

- **Small samples.** There are 3 milestones and 2 repetitions, so model variance can exceed the
  effect. Mitigation: the within-arm spread is reported, and rule 1 makes the result
  inconclusive when it dominates.
- **Task representativeness.** M15, M16 and M17a are one related feature sequence (people and
  companies), chosen because they are the most recent milestones with clean bases and known
  outcomes. A result on them says less about milestones of a different kind, such as the data
  layer or server work. The Phase 1 counts per milestone show how different the kinds are.
- **Competing guides.** The README code map, the build plan's file hints and the session summary
  also point to files. They are present in every arm, so the comparison measures the graph's
  *additional* value, which is the decision being made.
- **The reference is one solution.** Mitigation: the blind adjusted score, with M7 to stop
  padding.
- **Stopping at the plan** does not measure misses that only show up while editing. Phase 1
  describes them historically but does not compare arms. See section 2 and section 11.
- **Instructions changed during the project.** The reading rules were added on 2026-10-10 in
  `a682078`, between M16 and M17a. Each pair shares a base, so it does not bias the comparison,
  but it limits comparing different milestones with each other.
- **Mixed baseline model.** The historical sessions ran on two models. Phase 2 uses one, so the
  historical M1 figures are a budget guide, not a comparison point.
- **Measurement scripts.** Paths are matched as text, and commit attribution in 3.2 uses time
  windows. The paired runs avoid the second problem, because each run's clone has no commits.
- **Author bias.** This plan, the scripts and the question set were all written by the agent
  that uses the graph day to day. Two independent audits reviewed the first draft; their
  refuted items are the source of this revision.

## 10. Constraints

- No run touches `~/.job-tracker/`, `capture/` or the live original app.
- Clones live under a temporary directory, have no remote, make no commits, and are removed
  after scoring. `origin` on the main checkout is untouched.
- Graph builds use `graphify update app` from the clone root only. Never `update .`, never
  `extract --force`.
- Agent tokens are spent only after the human approves the budget in section 12, and every
  run stops at its per-run cap.

## 11. Out of scope

- Comparing graphify with other graph tools.
- Rebuilding with the new node-ID scheme.
- Tuning the query budget or the reminder before the decision. Changing either first would alter
  the arms being measured.
- Editing-time misses. A bounded full-milestone pair (one milestone, arms G and N, through
  `npm run check` and the review) would measure them. It is a separate proposal with its own
  budget, to be written only if the orientation result is borderline or the human asks.

## 12. Budget and decisions needed from the human

Every phase that spends agent tokens is listed. Phase 0 step 3 fills in the per-run figure;
the human approves the total **and the caps** before any agent run in any phase.

| Spend | Runs | Estimate | Cap |
| --- | --- | --- | --- |
| Phase 0 step 4, planting code | 0 | written in the main session on 2026-10-10; no agent spend | none |
| Phase 1 agent classifier | 1 pass over 20 reviews (47.6K characters, about 12K input tokens) | about 40K tokens on Sonnet 5.5, under $1 | 60K tokens |
| Phase 2 paired runs | 18 | 18 × 401,638 = 7.2M price-weighted tokens, about $72 at Fable 5.1's $10 per M input-equivalent | per run 803K weighted (about $8); total 10.8M weighted (about $108), retries included |
| Phase 2 retries of excluded runs | up to 3 | same per-run figure | counted inside the Phase 2 total cap |
| Phase 3 blind grader | 1 pass over disagreeing items (count known after Phase 2) | about 10K tokens per item on Sonnet 5.5; at 100 items 1M tokens, about $3 | 1.5M tokens |
| Graph refreshes | 12 (G and D runs) | 2 s each from scratch at the M15 base, no model key needed (verified in Phase 0 step 5) | none needed |

Decided on 2026-10-10: the thresholds T2 to T6 and the G1 gate values in section 7, and
`claude-fable-5-1` as the Phase 2 model.

**Changed on 2026-10-10, after the pilot pair and before the first scored run** (section 7 allows
this with date and reason): the scored Phase 2 set is **arms G and N only, 3 milestones,
3 repetitions, on `claude-opus-5-5`** (18 runs). Reasons: the human wants to conserve Fable
usage; Opus 5.5 shares Fable 5.1's tokenizer and built M17a historically; arm D is dropped
because the pilot showed the mandated arm itself used the graph only twice, so an unmandated arm
would be indistinguishable from N, and option B is reachable from G-versus-N plus the overhead
census; a third repetition costs about $1 per run on Opus and turns the per-milestone median into a
real median. The Fable pilot pair is excluded from the rules and kept as a cross-check. Section 7's
rules apply with the "arm D" clauses void; "2 of 3 milestones" and the T values are unchanged. The
finding is about Opus 5.5. T1 is fixed by formula and its number is filled in
from Phase 0 step 3.

Still needed from the human (Phase 0 is complete; nothing below has been decided):

1. Whether to stop after the Phase 0 overhead census (step 0) and decide B versus C without
   Phase 2. The census says: 0.22% median share under the plan's definition of M6, 1.1% median
   (2.65% mean against the median session) under the as-paid definition, against T6 = 2%.
2. Which M6 definition rules the step 5 fallback: once (the plan's text) or as paid. The plan's
   text stands until changed; under either the fallback currently points to B.
3. The budget table above, now that Phase 0 gives the per-run cost: about $72 estimated and
   $108 capped for Phase 2, under $5 for Phases 1 and 3 together.
4. T1 fixed at 20% (section 7), since no within-arm range exists before Phase 2.
5. ~~After the M17a pilot pair: fund the remaining runs or stop.~~ Done: 18 Opus runs on
   2026-10-10, $25.72. Verdict: inconclusive on cost under rule 1, no benefit shown under rule 4,
   fallback **B**. Remaining decision: accept B and apply it (remove the hook and the mandate,
   keep the graph and the CLI, log the change), or run the blind grader (Phase 3 step 2, about
   $3) first for the adjusted scores.
