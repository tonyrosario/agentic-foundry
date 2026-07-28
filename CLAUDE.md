# Claude Code Instructions

Use `AGENTS.md` as the source of truth for agent instructions.

Do not duplicate policy here. Update `AGENTS.md` instead.

## Permissions

`.claude/settings.json` holds the base tool policy: git, `gh issue`, `gh pr create/view/checks/diff`, and read-only `gh ruleset` commands are allowed; `gh pr merge`, `gh api`, and ruleset or repo edits are denied. The deny list is the mechanical backstop for the merge gate in `AGENTS.md` — do not weaken it.

`gh api` is denied wholesale because it can perform any mutation (including merging) regardless of other deny rules. If a task genuinely needs a raw API call, stop and comment on the issue; a human runs it.

`.claude/settings.local.json` is a machine-local override and is gitignored — never commit it. Do not use it to re-allow a denied command: deny always wins over allow in Claude Code regardless of which settings file the rule is in, so a re-grant is both inert and misleading policy.

---

Scaffolded from [github-agent-roadmap-bootstrap](https://github.com/tonyrosario/github-agent-roadmap-bootstrap).

<!-- STACK EXTENSION POINT: add your project's toolchain (test runner,
     linter, build commands) to the "allow" list in .claude/settings.json.
     This is filled by the stack-layer starter issue, not at bootstrap. -->
