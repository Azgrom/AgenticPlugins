# Aceitação de versão

Consultar somente ao validar ou alterar o tutor. Responsabilidade: critérios de aceitação da versão; não carregar durante aula.

Antes de salvar versão: validar formato de pacote, referências, esquemas, dados de teste e preservação de identidade, recursos, prompts e integrações; executar cenários P0 pertinentes às mudanças e registrar saídas reais. Todos os P0 executados devem passar; P0 não executado fica NOT_RUN/BLOCKED e não autoriza alegar validação completa. Registrar limitações e manter testes de ativação no ambiente hospedeiro separados dos testes offline. Não alegar execução da bateria completa por validar palavras-chave.

| Risco | Casos condicionais |
|---|---|
| Resposta avulsa, contexto, correta/marcada e tom | [atendimento avulso](cases/standalone_response.json) |
| Documentação, linguagem e preservação de contratos | [roteamento para language](cases/language_routing.json) |
| Graduação/pós-graduação, fontes, método e confronto de entendimento | [tutoria acadêmica](cases/academic_tutoring.json) |
| Origem, chave e elementos essenciais | [autenticidade](cases/authenticity.json) |
| Banco fechado, autoria e auxílio proibido | [certificação](cases/certification_security.json) |
| Exame/versão e fronteiras | [roteamento](cases/exam_routing.json) |
| Pontos, anulação e escalas | [pontuação](cases/scoring.json) |
| Duplicação, revelação e memória | [estado](cases/state_integrity.json) |
| Capacidades, injeção de instruções e falha | [ferramentas](cases/tool_failures.json) |
| Autenticação do estudante, fontes e limites de recuperação | [fontes acadêmicas](cases/academic_sources.json) |
| Progressão e replanejamento | [pedagogia](cases/pedagogy.json) |
| Formatos e execução observada | [texto/prática](cases/written_and_practical.json) |
| Adaptação e validade | [acessibilidade](cases/accessibility.json) |
| Mapeamento de currículo e metas SISU | [currículo e seleção](cases/curriculum_and_selection.json) |

**Cobertura por módulo.** O campo opcional `covers` de um caso nomeia o módulo que ele exercita; módulos sem bateria de testes própria são cobertos assim:

| Módulo | Casos |
|---|---|
| critical_reading | ACAD-03, 07, 09, 10, 11, 15 |
| literature_review | ACAD-04, 05, 06, 13, 15, 16 |
| research_methodology | ACAD-07, 10, 11, 14 |
| spaced_review | PED-01, 02, 03 (somente P1; sem caso P0 por risco pedagógico, não factual) |
| question_gate | AUTH-03, 04, 05, 06; ACCESS-01, 02 |
| curriculum_mapping | MAP-01 |
| sisu_methodology | SISU-01 |

Esses vínculos são por leitura dos casos, não resultado de execução.

Revisão da estrutura e do roteamento: [resultados de 2026-10-28](results/context_structure_2026_10_28.json), com saídas efetivas, referências lidas e casos não executados. Consultar somente ao auditar essa alteração.

Distribuição sem declarações de servidores: [resultados de 2026-10-29](results/skills_only_2026_10_29.json), com três cenários de recuperação executados em contextos independentes, saídas completas e limites. Consultar somente ao auditar essa alteração.

Auditoria histórica da revisão 1.3.0: [resultados e limites](results/evaluation_1_3_0.json), [saídas da candidata](results/candidate_1_3_0.json) e [observação da base](results/baseline_1_2_0.json). Foram avaliados semanticamente os 15 novos cenários offline; isso não executa as 77 definições nem comprova ativação no ambiente hospedeiro. Os registros preservam as configurações e saídas daquela revisão; não descrevem dependências do pacote atual. Consultar esses arquivos somente ao auditar a revisão.

Complemento opcional: [protocolo de execução](evaluation_protocol.md), ao aplicar a bateria de testes; [adversariais](adversarial_tests.md), ao testar pressão. Para verificação documental local: executar `python3 scripts/validate_package.py` a partir da raiz desta habilidade. Se houver validador JSON Schema 2020-12 completo, usar adicionalmente para conformidade geral; o script portátil cobre apenas as palavras-chave usadas no pacote.

Para os testes executáveis do contrato acadêmico, executar `python3 -m unittest discover -s scripts -p 'test*.py'` a partir da raiz da habilidade. Também é possível executar `python3 scripts/test_academic_contract.py`; ambos os modos devem passar.
