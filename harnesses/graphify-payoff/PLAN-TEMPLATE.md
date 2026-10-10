# Plan: does the code graph earn its place in {{repo}}?

Prepared {{date}} at commit `{{head}}`. Fill every `{{blank}}` and fix section 7 before the first
scored run. The method follows the graphify validation guide (claims: the graph is correct, the
integration is used, the workflow improves); this plan measures the third.

## 1. Decision this plan informs

The repo runs graphify over `{{code_root}}`. With it come: an instruction to orient with
`graphify query` ({{instructions_file}}, section `{{section_heading}}`), a `PreToolUse` hook
that reminds the agent on every tool call, and a refresh step per task. The plan ends in one of:

| Option | What changes |
| --- | --- |
| A. Keep as configured | Nothing |
| B. Keep on demand | Graph and CLI stay; the mandate and the hook go |
| C. Remove | Graph, hook, skill, instructions section and refresh steps all go |

## 2. Goal

Determine, with criteria fixed before measuring, whether graph-first navigation makes the task
workflow cheaper (fewer tokens and tool calls before the first edit) or safer (fewer missed
dependents, less duplicate code), net of its overhead (reminders, query output, refreshes,
instructions loaded every session). Graph accuracy is a precondition, not the goal.

Scope: Phase 2 measures orientation (the prompt to `PLAN.md`). Misses that appear only while
editing are not measured; a full-task pair is a separate proposal.

## 3. What is known today

Fill from Phase 0. Keep each figure with its method and limits.

- Graph accuracy (`eval.py`): import recall/precision {{..}}, call questions {{..}}, retrieval
  {{..}}, `affected` {{..}}, stale or ghost files {{..}}.
- Graph use (`usage_report.py` over `sessions.json`): sessions {{n}}, tool calls {{n}}, graph
  calls {{n}} ({{x}} per 100), hedged with grep/cat {{n}}, hook reminders {{n}}, first opens led
  by graph / search / other / none {{..}}.
- Overhead (`overhead_census.py`): M6 once {{tokens}} per session ({{share}} median share),
  as paid {{tokens}} ({{share}}).
- Historical orientation cost (`orientation.py` on real sessions): {{task}}: {{M1}} …

## 4. Hypotheses

- H1 (cost): with the graph as configured, orientation costs less than without it.
- H2 (outcome): with the graph, a plan names more of the code the task needed, without padding.
- H0: no difference larger than run-to-run noise.

## 5. Measures

| ID | Role | Measure |
| --- | --- | --- |
| M1 | rule | Orientation tokens, raw and price-weighted (input ×1, cache write ×1.25, cache read ×0.1, output × {{output/input price ratio}}); rules test the weighted figure |
| M2 | diagnostic | Tool calls in the window |
| M3 | rule | File recall against the reference build's changed existing files |
| M4 | rule | Reuse recall against the modules the reference build's changed files import |
| M5 | diagnostic | Exploratory reads |
| M6 | fallback | Overhead per session from historical transcripts |
| M7 | rule | Plan precision |
| G1 | gate | `eval.py` at the base commit: import recall and precision ≥ 0.99, every `affected` probe found, 0 stale files, 0 missing nodes |

Unadjusted scores use the reference only; adjusted scores add items a blind grader accepts
(Phase 3). Report both; the rules test the adjusted score when the grader has run.

## 6. Acceptance criteria (fix before Phase 2; record any change with date and reason)

| Symbol | Default | Meaning |
| --- | --- | --- |
| T1 | 20% | M1 saving G must show for A |
| T2 | ±10% | D counts as matching N on cost |
| T3 | 0.05 or one file | recall or precision a graph arm may lose |
| T4 | 0.10 or two files | recall gain that earns B |
| T6 | 2% of the median session's weighted tokens | M6 below which the fallback picks B |

