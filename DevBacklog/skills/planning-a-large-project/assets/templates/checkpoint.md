# {id} checkpoint — {kind}

Loaded when: reviewing or resuming {id}. Up: [STATE](../STATE.md)

kind: {planning | accepted | recovery | replan | closeout}
task: {id} / {step}; plan revision {n}; predecessor {path or none}; time {UTC ISO}
artifact: code {sha12} {clean or dirty:hash12}; backlog {sha12 or uncommitted}

| Check | Command | Expected | Observed | Evidence |
| --- | --- | --- | --- | --- |
| {name} | `{command}` | {expected} | {observed, exit code} | [{file}](../evidence/{file}) |

findings: {finding — disposition, or none}
limits: {what these checks cannot establish}
acceptance: {pending | human "verbatim user words" (source, date) | policy <stop class>}
next: {task / step / action}
