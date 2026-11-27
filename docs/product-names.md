# Catálogo de nomes recuperado da conversa

**Fonte:** nomes lidos pelo usuário em voz durante a retomada de 15/11/2026. Este catálogo recupera o conteúdo disponível da tabela, sem alegar acesso à tabela original inteira. Um nome mencionado não comprova implementação nem aprovação comercial definitiva.

## 1. Associações explicitamente lidas

| Área/função dita pelo usuário | Nome lido |
| --- | --- |
| Ingestão; conectores para APIs | **NØUS Connect** |
| Engenharia semântica | **NØUS Semantic Studio** |
| Processamento e distribuição | **NØUS Transaction Core** |
| Analytics | **NØUS Analytics** |
| Console | **NØUS Cloud Console** |

As três primeiras funções foram associadas explicitamente aos nomes na fala. Nas duas últimas linhas, os rótulos funcionais apenas repetem Analytics/Console; a fala não definiu seu escopo detalhado.

**Correção importante:** `nous-ia-contract` é o repositório do componente examinado. Seu título atual não substitui os nomes do catálogo. A associação recuperada para engenharia semântica é **NØUS Semantic Studio**. Não afirmar que todo o ecossistema, cada motor interno ou o repositório inteiro recebeu automaticamente esse nome.

## 2. Nomes de componentes e conceitos mencionados

A lista abaixo preserva nomes que o usuário leu, com repetições eliminadas. A distribuição entre submódulos, arquitetura, alternativas de nome e produtos independentes **ainda não foi estabelecida na fala**. Nenhuma linha desta seção significa que o módulo já existe no código.

| Nome recuperado | Observação de fidelidade |
| --- | --- |
| Semantic Studio | Repetição do nome da área de engenharia semântica, sem prefixo na segunda leitura |
| Canonical Core | Nome mencionado; limite funcional a definir |
| Contract Hub | Nome mencionado; limite funcional a definir |
| Normalization Engine | Nome mencionado; não substituir automaticamente por Semantic Normalization Engine |
| Raw Data | Nome/conceito mencionado; fronteira com Connect não foi estabelecida |
| Integration Runtime | Nome mencionado |
| Transaction Core | Repetição sem prefixo; relacionado ao nome NØUS Transaction Core na tabela lida |
| Event Hub | Nome mencionado; não identifica um serviço de nuvem já escolhido |
| Data Pipeline | Nome mencionado |
| Analytics | Repetição sem prefixo |
| Raw Data Layer Architecture | Designação de arquitetura mencionada |
| Layered Intelligence Architecture | Designação de arquitetura mencionada |
| Mapping Resolver | Nome mencionado mais de uma vez; registrar uma vez, sem criar módulos duplicados |
| Semantic Transformer | Nome mencionado |
| Canonical Validator | Nome mencionado |
| Canonical Store | Nome mencionado; não é banco já implementado |
| TMM — Telemetry Mapping Metrics | Sigla e expansão ditas pelo usuário; manter essa expansão sem substituir por outra |
| Event Telemetry Mapping | Nome mencionado; nenhuma sigla adicional foi confirmada |
| Correlation Layer | Nome audível; a palavra Semantic veio próxima, mas a composição Semantic Correlation Layer não foi inequívoca |
| Semantic Normalization Engine | Nome mencionado; relação com Normalization Engine a definir |
| Adaptative Engine | Grafia baseada na transcrição; houve hesitação Adapter-/Adaptative. Não corrigir silenciosamente para outro nome comercial |

## 3. Pistas e alternativas ainda incertas

| Trecho/nome | Estado do registro |
| --- | --- |
| NØUS Cloud | Pista dada antes da leitura mais longa; não presumir equivalência com NØUS Cloud Console |
| NØUS Observe; NØUS Operational Intelligence | Nomes/expressões da fala anterior; associação entre marca e descrição não ficou inequívoca |
| NØUS Predict / Predictive | Trecho da fala anterior com hesitação; grafia e relação entre nome e descrição permanecem incertas |
| Workflow | O usuário considerou e descartou/hesitou no momento da procura; não tratar como nome escolhido |
| Canvas / NØUS Editor | O usuário disse algo próximo a Canvas NØUS Editor e indicou incerteza. Não consolidar um nome final a partir disso |

## 4. Referência AWS e restrição de marca

O usuário informou que a ferramenta havia sido discutida tomando **AWS Entity Resolution como referência**, mas que não queria um nome próprio com **Entity** ou **Resolution**, para evitar semelhança com o produto AWS.

Essa restrição foi recuperada. A comparação não demonstra equivalência técnica, não escolhe AWS como implementação e não transforma todos os nomes da seção 2 em alternativas aprovadas para a mesma ferramenta.

## 5. Relação com a implementação e o handoff

O código inspecionado continua sendo FastAPI, avaliação heurística, validação JSON Schema e adaptadores sintéticos determinísticos. Registrar os nomes não instala Connect, Studio, Transaction Core, Analytics, Console, os agentes ou os módulos internos.

A [especificação detalhada](product-specification.md) descreve os requisitos e o catálogo técnico, distinguindo-os da implementação. O [registro da conversa](session-decisions-2026-11-15.md) preserva a evolução e as correções. O [relatório de validação](validation-2026-11-15.md) contém as evidências executadas.
