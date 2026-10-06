# Protocolo de avaliação do tutor

Consultar somente ao executar ou interpretar testes. Entrada: casos e release; saída: evidência auditável.

Separar superfície estrutural (JSON/links/pacote), comportamento offline (respostas com skill candidata) e ativação real no host. PASS em uma não prova outra.

1. Resolver caso e fixture antes da execução; fonte real, se necessária, deve estar disponível. Fixture é explicitamente sintética e não pode ser apresentada como questão histórica.
2. Dar ao executor somente skill, user_input e fixture_context. Ocultar expected/forbidden e resultados prévios. Para comparação causal, manter ambiente/modelo e usar contexto independente; registrar quando isso não ocorrer.
3. Capturar resposta completa, módulos lidos quando observáveis e ações efetivamente executadas. Não exigir exposição de raciocínio interno. Em análise de suite na mesma thread, declarar que casos não tiveram contextos isolados.
4. Avaliador confronta a saída com cada expected/forbidden, inspecionando semanticamente. PASS=critérios atendidos; FAIL=violação; BLOCKED=fixture/capacidade essencial ausente; NOT_RUN=não aplicado. Contagem/regex não bastam para julgamento comportamental.
5. Registrar case_id, versão, método, observação, evidência da saída, resultado e limite. Cobertura exige enumerar quais casos foram executados. Cinco repetições da mesma demanda medem consistência nessa demanda; não provam confiabilidade geral.

P0 falho exige correção antes de release. Reavaliar cenários afetados após mudança. Não inventar rollback: restauração exige ferramenta/release autorizada e verificação. O benchmark não autoriza editar dados reais de estudantes.

Na comparação acadêmica, medir separadamente descoberta pelo catálogo, resposta conceitual, adequação de evidência, vínculo afirmação/fonte, respeito ao acesso real e regressões de atendimento avulso. Preservar as saídas de base e candidata. Se a base já acertar um cenário, relatar preservação; não inventar ganho. Nova cobertura ou contrato não demonstram superioridade estatística geral. Interrupção do executor e ausência de acesso são registradas, nunca convertidas em PASS por conveniência.
