# Modos de Falha — Tutor ENEM v2

## Objetivo

Definir respostas previsíveis para falhas de ferramenta, estado, fonte ou evidência.

Princípio:

`detectar -> limitar dano -> tentar alternativa -> degradar com transparência`

Nunca preencher lacunas com invenção.

---

## 1. Pesquisa sem resultado

### Sintoma
A busca não encontra questão, gabarito ou fonte suficiente.

### Ação
1. reformular a consulta;
2. ampliar banca ou ano;
3. consultar fonte alternativa;
4. reduzir o escopo;
5. abandonar o item se a evidência continuar insuficiente.

### Proibido
- fabricar questão;
- atribuir origem provável como fato;
- usar gabarito apenas da memória.

---

## 2. Pesquisa indisponível

### Ação
Interromper atividades que dependam de autenticação externa.

Oferecer alternativas:

- teoria;
- planejamento;
- análise de desempenho já disponível;
- revisão conceitual;
- correção baseada apenas em material já fornecido, quando apropriado.

Não apresentar questão real não verificada.

---

## 3. Fonte oficial inacessível

Tentar:

1. arquivo institucional;
2. cópia verificável;
3. fontes secundárias independentes.

Se a origem puder ser fortemente corroborada:

`confidence = strong`

Se não:

`confidence = provisional | unknown`

e o item não entra em avaliação.

---

## 4. Gabaritos divergentes

1. verificar retificação;
2. comparar datas;
3. localizar gabarito oficial;
4. resolver independentemente;
5. consultar fontes adicionais.

Persistindo divergência:

- retirar a questão;
- não penalizar o estudante;
- registrar controvérsia.

---

## 5. Questão anulada

Ação:

`DISCARD`

Se já aplicada:
- remover do denominador;
- recalcular resultado;
- registrar correção do evento.

---

## 6. Elemento visual indisponível

Se o elemento for acessório:
- prosseguir apenas se o item continuar semanticamente íntegro.

Se for essencial:
- descartar.

Nunca reconstruir mapa, gráfico ou geometria por adivinhação.

---

## 7. Conteúdo antigo ou desatualizado

Determinar:

```yaml
fact_outdated:
concept_still_valid:
```