Rules, in order; the first that applies is the outcome. Comparisons are per-task medians over the
repetitions, against arm N. A run that writes no plan, hits its cap, errors, fails G1 or shows
leakage is excluded; a task with fewer than 2 valid runs in an arm is unscored; fewer than 2
scored tasks is inconclusive.

1. **Inconclusive** if, on a majority of scored tasks, a graph arm's within-arm M1 range is wider
   than the gap between its median and N's. Then add repetitions or fall to rule 5.
2. **A** if G's median M1 is at least T1 below N on 2 of 3 tasks, and G's M3, M4, M7 are each no
   more than T3 below N on every task.
3. **B** if D's M1 is within T2 of N and D beats N on M3 or M4 by T4 with M7 intact on 2 of 3
   tasks; or if G or D beats N on M3 or M4 by T4 with M7 intact while costing more (a
   cost-for-safety trade, reported as such).
4. **C** if neither G nor D beats N on M1 by T1, nor on M3 or M4 by T4, on 2 of 3 tasks.
5. **Fallback from rule 1:** B if M6 < T6, else C. A is not reachable here.
6. Anything else is unresolved; the human decides.

## 7. Method

**Phase 0 (free):** overhead census (decision point: if M6 ≪ T6, the human may stop and choose
B vs C on accuracy alone); freeze the corpus (`corpus.py`); historical M1 for the budget; planted
defects (`eval.py --plant`); clone checks (`make_clone.sh`, `check_clone.sh`). Record results here.

**Phase 1 (optional, descriptive):** classify findings in saved reviews into duplicate / missed
dependent / other, by keyword script and by an agent blind to the task name.

**Phase 2 (paid):** tasks {{t1}}, {{t2}}, {{t3}} with bases and ticks in `harness.json`. Each run:
a fresh clone holding only the base commit's history (`git init`, `fetch <main> <sha>`,
`checkout --detach`), no remote, empty per-project memory, one model, one prompt, arm order
coin-flipped per pair, subagents disallowed, a dollar cap. Arms G and N; D only if the repo's
agents demonstrably use the graph. Prompt: "go {{task}}. Do the session-start reading, then stop
before your first edit and write `PLAN.md` in the repository root listing: files to create,
existing files to change, existing modules to reuse, and callers that the change affects. Do not
spawn subagents." Repetitions: 3 per arm per task. Leakage scan after each run for `--all`,
`reflog`, `fetch`, later task names and the harness's own path.

**Phase 3:** `score_batch.py`; optional blind grader for plan items outside the reference
(valid = would need to change or be imported in some correct implementation; plan stripped of
graph vocabulary; grader guesses the arm and the guess is recorded); apply section 6 in order and
write the decision with its numbers, exclusions and ranges.

## 8. Threats to validity

Small samples (report ranges; rule 1 guards); task representativeness (choose tasks of more than
one kind if you can); competing guides (README, build plan) present in every arm, so the result is
the graph's additional value; the reference is one solution (blind grader); orientation only;
instructions that changed between tasks (pairs share a base, so arms are comparable, tasks less
so); mixed-model history (budget guide only); scorer bias (author uses the graph daily; have the
plan audited independently before running it).

## 9. Constraints

No run touches live services, personal data or the real checkout. Clones live under a temporary
directory, have no remote, make no commits, and are removed after scoring (plans are copied out
first). Graph builds use `graphify update <code_root>` from the clone root only, with every model
key unset. Agent tokens are spent only after the human approves the budget and the caps.

## 10. Budget (fill from Phase 0 and a pilot pair)

| Spend | Runs | Estimate | Cap |
| --- | --- | --- | --- |
| Pilot pair | 2 | {{..}} | 2 × per-run cap |
| Phase 2 | 3 tasks × 2 arms × 3 reps = 18 | 18 × pilot median | per run 2 × pilot median; total 1.5 × estimate |
| Phase 3 grader | 1 pass | ~10K tokens per item | 1.5 × estimate |

Decisions needed from the human: stop after Phase 0 or fund Phase 2; the T values; the model;
the budget and caps.
