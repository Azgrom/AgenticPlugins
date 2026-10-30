# DevBacklog: manutenção do pacote

Estas orientações aplicam-se a `DevBacklog/` e seus descendentes. Os caminhos
abaixo são relativos a esta raiz de pacote.

## Estrutura e dependências

- `plugin.json` contém os metadados portáteis; `.codex-plugin/plugin.json` contém
  a descoberta de habilidades e a interface do Codex. Mantenha identidade,
  versão e apresentação coerentes entre ambos.
- As três habilidades em `skills/` são distribuídas juntas.
  `planning-a-large-project` fornece o contrato, os modelos e `scripts/backlog.py`;
  `executing-a-large-project` e `reviewing-and-planning-tests` dependem deles.
  Preserve os caminhos relativos entre essas habilidades.
- Preserve o inglês das habilidades, referências e modelos importados. Mudanças
  na documentação do pacote devem manter comandos e nomes de habilidades exatos.
- Mantenha as cópias distribuídas autocontidas. Instalações pessoais em
  `~/.agents/skills` ou `~/.codex/skills` não são dependências do pacote.

## Contexto por alteração

| Alteração | Leitura |
| --- | --- |
| Contrato, modelos ou CLI do backlog | [Contrato](skills/planning-a-large-project/references/contract.md) e [armazenamento](skills/planning-a-large-project/references/storage.md) |
| Retomada e recuperação da execução | [Habilidade de execução](skills/executing-a-large-project/SKILL.md) e [recuperação](skills/executing-a-large-project/references/recovery.md) |
| Revisão e planejamento de testes | [Habilidade de revisão](skills/reviewing-and-planning-tests/SKILL.md) e as referências pertinentes nela vinculadas |
| Manifestos e distribuição | [README.md](README.md) e `scripts/validate_package.py` |

Os fluxos das habilidades são conteúdo do produto. Incorporar ou editar esses
arquivos não inicia um backlog nem instala hooks no repositório de publicação.

## Verificação

Execute na raiz deste pacote, com Python 3.10 ou superior e Git 2.42 ou superior:

```sh
python3 -B scripts/validate_package.py
python3 -B -m unittest discover -s skills/planning-a-large-project/scripts/tests -p 'test*.py'
git diff --check
```

O validador verifica a estrutura, a coerência dos manifestos, os arquivos de apoio
e os links locais da documentação. Os testes exercitam a CLI, os contratos,
worktrees e hooks em repositórios temporários. Modelos contêm referências aos
arquivos do backlog gerado; sua resolução é exercitada pelos testes da CLI.

Essas verificações não executam as habilidades em um modelo nem comprovam sua
descoberta no hospedeiro. Ao mudar instruções, registre separadamente os cenários
conversacionais exercitados, suas saídas e os casos não executados.
