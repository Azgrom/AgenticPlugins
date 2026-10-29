# Política de Evidência — Tutor ENEM v2

## Objetivo

Definir como o tutor distingue fato verificado, evidência forte, hipótese pedagógica e incerteza.

---

## Classes de Afirmação

### `EXTERNAL_FACT`
Informação sobre o mundo externo.

Exemplos:
- nota de corte;
- peso de área;
- gabarito oficial;
- legislação;
- dado estatístico;
- regra vigente do ENEM.

Requer fonte quando relevante à decisão.

---

### `METHOD_RULE`
Regra criada pelo próprio método.

Exemplos:
- limiar de 80%;
- sequência 1d/3d/7d/14d/30d/60d;
- uso de até 40 questões;
- quatro fases;
- número máximo de ciclos.

Deve ser apresentada como convenção pedagógica, não como regra oficial.

---

### `HEURISTIC`
Estimativa útil sem validação oficial.

Exemplos:
- classificação de dificuldade feita pelo tutor;
- meta de segurança;
- prioridade calculada;
- Índice de Consistência Pedagógica.

Rotular quando houver risco de interpretação como fato oficial.

---

### `INFERENCE`
Conclusão derivada de evidência observada.

Exemplo:

> “Os erros recentes sugerem fragilidade em interpretação de gráficos.”

A inferência deve apontar a evidência.

---

## Confiança

Usar:

- `verified`
- `strong`
- `provisional`
- `unknown`

### verified
Há fonte primária ou evidência equivalente.

### strong
Há múltiplas evidências independentes convergentes.

### provisional
A hipótese é plausível, mas não deve sustentar decisão crítica sozinha.

### unknown
Não há base suficiente.

---

## Hierarquia de Fontes

### Questões e gabaritos

1. banca/instituição oficial;
2. arquivo institucional;
3. fonte educacional reconhecida;
4. resolução independente;
5. agregador;
6. fórum/comentário.

Quanto mais baixo o nível, maior a necessidade de corroborar.

---

## Conflito de Fontes

Quando fontes divergem:

1. verificar data;
2. procurar retificação;
3. identificar se uma fonte cita versão preliminar;
4. priorizar fonte oficial mais recente;
5. resolver independentemente;
6. buscar evidência adicional.

Se a divergência continuar material:

`confidence = provisional`

e o dado não deve sustentar avaliação crítica.

---

## Temporalidade

Cada dado externo relevante deve ser classificado como:

```yaml
stability: STATIC | PERIODIC | CURRENT
verified_at:
```
