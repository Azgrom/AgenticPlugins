# Orientações para o repositório

## Escopo

Estas orientações aplicam-se a `Tutor/` e seus descendentes.
Os caminhos abaixo são relativos à raiz do pacote (`Tutor/`).

Tutor é um plugin portátil de tutoria composto por instruções Markdown, contratos
e fixtures JSON e scripts de validação em Python. Trate a manutenção do repositório
separadamente da ativação do tutor. Preserve o português das instruções voltadas
ao tutor e o idioma existente no código e nos identificadores.

## Leitura prévia às alterações

- Para alterações no comportamento ou no roteamento do tutor, leia
  `skills/instructions/SKILL.md` e `skills`; depois,
  leia apenas os módulos pertinentes à alteração. CORE define as invariantes do
  tutor; mantenha cada política detalhada no módulo responsável por ela, sem
  duplicá-la no ponto de entrada.
- Ao adicionar, mover ou remover módulos, atualize os links de roteamento
  aplicáveis e `skills/instructions/lookup/knowledge-index.json`. Os caminhos no
  ponto de entrada e no índice são relativos à raiz da habilidade; os links nos
  módulos de referência são relativos ao arquivo que os contém.
- Para alterações nos registros, consulte a documentação pertinente em
  `skills/instructions/references/schemas` e mantenha esquemas, fixtures e
  verificações do validador alinhados. Os esquemas descrevem contratos, não um
  serviço de persistência implementado.
- Para alterações no tutor e validação de versões, leia
  `skills/instructions/references/evals/acceptance_tests.md`. Ao executar casos
  comportamentais, leia também `evaluation_protocol.md` nesse diretório.

## Restrições de edição

- Preserve a tutoria direta, sob demanda, incluindo apoio acadêmico fora do
  contexto de provas. ENEM é uma especialização explícita, não o contexto
  presumido de toda solicitação.
- Mantenha a proveniência factual, os limites de acesso às fontes e os registros
  opcionais do estudante coerentes com CORE e os módulos de políticas pertinentes.
- Trate `skills/instructions/references/instructions.zip` como artefato legado;
  as instruções ativas pertencem aos módulos Markdown extraídos. Não o adicione ao
  roteamento ativo nem o descompacte para consultas rotineiras de contexto.
- O empacotamento tem dois manifestos distintos: `plugin.json` e
  `.codex-plugin`; a apresentação da habilidade também consta em
  `skills`. Ao alterar metadados, examine todos os
  locais pertinentes e preserve suas diferentes estruturas. Altere identidade,
  dados de autoria, prompts, recursos e versões apenas dentro do escopo solicitado.
- O validador Python usa a biblioteca padrão e aceita um subconjunto explícito das
  palavras-chave de JSON Schema. Uma nova palavra-chave de esquema exige suporte
  correspondente no validador e cobertura de testes com casos relevantes de
  aceitação e rejeição.

## Verificação

Execute estes comandos na raiz do pacote (`Tutor/`):

```sh
python3 -B skills/instructions/scripts/validate_package.py
python3 -B -m unittest discover -s skills/instructions/scripts -p 'test*.py'
git diff --check
```

Relate as falhas conforme observadas e distinga falhas existentes de regressões.
O validador do pacote verifica contratos e restrições de empacotamento, incluindo
limites de texto dos manifestos. Examine a asserção que falhou antes de alterar
metadados ou enfraquecer uma verificação.

O validador informa citações datadas (`consultado em YYYY-MM-DD`) como dados
informativos, não como falhas. Ao editar uma citação datada, verifique novamente a
fonte e atualize a data; trate uma data antiga como indicação para nova
verificação, não como prova de que a fonte continua atualizada.

As verificações offline não executam os casos comportamentais do tutor nem
verificam a ativação no ambiente hospedeiro. Para alterações de comportamento,
execute os casos P0 pertinentes conforme o protocolo de avaliação e registre as
saídas efetivas; classifique os casos não executados como NOT_RUN ou BLOCKED. Nos
relatórios de conclusão, apresente separadamente os resultados das verificações
estruturais, da avaliação comportamental e da ativação no ambiente hospedeiro.
