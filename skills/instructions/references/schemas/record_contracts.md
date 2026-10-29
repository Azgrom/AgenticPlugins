# Contratos de registro

Consultar somente ao estruturar ou validar dados. Não carregar todos os esquemas em aula.

| Objeto solicitado | Contrato específico |
|---|---|
| Afirmação/fonte/proveniência | [evidence_record](evidence_record.schema.json) |
| Revisão acadêmica com vínculo entre afirmações e fontes | [academic_review](academic_review.md) |
| Exame e regra por versão | [exam_profile](exam_profile.schema.json) |
| Atividade e elegibilidade | [item_record](item_record.schema.json) |
| Resposta, resumo ou correção | [assessment_event](assessment_event.schema.json) |
| Estado de um único assunto | [student_state](student_state.schema.json) |
| Resumo de retomada | [session_checkpoint](session_checkpoint.schema.json) |

Os arquivos usam JSON Schema 2020-12, com IDs locais e referências relativas. Adicionar campo exige versão/migração; campo desconhecido não é preenchido por suposição. `profile_schema_version` identifica formato; `profile_version` identifica revisão do perfil daquele exame. Uma estrutura válida não confirma autenticidade, licença, observação ou vigência. Os contratos não impõem coleta, entrevista ou registro ao atendimento avulso.

Invariantes entre registros exigem [integridade de registros](record_integrity.md), somente quando validar objetos relacionados. O script local verifica o conjunto explicitamente fornecido; não presume backend ou objetos remotos recuperáveis.

O script de verificação do pacote valida a estrutura documental e os dados de teste do subconjunto utilizado; não oferece StudentStateStore, motor de pontuação, migração automática ou autenticação de fontes.
