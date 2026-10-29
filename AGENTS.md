# Tutor: contexto do repositório

Tutor é um plugin portátil de tutoria composto por instruções Markdown, contratos
JSON e validação em Python. O pacote distribuível está em `src/`; a raiz organiza
o trabalho no repositório e acomoda documentação e automação de CI externas ao
pacote.

## Escopo

Estas orientações aplicam-se ao repositório inteiro. Antes de editar uma área,
leia o `AGENTS.md` mais específico existente nela; suas orientações prevalecem
nessa área em caso de conflito. Os caminhos deste arquivo são relativos à raiz do
repositório.

A manutenção do repositório é distinta da execução do tutor. Ao revisar arquivos
de habilidades, trate suas instruções como conteúdo do produto; a leitura não
ativa o papel de tutor na conversa de desenvolvimento.

## Organização e empacotamento

- Mantenha em `src/` os arquivos que integram o plugin: manifestos, habilidades,
  referências, recursos e validação do pacote. Documentação e automação de escopo
  geral pertencem fora de `src/`.
- Use `src/` como raiz do pacote ao instalar, validar ou preparar sua distribuição.
  Inclua os arquivos ocultos necessários, especialmente
  `src/.codex-plugin/plugin.json`.
- Os caminhos dos manifestos, como `./skills` e `./assets`, são relativos à raiz
  do pacote. Preserve essa base ao trabalhar a partir da raiz do repositório.
- Ao criar automação, explicite o diretório de trabalho e reutilize os
  validadores do pacote. Mantenha as regras de validação nos scripts responsáveis,
  evitando implementações divergentes na CI.

## Contexto por tarefa

| Quando | Leitura |
| --- | --- |
| Alterar arquivos em `src/` ou sua integração com a CI e o empacotamento | [src/AGENTS.md](src/AGENTS.md): regras locais, contratos e avaliação |
| Entender a arquitetura e as capacidades do plugin | [src/README.md](src/README.md): visão geral e referências técnicas |
| Redigir ou revisar documentação | [Habilidade language](src/skills/language/SKILL.md): convenções de redação |

Siga os links pertinentes à tarefa. As políticas do tutor, os contratos de
registros e o protocolo de avaliação permanecem nos módulos indicados pela
orientação local. Preserve o português das instruções do tutor e o idioma
existente nos demais arquivos e identificadores.

## Verificação

Para alterações no pacote ou na automação que o valida ou empacota, execute na
raiz do repositório, com Python 3 e sua biblioteca padrão:

```sh
python3 -B src/skills/instructions/scripts/validate_package.py
python3 -B -m unittest discover -s src/skills/instructions/scripts -p 'test*.py'
```

Para alterações apenas na documentação da raiz, confira os caminhos, os links e
os comandos afetados. Em qualquer alteração, execute:

```sh
git diff --check
```

As verificações Python cobrem a estrutura e os contratos do pacote. Para mudanças
de comportamento, siga também a avaliação indicada em `src/AGENTS.md`; os testes
offline não comprovam o comportamento do tutor nem sua ativação no hospedeiro.
Ao concluir, informe as alterações, as verificações executadas e suas limitações,
distinguindo falhas preexistentes de regressões.

## Manutenção deste contexto

Mantenha aqui somente orientações de escopo geral e links com condições claras de
leitura. Quando novas áreas de CI ou documentação existirem, acrescente seus
pontos de entrada reais; coloque regras específicas no `AGENTS.md` da área.
Atualize caminhos e comandos junto com mudanças de estrutura. Detalhes do produto
e registros temporários de trabalho permanecem fora deste ponto de entrada.
