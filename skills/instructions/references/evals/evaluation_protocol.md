# Protocolo de avaliação do tutor

Consultar somente ao executar ou interpretar testes. Entrada: casos e versão; saída: evidência auditável.

Separar superfície estrutural (JSON/links/pacote), comportamento offline (respostas com habilidade candidata) e ativação real no ambiente hospedeiro. PASS em uma não prova outra.

1. Preparar o caso e os dados de teste antes da execução; fonte real, se necessária, deve estar disponível. Os dados de teste são explicitamente sintéticos e não podem ser apresentados como questão histórica.
2. Dar ao executor somente a habilidade, user_input e fixture_context. Ocultar expected/forbidden e resultados prévios. Para comparação causal, manter ambiente/modelo e usar contexto independente; registrar quando isso não ocorrer.
3. Capturar resposta completa, módulos lidos quando observáveis e ações efetivamente executadas. Não exigir exposição de raciocínio interno. Em análise de bateria de testes na mesma conversa, declarar que casos não tiveram contextos isolados.
4. O avaliador confronta a saída com cada critério expected/forbidden, inspecionando semanticamente. PASS=critérios atendidos; FAIL=violação; BLOCKED=ausência de dados de teste ou capacidade essencial; NOT_RUN=não aplicado. Contagem/regex não bastam para julgamento comportamental.
5. Registrar case_id, versão, método, observação, evidência da saída, resultado e limite. Cobertura exige enumerar quais casos foram executados. Cinco repetições da mesma demanda medem consistência nessa demanda; não provam confiabilidade geral.

Falha em caso P0 exige correção antes de publicar a versão. Reavaliar cenários afetados após mudança. Não alegar restauração de versão anterior sem executá-la: a restauração exige ferramenta e versão autorizadas, além de verificação. A avaliação comparativa não autoriza editar dados reais de estudantes.

Na comparação acadêmica, medir separadamente descoberta pelo catálogo, resposta conceitual, adequação de evidência, vínculo afirmação/fonte, respeito ao acesso real e regressões de atendimento avulso. Preservar as saídas de base e candidata. Se a base já acertar um cenário, relatar preservação; não inventar ganho. Nova cobertura ou contrato não demonstram superioridade estatística geral. Interrupção do executor e ausência de acesso são registradas, nunca convertidas em PASS por conveniência.
