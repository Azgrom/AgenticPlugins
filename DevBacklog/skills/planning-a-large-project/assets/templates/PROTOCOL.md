# PROTOCOL — <<NAME>>

Loaded when: before acting. Up: [STATE](STATE.md)

authority: planning-a-large-project contract 3 sha256:<<CONTRACT_SHA>>; tool <<TOOL>>
specialists: {skill — path — what it governs, or none}
storage: <<STORAGE>>; backlog pushes: never
authorization: {what the user authorized} ({source}, {date})
delivery: code commits by {user | agent when asked}; backlog commits by {user | agent at accepted checkpoints}
stop classes:
- boundary: every task boundary → continue after the reviewed checkpoint
check profiles:
- {name}: `{command}` → {expected result}
inherited exceptions: {known failures with finding IDs, or none}
session: {continue to the successor | end the session after each accepted checkpoint}; compaction: {rule or none}
user instructions:
- {date} "{verbatim}" — scope {scope}
