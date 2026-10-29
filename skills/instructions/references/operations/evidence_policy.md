# Política de evidência

Consultar para autenticar origem, verificar regra atual ou resolver conflito. Entrada: afirmação e fontes; saída: evidência classificada e limite de uso. Esta política classifica e qualifica uma afirmação ou fonte, sobretudo em exame e uso geral; a verificação de trabalhos acadêmicos segue [evidência acadêmica](academic_evidence.md).

Classes: EXTERNAL_FACT, METHOD_RULE, HEURISTIC, INFERENCE. Origem de dado: measured, user_reported, external, inferred. Confiança: verified (documento primário ou medição rastreável), strong (corroboração independente), provisional (hipótese), unknown (sem base). Essas dimensões não se substituem; relato pode ser fielmente registrado sem o fato relatado estar verificado.

Priorizar documento do organizador/emissor e versão vigente, depois arquivo institucional e fontes independentes que sustentem o mesmo item. Resolução própria não confirma ocorrência histórica nem cria gabarito oficial. Agregador ajuda a localizar, sem autenticar sozinho. Para gabarito corroborado, exigir pelo menos duas fontes independentes convergentes e resolução compatível; rotular como strong, nunca official. Para questão oficial, checar caderno, versão, numeração, alternativa e retificação. Para autoria, declarar autoral e citar o material técnico usado, sem exigir falsa ocorrência.

Conflito: conferir edição, data, preliminar versus definitivo e retificação; resolver tecnicamente; buscar fonte adicional. Se persistir divergência material, não usar o item para medir domínio nem emitir conclusão definitiva. Em regra externa cuja vigência não possa ser confirmada, manter unknown e não decidir como se vigente.

Classificar estabilidade STATIC, PERIODIC ou CURRENT; registrar retrieved_at e effective_version quando relevante. Não existe TTL universal: nova edição, aviso oficial, legislação ou versão técnica mudam a necessidade de verificar. Ausência de retificação localizada não equivale a prova de inexistência; registrar o alcance da busca.

Para confronto acadêmico, aplicar [evidência acadêmica](academic_evidence.md). A confiança aqui qualifica a afirmação efetivamente verificada: identidade bibliográfica confirmada não torna um resultado publicado verdadeiro ou universal. Duas fontes convergentes podem corroborar um gabarito, mas não certificam consenso científico. Não aplicar critérios de exame a teorias, interpretações ou hipóteses abertas.

Complementos opcionais: [proveniência](../schemas/evidence_record.schema.json) ao registrar evidência; [critério de elegibilidade de item](question_gate.md) ao selecionar questão; [falhas](failure_modes.md) quando a evidência não puder ser obtida.
