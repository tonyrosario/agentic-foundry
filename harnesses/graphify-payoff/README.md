# graphify payoff harness

Does a graphify code graph earn its place in a repository worked on by Claude Code? This harness
answers that with criteria fixed before measuring, a paired experiment (graph mandated versus
absent, same task, same model, fresh isolated clone per run), and scripts that score every run
from the saved transcripts and git. It is repo-agnostic: everything specific to a repository
lives in one `harness.json`.

First used on `tealhq-clone` (2026-10-10, a ~260-file TypeScript app). Result there: no cost or
recall benefit from mandating the graph, overhead about 0.2% of a session, decision "keep the
graph on demand, drop the hook and the mandate". The worked example is under `examples/`.
A larger codebase may show a different answer; that is the point of keeping the harness.

## What it measures

Each run is one Claude Code session that reads the repository's own instructions, orients on a
task, and stops after writing `PLAN.md` (files to create, files to change, modules to reuse,
callers affected). Orientation is where a code graph is supposed to help, and stopping there
keeps a run at $1 to $3.

| Measure | Role | Definition |
| --- | --- | --- |
| M1 | rule | Orientation tokens, price-weighted (input ×1, cache write ×1.25, cache read ×0.1, output × the model's output/input price ratio), summed per API request from the transcript |
| M2 | diagnostic | Tool calls in the window |
| M3 | rule | File recall: of the existing source files the reference build changed, the share the plan names |
| M4 | rule | Reuse recall: of the modules the reference build's changed files import, the share the plan names |
| M5 | diagnostic | Exploratory reads: files opened that are in neither the plan nor the reference |
| M6 | fallback | The graph's overhead per session from historical transcripts: hook reminders, query output, instructions section, refresh output |
| M7 | rule | Plan precision: of the paths the plan names, the share in the reference or its reuse set |

The reference is what the task's real build touched (`git diff base..tick`). It is one valid
answer, not the only one, so recall is a lower bound; `PLAN-TEMPLATE.md` describes the optional
blind-grader adjustment.

Arms: **G** (graph, hook and instructions as the repo has them), **N** (no graph: hook removed,
instructions section removed, skill removed, no graph files), **D** (graph available, mandate and
hook removed). D turned out to be indistinguishable from N on tealhq because even G queried the
graph only once or twice per run; drop it unless the repo's agents actually use the graph.

## Applying it to a repository

1. **Prerequisites.** Each task's base commit either carries graphify as you intend to test it
   (hook and instructions in place) or `arm_G_restore` names a commit to take them from: arm G
   installs that commit's hook files and instructions section into any clone whose base lacks
   the hook, so a repo that has gone on demand, or never mandated the graph, can still be
   measured. If the graph is mentioned outside that section (an on-demand repo usually says
   "or `graphify query`" in its reading rules), list the literal `[old, new]` substitutions
   arm N must make in `arm_N_edits`; `check_clone.sh` fails N on any remaining mention.
   You have a few finished tasks with a clean
   `base` commit (the commit before the task's first change) and a `tick` commit (the task done).
   Three tasks is the minimum the rules need. Claude Code sessions for the repo exist under
   `~/.claude/projects/<slug>/` if you want the historical census (optional).
2. **Copy the scripts** into the repo at an ignored path (for example `local/graphify-eval/`) or
   point `HARNESS_CONFIG` at a config anywhere. Copy `scripts/harness.example.json` to
   `harness.json` beside them and fill it in: `repo`, `code_root` (the folder graphify indexes,
   `""` if the repo root), `source_dirs` and `source_exts` (what counts as source), the graph
   section heading in the instructions file, what arm N removes, the tasks, the model and cap.
   Write `questions.json` (schema in `scripts/questions.example.json`) if you want the accuracy
   gate `eval.py`; its expected answers must come from grep and git, never from the graph.
3. **Phase 0, free.** `corpus.py` freezes the historical transcripts; `overhead_census.py` gives
   M6; `orientation.py` on a historical session gives the per-run budget; `eval.py --plant`
   proves the accuracy scorer can fail; `make_clone.sh` + `check_clone.sh` prove the arm clones
   are isolated (no remote, no refs past the base, empty per-project memory, graph built with no
   model key). If M6 is already far below your threshold, you may stop here: the graph costs
   nothing to keep idle, and only the mandate is in question.
4. **Phase 2, paid.** `run_batch.sh <runs-dir> <reps>` builds fresh clones per run and runs G and
   N in a coin-flipped order with `claude -p`, a dollar cap, subagents disallowed and no
   permission prompts (the clone is isolated). Expect $1 to $3 per run; 3 tasks × 2 arms × 3 reps
   is 18 runs. Run a single pair first with `run_pair.sh` to see the pipeline work.
5. **Phase 3.** `score_batch.py <runs-dir> --out <file>` scores every run, excludes invalid ones
   (no plan, capped, leakage of later history), and applies the rules in order. Read the
   per-milestone ranges before the verdict: with 3 reps, only large effects are visible.

Write your criteria (the T values) into your copy of `PLAN-TEMPLATE.md` before Phase 2 starts.

## Decision rules (from the template)

Evaluated in order, first that applies wins, on per-task medians against N:
1. Inconclusive if G's within-arm M1 range exceeds the G–N gap on most tasks → M6 fallback.
2. **A (keep as configured)** if G saves ≥ T1 (20%) on M1 on 2 of 3 tasks and loses no more than
   T3 (0.05) on M3, M4, M7 anywhere.
3. **B (keep on demand)** if G beats N on M3 or M4 by ≥ T4 (0.10) with M7 intact, whatever the cost.
4. **C (remove)** if G beats N on neither cost nor recall on 2 of 3 tasks.
5. Fallback from 1: B if M6 < T6 (2% of a session), else C.

## What the scripts need

Python 3.11+ (standard library only), `git`, `graphify`, `claude` (Claude Code CLI with `-p`),
`jq` only for the ad-hoc checks in this README. Transcript facts the readers depend on (Claude
Code 2.1.x): one API request is stored as several `assistant` rows sharing a `requestId`, so usage
is summed once per request; hook reminders are the `hook_success` attachments keyed by
`toolUseID`; subagent transcripts live under `<session>/subagents/`.

## Caveats learned on the first run

- Transcript token sums are a lower bound of what the harness bills (median 94 to 99% of the
  harness's own cost-state on the large fields); the same method applies to every arm.
- Agents `cd` into the code root and write relative paths; the path regexes accept both forms.
  `cat > PLAN.md` closes the window as well as a `Write`.
- Run-to-run spread within one arm was 16 to 18% of the median on tealhq. Two repetitions give a
  range; three give a median that one odd run does not move.
- A headless run costs about half of a human-driven one; budget from a pilot pair, not from
  history.
- `claude -p` needs `--dangerously-skip-permissions` to run tools unattended; that is acceptable
  only because the clone has no remote and no history past the base. Never point it at a live
  checkout.

## Layout

```
README.md             this file
PLAN-TEMPLATE.md      the evaluation plan with blanks and default thresholds
scripts/              the harness (config.py reads harness.json; see each file's docstring)
examples/tealhq-clone the first application: config, the plan as executed, results, verdict
```
