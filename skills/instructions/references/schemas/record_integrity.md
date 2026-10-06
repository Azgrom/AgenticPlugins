# Integridade entre registros

Consultar somente ao validar registros relacionados. Entrada: objetos e fontes recuperáveis fornecidos; saída: relações resolvidas ou rejeição explícita. Não carregar em explicação avulsa.

O verificador local recebe os seis registros primários dos contratos. Listas opcionais `event_history`, `item_records` e `evidence_records` fornecem objetos adicionais; não são um serviço de armazenamento. IDs devem ser únicos e resolvidos nesse conjunto. Fontes de perfil, item, pesos e mínimos apontam para `evidence_id`, com conteúdo recuperável; referências textuais não bastam. Evidência verificada continua sujeita à conferência real da fonte.

- Exigir exam_key e profile_version compatíveis em atividades, eventos e estado; comparar todos os campos do contexto de checkpoint com o perfil, inclusive edição, etapa, idioma e jurisdição. `profile_schema_version` não é revisão do perfil.
- Material restrito é DISCARD em qualquer modalidade; não aceitar TRAINING_ONLY como evasão dessa regra.
- Origem do evento deve corresponder à dos itens. Resumo misto tem material_type=null e eventos de origem resolvidos; discriminar trilhas e denominadores na apresentação. Não inferir comparabilidade ou calibragem por um schema válido.
- `metric.official=true` designa resultado externo verificado de exame, não cálculo local que usa critérios oficiais. Resultado autoral é formativo. Relatório oficial requer evento OFFICIAL_RESULT, origem external e evidência externa verificada; retificação exige original oficial recuperável.
- CORRECTION exige original recuperável no mesmo contexto e com os mesmos itens; preservar ambos, aplicar só a revisão vigente. Após anulação, o evento histórico conserva a elegibilidade registrada à época, mas não entra no estado atual. Exigir elegibilidade atual somente em eventos não substituídos. Rejeitar autorreferência, ciclo, referência órfã, duplicação de IDs e aplicação de qualquer evento substituído ao estado atual.
- Resolver evidência, bases e eventos derivados. `raw_accuracy=numerator/denominator`, com numerator≤denominator; ajuda e resposta após solução não viram acerto independente. Peso positivo e mínimo têm componente, unidade/escala e fonte explícitos.

Esses testes validam relações, não autenticidade, implementação de pontuação, migração automática ou persistência. Validação estrutural não comprova desempenho do usuário.

Complementos opcionais: [contratos](record_contracts.md), para localizar o schema específico; [política de estado](../operations/state_policy.md), para interpretar histórico explicitamente solicitado.
