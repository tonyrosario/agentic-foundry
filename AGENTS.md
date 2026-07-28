# Agent Instructions

This repository uses GitHub as the source of truth for roadmap and delivery work.

## Before Starting

Confirm the issue is grabbable:

- Labeled `agent-ready`
- Not labeled `blocked`
- Not labeled `in-progress`
- Every issue it lists as "Blocked by" is closed. A blocker closed by a pull request counts only if that pull request merged.

If any check fails, do not implement it. If a blocker's resolution is ambiguous, comment instead of guessing.

Claim the issue before working: add the `in-progress` label (`gh issue edit <number> --add-label in-progress`) and assign yourself if possible. Keep `agent-ready` in place. An existing `in-progress` label is a hard hands-off: that issue belongs to another agent. If you stop before opening a PR, remove `in-progress` and comment why.

Read:

- The assigned issue
- Linked parent issues
- Relevant repository docs
- Existing code near the change

## Project Tooling

Load a tooling guide only when the task involves that tool:

- For Markdown lint rules, configuration, CI, or version changes, read
  [`docs/tooling/markdownlint-cli2.md`](docs/tooling/markdownlint-cli2.md).
  This repository uses `markdownlint-cli2`, not `markdownlint-cli`.

## Rules

You may:

- Create a branch
- Make scoped changes
- Commit changes
- Open a pull request
- Request human review
- Comment with blockers

You may not:

- Merge pull requests
- Enable auto-merge
- Push directly to protected branches or bypass branch protection
- Change roadmap priorities
- Work on issues not marked `agent-ready`
- Introduce dependencies unless explicitly allowed by the issue
- Touch secrets, auth, billing, production deploy config, permissions, or infrastructure unless explicitly allowed by the issue
- Expand scope beyond the issue

## Code comments

Keep comments sparse. Add one only when it records information the code cannot
make clear: a non-obvious rationale, constraint, invariant, workaround, or gotcha.

Do not narrate code, restate self-evident logic, add section dividers, or modify
comments/docstrings/type annotations on code unrelated to the requested change.
Prefer clearer names or smaller functions over explanatory comments.

Follow existing project conventions for public API documentation and type annotations.

## Workflow

1. Restate the task in your own working notes.
2. Inspect the repository before editing.
3. Make the smallest useful change.
4. Run relevant verification.
5. Open a PR linked to the issue.
6. Include verification and limitations in the PR body.

## Working in Parallel

- One issue = one branch = one worktree. Never work two issues in one checkout.
- Keep single-checkout build state (virtualenvs, `node_modules`, `.terraform`) inside your own worktree; content-addressed caches may be shared.
- Rebase on the default branch before opening a PR, and again after any blocker's PR merges.
- Never touch another worktree's files or branches.

## Shared Files

Some files are shared across issue scopes: root tooling and dependency manifests, CI config, and files that define global structure. These are owned by designated issues, not by whoever needs them first.

- If your task needs a change to a shared file and another issue owns that change, comment a blocker and stop. Do not make the edit.
- If no issue owns it, comment on your own issue and wait for a human to designate an owner or allow the edit.
- Sequence-numbered artifacts (ADRs, migrations): claim the next number in an issue comment before opening your PR.

<!-- TODO(stack): list this repo's shared files, e.g. dependency
     manifests, lockfiles, CI config. Filled by the stack-layer issue. -->

## If Blocked

Stop and comment on the issue with:

- Why you are blocked
- What you tried
- What you need from a human

## Pull Requests

Every PR must include:

- Linked issue
- Summary
- Verification
- Known limitations
- Confirmation that forbidden areas were not touched unless explicitly allowed

Humans merge. Agents do not merge.

A pull request is required for every change to the default branch, mechanically enforced two ways: the ruleset itself — by default it has no bypass actor at all, so it binds your credential the same as everyone else's — and `.claude/settings.json`, which denies `gh pr merge`, `gh api`, and ruleset edits regardless of ruleset state. If `gh ruleset check` reports `current_user_can_bypass: true` (or `always`) for your identity, that means the operator has explicitly opted into an admin bypass; it is not something the merge flow needs (zero required approvals already lets the operator merge without one — see the solo-mode ADR) and is not itself a blocker for you, since it's the operator's own credential grant, not license for you to invoke it. Confirm instead that `.claude/settings.json` still denies those three command classes. If that deny list is missing or weakened, stop and report a blocker.

Human review is the merge gate. In team repositories it is enforced by required approvals. In solo repositories it is enforced by policy: agents never merge, never enable auto-merge, and never edit rulesets or protections.

---

Scaffolded from [github-agent-roadmap-bootstrap](https://github.com/tonyrosario/github-agent-roadmap-bootstrap).
