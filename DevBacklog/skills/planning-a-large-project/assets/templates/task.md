# {id} — {title}

Loaded when: executing or reviewing {id}. Up: [STATE](../STATE.md)

outcome: {what exists when this task is done}
requirements: {requirement IDs from PLAN, obligation IDs}
entry: {predecessor checkpoint, inputs and their versions}
owns: {paths this task may change}
excludes: {what must stay unchanged}
context: {path — the question it answers}
checks: {PROTOCOL profile} + {task-specific command → expected result}
exit: checkpoint checkpoints/{id}.md; successor {id or none}

## Steps

- [ ] {id}.1 {action} — done when {observable result}
- [ ] {id}.2 Review the result against this contract; write the checkpoint — done when validate passes

## Record

{unfinished step, operation IDs and log paths, observations needed to resume}
