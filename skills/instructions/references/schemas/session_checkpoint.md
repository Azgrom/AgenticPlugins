# Ponto de retomada de sessão 2.0

Consultar somente quando o usuário fornecer ou pedir ponto de retomada. Responsabilidade: resumir continuidade, sem copiar histórico. Não gerar ponto de retomada por encerramento de resposta; contexto e memória do ambiente hospedeiro bastam ao atendimento avulso.

O [contrato JSON](session_checkpoint.schema.json) é obrigatório quando produzir ponto de retomada estruturado. Preservar contexto de exame/versão/etapa/idioma/jurisdição, IDs de estado/eventos, pendências, revisões e próxima ação. Dados desconhecidos são null; listas desconhecidas não afirmam ausência de fatos: registrar missing_data. created_at só é preenchido quando houver relógio disponível; sem ele, null.

Não incluir enunciados completos, transcrição de diálogo, dados pessoais ou raciocínio interno. Referenciar somente objetos recuperáveis; se armazenamento não existir, apresentar os objetos mínimos juntos como conteúdo copiável. IDs sozinhos sem resolução não permitem retomada.

Ponto de retomada fornecido pelo estudante continua user_reported até verificar origem e conteúdo. Um esquema válido não autentica estado. Ao trocar alvo, retomar o contexto correspondente, sem importar nota ou domínio.

Complementos opcionais: [estado](../operations/state_policy.md) ao rederivar progresso; [migração](migration.md) para versão 1.0; [ferramentas](../operations/tool_policy.md) para gravação real. Sem gravação confirmada, dizer “ponto de retomada apresentado”, nunca “salvo”.
