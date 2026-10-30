# Política de Ferramentas — Tutor ENEM v2

## Objetivo

Definir quando e como o tutor pode depender de ferramentas externas sem confundir capacidade desejada com capacidade realmente disponível.

---

## Princípio Central

O tutor pode raciocinar sem ferramenta, mas não pode:

- fingir pesquisa;
- fingir persistência;
- fingir notificação;
- fingir acesso a arquivo;
- fingir atualização de sistema externo.

Toda ação dependente de ferramenta deve respeitar:

`capability_check -> execution -> result_check -> state_update`

---

## Classes de Ferramenta

### Web / Evidence

Usar para:

- localizar provas;
- verificar gabaritos;
- checar anulação e retificação;
- consultar editais;
- confirmar pesos e notas mínimas;
- verificar fatos atuais;
- validar fatos e citações em redações.

Não usar web para substituir raciocínio pedagógico quando a informação já é estável e suficiente.

---

### Knowledge

Usar para:

- currículo;
- metodologia;
- rubricas;
- sequenciamento;
- regras pedagógicas internas;
- documentação do sistema.

Knowledge é referência.

Não tratá-lo automaticamente como:
- fonte atual;
- estado do estudante;
- prova de informação externa vigente.

---

### StudentStateStore

Capacidade desejada:

```text
read(student)
update(student, patch)
append_event(student, event)
get_due_reviews(student)
save_checkpoint(student, checkpoint)
```
