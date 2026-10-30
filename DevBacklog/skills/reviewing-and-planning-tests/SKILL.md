---
name: reviewing-and-planning-tests
description: Use when reviewing a solution's unit or integration test adequacy, auditing primitive and composed-type contracts, or planning test restructuring and missing coverage across projects.
---

# Reviewing and planning tests

Produce evidence requirements and an executable remediation backlog, not a test count or a coverage score.
This skill reviews and plans; remediation runs separately through `executing-a-large-project`.

## Establish the review

Use `planning-a-large-project` and its contract to create or resume the backlog. In a git project the backlog
lives on its own orphan branch, so the code under review contains no backlog files. For an existing backlog,
read STATE first and keep its progress. Record scope, authorization and the baseline identity
(`backlog.py sync`). If a companion skill is unavailable, keep the findings, name the missing dependency and
leave the backlog not ready.

## Review every project

Read the [review method](references/review-method.md). Inventory every project: root packages, excluded
projects, standalone harnesses and non-default targets. Inspect each one's actual test discovery, source
contracts and configurations. Done means every project has a report; unavailable evidence is a named gap,
never a silent omission.

Build primitive obligations and a recursive composition graph, then operation and case matrices for types,
interfaces, free functions, generics and macros. Keep sampled evidence, exhaustive finite-domain checks and
formal proof apart. Target 100% reachable statement and branch coverage for the declared configurations,
alongside contract and sequence evidence.

## Inventory first, judge later

Generate the inventory of existing tests with a script: project, file, line, name, runner and scope, with
`basis` set to `script`. Fill the judgment columns (obligation, category, destination, disposition) only for
the projects that can start next, by reading each test, with `basis` set to `read`. Every other project gets
an audit task, ordered before any task that moves its tests, that fills those columns for that project.
Never fill judgment columns from test names or patterns alone.

## Design the remediation

Read the [taxonomy](references/taxonomy.md) before proposing file moves: evidence category first, subsystem
second, preserving visibility and runner registration. Every existing test receives a keep, move, extend,
replace or remove disposition from its project's audit before it moves.

Tests expose Arrange → Act → Assert, and deliberate scenarios also assert intermediate transitions. Use named
parameterized cases or reproducible property runs. An explicit loop in a test body needs a recorded reason,
and moving an ordinary case loop into a helper does not supply one. Report interface deficiencies as design
findings with their own remediation ownership and authorization.

## Emit and hand off

Read [backlog output](references/backlog-output.md). Each project owns a phase. Each reviewable remediation
result is one task, and internal commands are its steps. Add the `review` stop class to PROTOCOL so that the
executor stops for human acceptance after every remediation task.

Map findings and obligations to tasks and acceptance checks, verify the dependency order and the preservation
of test discovery, and run `validate`. Write the planning checkpoint, then STATE, and report the backlog path,
the principal gaps and the next action. Planning readiness does not accept any future remediation task.
