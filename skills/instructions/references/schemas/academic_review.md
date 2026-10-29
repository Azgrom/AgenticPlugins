# Contrato de revisão acadêmica

Consultar somente quando o usuário pedir um registro estruturado de análise ou ao validar o tutor. Entrada: demanda, fontes e proposições; saída: objeto [academic_review](academic_review.schema.json). Não exige exame, perfil de estudante ou persistência.

`schema_version` identifica o formato. `sources` descreve identidade, nível real de leitura e estado editorial conhecido. Campos bibliográficos desconhecidos ficam nulos ou vazios; identificador ausente não é fabricado. `claims` liga cada proposição à fonte, localizador, relação e base da leitura. A razão e os limites distinguem a análise do tutor do que o autor relata.

`search_scope.kind` é `provided_material`, `targeted` ou `systematic`. Busca efetiva exige termos, locais e data; declarar `systematic` exige também escopo e processo documentados nas limitações/relato associado. O esquema não prova exaustividade nem avalia a qualidade da busca. Não mudar o rótulo para passar um teste.

As invariantes verificadas por `python3 scripts/validate_package.py` incluem IDs únicos, vínculo resolvido, localizador para texto inspecionado, resumo usado apenas no nível declarado e referência/data para consulta de status editorial. Registro editorial ou metadados não dão suporte a uma afirmação sobre conteúdo lido. Uma proposição sem evidência pode ser `unresolved`, com razão explícita. Fonte retratada não sustenta afirmação sem ressalva material.

Metadados rotulados como consultados exigem referência e nível de leitura diferente de `NONE`. `partially_supported` exige algum vínculo de suporte; vínculos apenas contrários não oferecem esse suporte. `unresolved` permite reconhecer explicitamente a ausência de evidência.

O validador verifica o conjunto fornecido, sem resolver serviços externos. Um JSON válido pode conter uma referência falsa; autenticidade exige [verificação de evidência](../operations/academic_evidence.md). Não apresentar validade estrutural como verdade científica ou revisão por pares. Os seis contratos anteriores permanecem compatíveis; este é um contrato adicional e opcional.
