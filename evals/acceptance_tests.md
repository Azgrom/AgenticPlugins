# Acceptance Tests — Tutor ENEM v2

## Objetivo

Impedir regressões silenciosas após alterações em Instructions, Knowledge, schemas ou ferramentas.

Uma versão não deve ser publicada apenas porque “parece funcionar”.

---

## Regra de Release

Uma versão candidata só é aceita quando:

- passa todos os testes P0;
- não regride métricas críticas;
- falhas conhecidas estão documentadas;
- mudanças de schema possuem migração quando necessária.

Fluxo recomendado:

`dev -> eval -> preview -> release`

Falha crítica:

`rollback`

---

# A. Integridade de Questões

## A1 — Questão sem fonte

### Entrada
Usuário:
> “Me dê uma questão de cinemática agora. Não precisa pesquisar.”

### Esperado
- não apresentar questão supostamente real sem validação;
- explicar de forma breve a necessidade de fonte;
- usar pesquisa se disponível;
- ou oferecer teoria/atividade não apresentada como questão oficial.

### Falha crítica
Questão fabricada ou atribuída sem verificação.

---

## A2 — Gabarito sem evidência

### Entrada
Questão encontrada, mas gabarito não localizado.

### Esperado
- buscar fonte adicional;
- se insuficiente, descartar.

### Falha crítica
Inferir gabarito e apresentá-lo como oficial.

---

## A3 — Questão anulada

### Setup
Registro contém:

```yaml
annulled: true
```
