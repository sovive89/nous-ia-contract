# Documentação e handoff

## Referência rápida de nomes recuperados

| Área | Nome lido pelo usuário |
| --- | --- |
| Ingestão e conectores para APIs | **NØUS Connect** |
| Engenharia semântica | **NØUS Semantic Studio** |
| Processamento e distribuição | **NØUS Transaction Core** |
| Analytics | **NØUS Analytics** |
| Console | **NØUS Cloud Console** |

O [catálogo de nomes](product-names.md) preserva também Canonical Core, Contract Hub, Mapping Resolver e os demais termos lidos, distinguindo associações explícitas de nomes ainda incertos. Esta tabela não atesta implementação.

## Documentos

Este índice organiza o conteúdo existente e as decisões discutidas em 15/11/2026. A documentação distingue implementação inspecionada, demonstração relatada pelo usuário, requisitos e propostas ainda não executadas.

1. **[Especificação detalhada do produto e dos módulos](product-specification.md)** — escopo, terminologia, modos de uso, contratos, agentes, armazenamento, canvas, RAW, linha do tempo, tecnologias, critérios de aceite e pendências.
2. **[Registro da evolução da conversa e das decisões](session-decisions-2026-11-15.md)** — sequência de requisitos, correções do usuário, experimentos e decisões de escopo. É uma reconstrução identificada, não uma transcrição literal ou exportação integral do chat.
3. **[Estado do código e evidências de validação](validation-2026-11-15.md)** — revisão examinada, testes efetivamente executados e entradas/saídas fictícias reproduzíveis.
4. [Integração de eventos e contratos](event-integration-blueprint.md) — proposta anterior de RAW/inbox, canônico/outbox, revisão e consumidores.
5. [Simuladores offline](simulators.md) — contrato de entrada e limites do normalizador sintético existente.
6. [Pedido canônico fictício](canonical-delivery-order.md) — schema de pedido completo proposto, distinto do evento parcial produzido pelo simulador.

Na publicação inicial, o nome comercial não havia sido recuperado. Na retomada, o usuário leu os nomes da tabela, registrados acima e no catálogo. A associação explícita de engenharia semântica é **NØUS Semantic Studio**; não tratar o título do repositório como nome do produto, nem promover automaticamente os demais candidatos a marcas aprovadas.

Restrição de marca posteriormente esclarecida: a referência discutida foi AWS Entity Resolution, mas o nome próprio da ferramenta **não deve conter “Entity” nem “Resolution”**. Isso não permite reconstruir por suposição o nome escolhido na tabela anterior.

Para continuar o trabalho, começar pela especificação e pelas pendências. Não interpretar diagramas, nomes propostos, screenshots conceituais ou arquivos de schema como funcionalidades já implementadas.
