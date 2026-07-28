# markdownlint-cli2

## Purpose

This repository uses `markdownlint-cli2` for its planned Markdown CI gate.
This document identifies the exact tool and defines how agents must research,
configure, and upgrade it.

Implementation is tracked by
[Issue #5](https://github.com/tonyrosario/agentic-foundry/issues/5). Until that
issue is complete, the repository does not have an authoritative pinned CI
version.

## Canonical identity

- CLI, package, and executable: `markdownlint-cli2`
- Canonical upstream:
  <https://github.com/DavidAnson/markdownlint-cli2>
- CI integration:
  <https://github.com/DavidAnson/markdownlint-cli2-action>
- Underlying rule engine:
  <https://github.com/DavidAnson/markdownlint>

Do not substitute similarly named projects:

- `markdownlint-cli` is a different command-line interface.
- `DavidAnson/markdownlint` is the rule engine used by CLI2, not the CLI.
- `markdownlint/markdownlint` is a different project.
- `vscode-markdownlint` is an editor integration, not the project CI tool.

## Project sources of truth

Once Issue #5 is implemented, use these sources in order:

1. The pinned action SHA and version comment in the Markdown lint workflow.
2. The checked-in `.markdownlint-cli2.*` configuration.
3. Documentation for the matching `markdownlint-cli2` release.
4. Documentation for the exact `markdownlint` engine version reported by that
   CLI2 execution, when researching individual rule behavior.

A workstation-global installation is not a version authority for this project.
Do not infer CI behavior from it.

For CLI behavior—including configuration discovery, globs, fixing, output, and
exit codes—use `markdownlint-cli2` documentation. For rule semantics, engine
documentation may be used only for the engine version reported by the pinned
CLI2 execution, and it must be identified as rule-engine documentation.

Do not use documentation from a repository's `main` branch to justify
version-specific behavior in the pinned CI gate.

## CI policy

The project workflow must:

- Use `DavidAnson/markdownlint-cli2-action`.
- Pin the action to a full commit SHA.
- Record the corresponding action release and expected CLI2 version beside the
  pin.
- Preserve output that identifies the CLI2 and rule-engine versions.
- Use the checked-in CLI2 configuration.
- Run with least-privilege GitHub permissions.
- Fail when the configured lint scope contains violations.

The gate applies only to this repository. Copying a foundry asset into another
project does not install or activate Markdownlint. A full fork contains the
versioned workflow and configuration, but the fork owner may retain, modify,
disable, or remove them.

## Configuration changes

Before changing lint rules, file scope, configuration, or CI:

1. Read the workflow and checked-in CLI2 configuration.
2. Confirm syntax and behavior against the matching CLI2 release.
3. Match rule research to the engine version reported by CLI2.
4. Keep exclusions narrow and explain why they are necessary.
5. Stop and report a specification gap if the pinned version or authoritative
   configuration cannot be determined.

Do not reformat preserved audits or adjudications merely to satisfy a general
style preference.

## Upgrades

Treat a CLI2 or action upgrade as one scoped change. Update and verify together:

- The action commit SHA and release comment.
- The expected CLI2 and rule-engine versions.
- Configuration compatibility.
- The clean-run result.
- A negative test demonstrating that a known violation still fails CI.
