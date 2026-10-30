# DevBacklog

DevBacklog reúne três habilidades para planejar projetos, retomar sua execução e
revisar a suficiência dos testes. Os planos usam um backlog: um conjunto de
arquivos com contratos de tarefas, evidências, pontos de controle e uma próxima
ação explícita para outra sessão.

| Habilidade | Finalidade |
| --- | --- |
| [planning-a-large-project](skills/planning-a-large-project/SKILL.md) | Criar ou revisar um plano por fases, com contratos e critérios de aceitação |
| [executing-a-large-project](skills/executing-a-large-project/SKILL.md) | Retomar o trabalho a partir de `STATE.md` e avançar por tarefas verificadas |
| [reviewing-and-planning-tests](skills/reviewing-and-planning-tests/SKILL.md) | Auditar evidências de testes e planejar as correções necessárias |

## Uso

Após carregar este pacote em um hospedeiro com suporte a habilidades, solicite,
por exemplo:

- `Use $planning-a-large-project para planejar esta migração.`
- `Use $executing-a-large-project para continuar o backlog indicado.`
- `Use $reviewing-and-planning-tests para revisar os testes desta solução.`

As habilidades são mantidas em inglês. Planejamento fornece o
[contrato compartilhado](skills/planning-a-large-project/references/contract.md),
os modelos e a CLI `backlog.py`. Execução e revisão usam esses mesmos arquivos;
as três habilidades devem permanecer juntas.

## Requisitos e armazenamento

Os scripts usam Python 3.10 ou superior e sua biblioteca padrão. O armazenamento
em Git exige Git 2.42 ou superior para criar uma branch órfã em outro worktree.
O perfil `directory` atende projetos sem Git. Consulte as
[regras de armazenamento](skills/planning-a-large-project/references/storage.md)
para criação, sincronização e recuperação.

A instalação dos hooks de proteção é opcional e requer autorização do usuário.
Instalar o plugin não cria um backlog nem instala esses hooks. A revisão de testes
produz um plano de correção; a execução desse plano passa pela habilidade de
execução e pela aceitação humana definida no protocolo.

## Estrutura e distribuição

`DevBacklog/` é a raiz completa do pacote:

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

O identificador técnico é `devbacklog`, e o nome de exibição é `DevBacklog`.
`plugin.json` contém os metadados portáteis; `.codex-plugin/plugin.json` aponta
para `./skills` e apresenta o plugin ao Codex. Referências, modelos, scripts,
metadados das habilidades e testes acompanham o pacote.

## Validação local

Execute na raiz do pacote (`DevBacklog/`):

```sh
python3 -B scripts/validate_package.py
python3 -B -m unittest discover -s skills/planning-a-large-project/scripts/tests -p 'test*.py'
```

Para preparar o ZIP a partir da raiz do repositório de publicação:

```sh
python3 -B ci/package.py --plugin devbacklog
```

O resultado é `dist/devbacklog.zip`, com o conteúdo do pacote diretamente na
raiz do arquivo. As verificações locais cobrem estrutura e comportamento da CLI;
a execução conversacional e a ativação no hospedeiro exigem avaliação separada.

## Licença

[MIT](LICENSE).
