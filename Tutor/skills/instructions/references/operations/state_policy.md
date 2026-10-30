# Estado e eventos pedagógicos

Consultar somente sob pedido explícito de registro/histórico, interpretação de ponto de retomada fornecido ou correção de resultado previamente registrado. Entrada: evidência disponível; saída: estado derivado com origem e limites. Não carregar para resposta avulsa.

O tutor não constrói memória própria nem entrevista para preencher estado. Contexto e memória disponibilizados pelo ambiente hospedeiro atendem à consulta habitual; esses contratos preservam compatibilidade e pedidos específicos de continuidade. Não registrar automaticamente cada questão ou gerar ponto de retomada ao final de resposta.

Separar exam_key, profile_version e domain_id. exam_key inclui exame, edição/versão, etapa, idioma e jurisdição; uma mudança cria contexto novo. Estados: NI não iniciado; P em estudo; A aprendizagem operacional; R revisão devida; RT reforço; GRAD consolidado longitudinalmente. Transições usuais NI→P; P→A/RT; RT→P; A→R/GRAD; R→A/RT/GRAD. Resultado de avaliação é evento, nunca estado permanente.

Aplicar event_id uma vez. Corrigir por novo evento com supersedes_event_id; preservar resposta/resultado originais e rederivar estado. Eventos medidos exigem observação; relato permanece user_reported. Após revelar resposta, autocorreção não altera acerto independente original. Dica, consulta, repetição ou item contaminado ficam registrados e separados de evidência independente.

Anulação/retificação: registrar novo evento. Para domínio, excluir item inválido do denominador e rever inferência. Para resultado segundo edital, calcular efeito oficial em trilha separada (inclusive atribuição de pontos a todos quando prevista). Não somar o histórico e seu evento substituto.

Sem estado persistente confiável, reconstruir apenas contexto atual ou usar ponto de retomada informado como relato até validar origem. Não inventar revisões atrasadas. Campos desconhecidos são null/ausentes conforme contrato. Para conflitos de versão armazenada, reler e reconciliar; não sobrescrever silenciosamente. Retomada: pedido atual prevalece; sem pedido específico, atividade interrompida, revisão devida e próxima ação.

Complementos opcionais: [assunto](../schemas/student_state.schema.json) para contrato; [evento](../schemas/assessment_event.schema.json) para registro; [ponto de retomada](../schemas/session_checkpoint.md) para retomada compacta; [migração](../schemas/migration.md) para versão antiga.
