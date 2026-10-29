# Tutor

Tutor é um plugin de tutoria com IA baseado em instruções, voltado à preparação
para provas e ao estudo acadêmico. Este repositório contém suas instruções
modulares, metadados do plugin, contratos de registros estruturados e materiais de
avaliação. Destina-se a colaboradores, revisores e desenvolvedores que examinam ou
adaptam o tutor.

As instruções de tutoria são escritas principalmente em português brasileiro.
Abrangem explicações conceituais, análise de questões, avaliações escritas e
práticas, leitura crítica e orientação de pesquisa nos níveis de graduação,
mestrado e doutorado. ENEM, concursos públicos e certificações profissionais têm
perfis específicos; a tutoria acadêmica também atende a demandas fora do contexto
de provas.

O nome de exibição é **Tutor**, definido nos dois manifestos e nos metadados da
habilidade principal. O campo `name` dos manifestos mantém o identificador técnico
`gpt-93c3cf04200c123c0971bae96376e92e`, distinto do nome exibido.

## Arquitetura

O pacote disponibiliza duas habilidades: [instructions](skills/instructions/SKILL.md),
para tutoria, e [language](skills/language/SKILL.md), para redação e revisão de
documentação. Ambas são descobertas em `skills`; o manifesto de compatibilidade
do Codex aponta para esse diretório. O tutor encaminha pedidos de documentação,
relatórios e comentários explicativos no código à habilidade `language`.

O ponto de entrada de `instructions` encaminha as solicitações de tutoria a módulos
de referência específicos:

1. [CORE](skills/instructions/references/CORE.md) define a missão comum, as regras
   de precedência e as restrições factuais e operacionais.
2. As políticas operacionais e os módulos de conhecimento fornecem as orientações
   necessárias para cada solicitação. Seu carregamento é condicional, para manter
   materiais sem relação com a solicitação fora do contexto ativo.
3. Os esquemas JSON definem registros opcionais de evidências, avaliações, estado
   do estudante, pontos de controle e revisões acadêmicas. Fixtures e verificações
   em Python testam esses contratos separadamente do comportamento conversacional
   do tutor.

O [índice de conhecimento](skills/instructions/lookup/knowledge-index.json) registra
os caminhos das referências e suas condições de carregamento. O ZIP legado é
mantido como artefato inativo; os módulos Markdown extraídos contêm as orientações
ativas.

