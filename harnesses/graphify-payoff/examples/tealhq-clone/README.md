# Is graphify paying off? (tealhq-clone instance, 2026-10-10)

Two measurements, following the validation guide at `~/dev/research/graphify/validation-guide.md`.
Both run from the repo root, read only, and never rebuild the graph or touch `capture/` or
`~/.job-tracker/`. This folder is untracked (`local/` is in the global git ignore).

| Script | Guide claim | What it answers |
| --- | --- | --- |
| `eval.py` | 1, the graph is correct | Are the graph's edges right and fresh, and does a query find the answer? `--plant` damages a copy three ways and checks the scorer flags each |
| `usage_report.py` | 2, the integration works | Did sessions query the graph, and did the graph lead them to the files they opened? Reads only the sessions `sessions.json` includes |
| `corpus.py` | 3, setup | Freezes the transcript corpus into `sessions.json`: cutoff, dedup keys, per-session facts |
| `overhead_census.py` | 3, cost | M6: reminders, graph output, CLAUDE.md section and refresh output per session, once and as paid |
| `orientation.py` | 3, cost | M1, M2 and M5 for one session's orientation window (historical or a Phase 2 run) |
| `plan_score.py` | 3, outcome | M3, M4 and M7 for a run's `PLAN.md` against the reference milestone |
| `make_clone.sh`, `check_clone.sh` | 3, isolation | Build and verify an arm clone (G, N or D) of one base commit for Phase 2 |

`transcripts.py` holds the shared readers (session files, per-request usage dedup, hook reminders).
Run every Python script with `python3 -I` from the repo root; the shell scripts take
`<base-sha> <G|N|D> <dir>`.

Claim 3 (the workflow improves) needs a paired run with and without the graph. Neither script
answers it. `plan.md` covers it: the decision, the acceptance criteria, and the paired-run method.
It was revised after the two audits in `audits/`. `plan-audit-prompt.md` is the reviewer prompt
the audits were run from. Where `plan.md` corrects this README (for example, graphify was adopted
after M1, not after M2), `plan.md` is right.

## When to run

- `eval.py`: after each `graphify update app`, so at least twice per milestone. Each run appends one
  line to `results.jsonl` (the trend) and writes full detail to `results/<date>-<commit>.json`.
- `usage_report.py --since <date>`: at each milestone boundary. Its output is printed, not stored.

```sh
python3 -I local/graphify-eval/eval.py
python3 -I local/graphify-eval/usage_report.py --since 2026-10-10
```

## eval.py

The expected answers are never taken from the graph:

| Section | Ground truth | Scored |
| --- | --- | --- |
| Imports | `source_imports.py`: every relative import in `src/`, `server/` and `e2e/`, resolved from source | Recall and precision for TS-to-TS imports. An edge resolved through a re-export is counted as correct. CSS-module imports are reported separately because the graph does not model CSS. |
| Calls (`questions.json` `calls`) | Written by hand from grep on 2026-10-10, before any graph run | Same-name functions in different files point to the right one. Calls inside callbacks and through `store.method()` are found. |
| Retrieval (`retrieval`) | Same | `graphify query` at the default budget returns every expected file. Records the rank, size and truncation. Two questions about things that don't exist expect no matches. |
| Affected (`affected`) | Files that import the symbol itself, from source (type-only importers excluded) | `graphify affected` names every one of them. |
| Freshness | git | Whether app changes are newer than `built_at_commit`. Deleted and renamed files must have no nodes, and every source file must have one. |

Each question carries an `evidence` regex. When the code no longer matches it, the question is
reported `stale` rather than counted as a graph failure. Update the question, don't delete it.

To check that the scorer can still fail, point it at a damaged copy:
`GRAPH_EVAL_GRAPH=<copy.json> python3 -I local/graphify-eval/eval.py`. On 2026-10-10 a copy
with a missing import, a call to the wrong `notFound` and a ghost `JobRow.tsx` was caught on all
three checks.

## usage_report.py

One row per session, with subagents folded into their parent, read from
`$CLAUDE_CONFIG_DIR/projects/-Users-tonyrosario-dev-tealhq-clone/`. Only counts and `app/`
paths are printed.

- `graph`, `hedged`, `truncated`: graph calls, the ones that also ran grep, cat or ls in the
  same command, and the ones whose output was cut.
- `reminders`: the hook's "MANDATORY: graphify query" reminder. Each one is stored in the
  transcript several times, so the script counts only `hook_additional_context` entries.
- `lead:*`: for each `app/` file a session opened for the first time, which earlier tool result
  first named it: graph, search, other output, or none (known from the prompt or the summary).
- `committed`, `cmt∩graph`: app files committed while the session ran, and how many of them a
  graph query in that session had named. Commits are matched by time window, because sessions
  commit with `git commit -q`. Two sessions that overlap and both commit are each credited with the
  window's commits.

Limits: paths are matched by text, and a file named only by its basename is missed. "Led by the
graph" means the graph named the file first, not that the agent would have missed it otherwise.
Only a paired run can show that.

## Phase 0 results, 2026-10-10

See `plan.md`, section 8, "Phase 0 results". Headline: the graph's overhead is 4,096 tokens per
session counted once (0.22% median share), 29,088 price-weighted as paid (1.1% median share);
historical orientation cost 480K and 324K price-weighted tokens for M15 and M16 on Fable 5.1;
planted defects all flagged; arm clones verified. The human decision point in the plan is open.

## Phase 2 results, 2026-10-10

18 orientation runs on Opus 5.5 (G and N, M15/M16/M17a, 3 reps), $25.72, scored by
`score_batch.py` into `results/runs-opus/score_batch.json`. Verdict under plan section 7:
inconclusive on cost (rule 1), no benefit shown on cost or recall (rule 4 would have given C),
fallback to **B**. G's plans were slightly more precise on every milestone. `run_pair.sh` runs one
pair; `run_batch.sh` runs the grid. Details in `plan.md`, section 8, "Phase 2 results".

## Baseline, 2026-10-10 (54d9806, graph built at de9d2cf)

`eval.py`:

| Check | Result |
| --- | --- |
| TS-to-TS import recall | 766/766 |
| Import precision | 1.0 (59 edges resolved through re-exports) |
| CSS-module imports in the graph | 0/103 |
| Calls to a same-name function resolved to the right file (C1 to C5) | 4/5, none to a wrong file. C5, a call from a test body, is missing. |
| Calls through `store.updateContact` in component handlers (C6, C7) | 0/2, missing |
| Retrieval questions passed | 13/18 |
| Retrieval outputs cut at the default budget | 14/18 |
| `affected` importers found | 10/10 |
| Ghost files in the graph | 0 |
| Source files with no node | 0 |

Retrieval misses:
- R2 is missing `ProblemBanner.tsx`.
- R4 finds `JobListPane.tsx` only at rank 51 and misses `ListPane.tsx`.
- R9 misses `httpJobStore.ts`.
- R16 misses `peopleHandlers.ts`.
- R17, the made-up "stripe webhook" question, returned seven files, `httpJobStore.ts` and `peopleHandlers.ts` among them.

`usage_report.py` (the 25 sessions in `sessions.json`, Oct 3 to 10; reminders keyed by `toolUseID`):

| Measure | Result |
| --- | --- |
| Graph calls | 22, about 0.9 per 100 tool calls |
| Graph calls that also ran grep, cat or ls | 17 |
| Reminders | 1,065, about 48 per graph call |
| First file opens led by | graph 13%, search 20%, other output 18%, none 49% |
| Committed app files named by a graph query in the same session | 74/670 |
