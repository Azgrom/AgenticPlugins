# Aceitação de versão

Consultar somente ao validar ou alterar o tutor. Responsabilidade: critérios de release; não carregar durante aula.

Antes de salvar versão: validar formato de pacote, referências, schemas/fixtures e preservação de identidade, assets, prompts e integrações; executar cenários P0 pertinentes às mudanças e registrar saídas reais. Todos os P0 executados devem passar; P0 não executado fica NOT_RUN/BLOCKED e não autoriza alegar validação completa. Registrar limitações e manter testes de ativação no host separados dos testes offline. Não alegar suite completa por validar palavras-chave.

| Risco | Casos condicionais |
|---|---|
| Resposta avulsa, contexto, correta/marcada e tom | [atendimento avulso](cases/standalone_response.json) |
| Graduação/pós-graduação, fontes, método e confronto de entendimento | [tutoria acadêmica](cases/academic_tutoring.json) |
| Origem, chave e elementos essenciais | [autenticidade](cases/authenticity.json) |
| Banco fechado, autoria e auxílio proibido | [certificação](cases/certification_security.json) |
| Exame/versão e fronteiras | [roteamento](cases/exam_routing.json) |
| Pontos, anulação e escalas | [pontuação](cases/scoring.json) |
| Duplicação, revelação e memória | [estado](cases/state_integrity.json) |
| Capacidades, injection e falha | [ferramentas](cases/tool_failures.json) |
| Progressão e replanejamento | [pedagogia](cases/pedagogy.json) |
| Formatos e execução observada | [texto/prática](cases/written_and_practical.json) |
| Adaptação e validade | [acessibilidade](cases/accessibility.json) |

Complemento opcional: [protocolo de execução](evaluation_protocol.md), ao aplicar suite; [adversariais](adversarial_tests.md), ao testar pressão. Para verificação documental local: executar `python3 scripts/validate_package.py` a partir da raiz desta skill. Se houver validador JSON Schema 2020-12 completo, usar adicionalmente para conformidade geral; o script portátil cobre apenas os keywords usados no pacote.

Para os testes executáveis do contrato acadêmico, executar `python3 -m unittest discover -s scripts -p 'test*.py'` a partir da raiz da skill. Também é possível executar `python3 scripts/test_academic_contract.py`; ambos os modos devem passar.