O carregamento segue a divulgação progressiva descrita na
[especificação Agent Skills](https://agentskills.io/specification): descrição para
descoberta, ponto de entrada com CORE na ativação e referências sob demanda.
O ponto de entrada separa entregas, políticas condicionais e perfis de exame,
com links diretos aos módulos. As rotas são alternativas; uma referência só é
carregada quando seu gatilho se aplica. `language` concentra as orientações de
documentação e é consultada por referência, sem copiar suas regras para o tutor.

A recuperação de informações externas segue o
[roteamento de fontes acadêmicas](skills/instructions/references/operations/academic_sources.md).
Crossref fornece identificação bibliográfica e avisos editoriais; Semantic Scholar
permite descobrir fontes e navegar por citações e referências; Europe PMC é
restrito a solicitações biomédicas nesta arquitetura. Essas rotas de consulta às
fontes são condicionais e usam ferramentas elegíveis disponibilizadas pelo
ambiente hospedeiro, incluindo seus recursos nativos de busca e leitura.
O pacote distribui habilidades, sem configurar conexões com servidores externos.
A disponibilidade e a elegibilidade de cada ferramenta devem ser verificadas no
ambiente hospedeiro.

A habilidade mantém a responsabilidade pela classificação de evidências, seleção
de fontes, vinculação entre afirmações e evidências, avaliação crítica, explicação
pedagógica e comparação com a resposta do estudante. Uma ferramenta de recuperação
não é responsável pelo julgamento acadêmico. A
[política de autenticação](skills/instructions/references/operations/tool_policy.md#end_user_authentication)
exclui do fluxo normal dependências que exijam do estudante criar contas, fazer
login, fornecer chaves ou credenciais, iniciar períodos de teste ou contratar
assinaturas. Quando a capacidade anônima é insuficiente, o fluxo recorre a outra
rota anônima ou às ferramentas nativas do ambiente hospedeiro.

Este repositório não fornece aplicação autônoma, ambiente de execução de modelos,
banco de dados ou backend próprio de recuperação hospedado. Os esquemas, por si
sós, não implementam persistência, e a validação local não comprova compatibilidade
com o ambiente hospedeiro.

## Estrutura do repositório

| Localização | Responsabilidade |
| --- | --- |
| [plugin.json](plugin.json) | Identidade do plugin e metadados da interface OpenAI |
| [.codex-plugin/plugin.json](.codex-plugin/plugin.json) | Manifesto do plugin para Codex e descoberta de habilidades |
| [skills/instructions/SKILL.md](skills/instructions/SKILL.md) | Ponto de entrada da habilidade e roteamento condicional |
| [skills/language/SKILL.md](skills/language/SKILL.md) | Redação e revisão da linguagem da documentação |
| [agents/openai.yaml](skills/instructions/agents/openai.yaml) | Metadados de apresentação da habilidade |
| [references/operations](skills/instructions/references/operations/) | Políticas de evidências, contexto, estado, ferramentas e respostas |
| [references/knowledge](skills/instructions/references/knowledge/) | Métodos de ensino, orientação de pesquisa, currículos e perfis de provas |
| [references/schemas](skills/instructions/references/schemas/) | Esquemas JSON e documentação dos contratos de registros |
| [references/evals](skills/instructions/references/evals/) | Critérios de aceitação, casos comportamentais e fixtures sintéticas |
| [scripts](skills/instructions/scripts/) | Validação offline do pacote e testes de contratos acadêmicos |

## Restrições de projeto

- **Tutoria direta, sob demanda.** Uma pergunta clara deve receber resposta sem
  integração inicial obrigatória, levantamento obrigatório de perfil ou plano de
  estudos não solicitado.
- **Proveniência explícita.** Questões oficiais, amostras publicadas, materiais de
  prática licenciados, exercícios autorais e materiais fornecidos pelo usuário
  têm origens distintas. Exercícios gerados não devem ser apresentados como
  questões de provas anteriores.
- **Evidências proporcionais à afirmação.** Metadados bibliográficos, texto
  examinado e sustentação de uma conclusão exigem verificações distintas. A
  orientação de pesquisa deve preservar as incertezas e informar os limites de
  acesso às fontes.
- **Avaliação específica ao contexto.** Regras de provas, sistemas de pontuação e
  registros do estudante permanecem vinculados ao contexto pertinente. Padrões
  pedagógicos internos não são regras oficiais de pontuação.
- **Registros opcionais.** A tutoria não exige um banco de dados paralelo de
  estudantes. Histórico estruturado e pontos de controle são usados apenas quando
  solicitados explicitamente.

CORE e os módulos de políticas vinculados pelo ponto de entrada da habilidade
contêm os detalhes normativos.

## Validação local

Os scripts de validação usam Python 3 e sua biblioteca padrão. Na raiz do
repositório, execute:

```sh
python3 -B skills/instructions/scripts/validate_package.py
python3 -B -m unittest discover -s skills/instructions/scripts -p 'test*.py'
git diff --check
```

O validador do pacote verifica referências Markdown, índice de conhecimento,
restrições dos manifestos, esquemas, fixtures e integridade dos registros. Seu
validador de esquemas aceita apenas as palavras-chave de JSON Schema implementadas
explicitamente; não é uma implementação geral do Draft 2020-12. Os testes unitários
verificam a integridade das revisões acadêmicas e a ausência de declarações de
servidores no pacote. Eles não comprovam a disponibilidade das ferramentas do
ambiente hospedeiro nem o acesso anônimo às fontes.

Verificações estruturais, avaliação comportamental e ativação no ambiente
hospedeiro são formas distintas de verificação. Os scripts Python não executam um
modelo de tutoria nem os casos comportamentais. Para esses casos, siga os
[critérios de aceitação](skills/instructions/references/evals/acceptance_tests.md)
e o [protocolo de avaliação](skills/instructions/references/evals/evaluation_protocol.md),
registre as respostas efetivas e informe os casos não executados como `NOT_RUN` ou
`BLOCKED`. Fixtures são materiais sintéticos de teste, não conteúdo autenticado de
provas nem evidências de pesquisa.

A [revisão de estrutura de 2026-10-28](skills/instructions/references/evals/results/context_structure_2026_10_28.json)
registra a fundamentação, as medidas de tamanho textual, as saídas de cinco casos
offline e os limites da avaliação. A redução de palavras não mede diretamente
tokens, atenção ou desempenho do modelo.

## Como contribuir

Comece por [AGENTS.md](AGENTS.md) para consultar as orientações de edição e
verificação do repositório. Para alterações de comportamento, leia o ponto de
entrada da habilidade, CORE e os módulos afetados. Mantenha cada política
detalhada no módulo responsável por ela e atualize os links de roteamento e o
índice de conhecimento ao adicionar, mover ou remover referências.

Alterações nos esquemas devem incluir fixtures alinhadas e cobertura do validador
para registros aceitos e rejeitados. Alterações de metadados devem considerar os
dois manifestos do plugin e os metadados de apresentação da habilidade. Preserve o
português das instruções voltadas ao tutor e restrinja alterações de identidade ou
marca ao escopo da contribuição pretendida.

Em um pull request, explique o comportamento ou contrato alterado, liste as
verificações e os casos comportamentais pertinentes efetivamente executados e
distinga falhas existentes de regressões. Informe separadamente os resultados da
ativação no ambiente hospedeiro quando ela tiver sido testada.

## Licença

[MIT](LICENSE).
