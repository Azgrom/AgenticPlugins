# Session Checkpoint Schema — Tutor ENEM v2

## Objetivo

Permitir retomada confiável sem presumir memória entre conversas.

O checkpoint é um resumo operacional, não um histórico completo.

---

## Schema

```yaml
checkpoint_version: "1.0"

session:
  session_id:
  started_at:
  ended_at:
  type:
  completed: true

student_goal:
  target_exam:
  target_course:
  strategic_target:

plan:
  phase:
  week:
  current_priority:
  next_priority:

active_subject:
  area:
  discipline:
  topic:
  state:
  tier:

activity:
  type:
  activity_id:
  completed_items:
  total_items:
  accuracy:
  hints_used:
  weak_subtopics: []
  error_profile: {}

reviews:
  completed: []
  due: []
  next_due: []

essay:
  last_score:
  weak_competencies: []
  next_task:

simulation:
  last_date:
  main_findings: []

decisions:
  - decision:
    reason:

pending:
  - item:
    priority:
    reason:

next_action:
  action:
  rationale:

state_confidence:
  value: high | medium | low
  missing_data: []
```
