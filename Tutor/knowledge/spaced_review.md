# Revisão Espaçada — Método v2

## Objetivo

Preservar retenção e detectar deterioração do domínio sem transformar revisão em calendário rígido.

Sequência padrão:

`1d -> 3d -> 7d -> 14d -> 30d -> 60d`

Os intervalos são regras internas do método, não prescrições oficiais do ENEM.

---

## Entrada no Ciclo

Um assunto entra em revisão quando:

- atingiu aprendizagem operacional;
- possui evidência suficiente de domínio;
- o tutor registrou `learned_at`;
- existe `next_due`.

Estado típico:

`A -> R`

---

## Unidade de Revisão

### Revisão de assunto
Preferência histórica:
- 10 a 15 questões;
- foco no mesmo assunto;
- amostra suficientemente variada.

### Revisão de disciplina
Pode misturar assuntos já aprendidos.

Preferência histórica:
- 5 a 8 itens por assunto quando o volume permitir.

### Revisão mesclada
Adequada sobretudo nas fases avançadas.

Misturar:
- assuntos;
- níveis de dificuldade;
- habilidades;
- disciplinas quando houver ganho interdisciplinar.

---

## Resultado

Registrar:

```yaml
review_id:
subject_id:
due_at:
completed_at:
n_items:
correct:
accuracy:
coverage:
hint_usage:
error_profile:
result:
next_due:
```
