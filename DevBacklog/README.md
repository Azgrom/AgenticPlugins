# DevBacklog

DevBacklog brings together three skills for planning projects, resuming their
execution, and reviewing test adequacy. Plans use a backlog: a set of files with
task contracts, evidence, checkpoints, and an explicit next action for another
session.

| Skill | Purpose |
| --- | --- |
| [planning-a-large-project](skills/planning-a-large-project/SKILL.md) | Create or revise a phased plan with contracts and acceptance criteria |
| [executing-a-large-project](skills/executing-a-large-project/SKILL.md) | Resume work from `STATE.md` and progress through verified tasks |
| [reviewing-and-planning-tests](skills/reviewing-and-planning-tests/SKILL.md) | Audit test evidence and plan the necessary corrections |

## Usage

After loading this package into a host that supports skills, use prompts such as:

- `Use $planning-a-large-project to plan this migration.`
- `Use $executing-a-large-project to continue the specified backlog.`
- `Use $reviewing-and-planning-tests to review this solution's tests.`

The skills are maintained in English. The planning skill provides the
[shared contract](skills/planning-a-large-project/references/contract.md),
templates, and the `backlog.py` CLI. Execution and review use these same files;
the three skills must remain together.

## Requirements and storage

The scripts use Python 3.10 or later and its standard library. Git storage
requires Git 2.42 or later to create an orphan branch in another worktree.
The `directory` profile supports projects without Git. See the
[storage rules](skills/planning-a-large-project/references/storage.md)
for creation, synchronization, and recovery.

Installing protection hooks is optional and requires user authorization.
Installing the plugin does not create a backlog or install these hooks. Test
review produces a remediation plan; carrying out that plan requires the execution
skill and the human acceptance defined in the protocol.

## Structure and distribution

`DevBacklog/` is the complete package root:

```text
.codex-plugin/plugin.json
plugin.json
skills/
  planning-a-large-project/
  executing-a-large-project/
  reviewing-and-planning-tests/
scripts/validate_package.py
AGENTS.md
README.md
LICENSE
```

The technical identifier is `devbacklog`, and the display name is `DevBacklog`.
`plugin.json` contains portable metadata; `.codex-plugin/plugin.json` points to
`./skills` and presents the plugin to Codex. References, templates, scripts,
skill metadata, and tests are included in the package.

## Local validation

Run from the package root (`DevBacklog/`):

```sh
python3 -B scripts/validate_package.py
python3 -B -m unittest discover -s skills/planning-a-large-project/scripts/tests -p 'test*.py'
```

To prepare the ZIP from the root of the publishing repository:

```sh
python3 -B ci/package.py --plugin devbacklog
```

The output is `dist/devbacklog.zip`, with the package contents directly at the
archive root. Local checks cover structure and CLI behavior; conversational
execution and host activation require separate evaluation.

## License

[MIT](LICENSE).
