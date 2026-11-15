# Documentação e handoff

Este índice organiza o conteúdo existente e as decisões discutidas em 15/11/2026. A documentação distingue implementação inspecionada, demonstração relatada pelo usuário, requisitos e propostas ainda não executadas.

1. **[Especificação detalhada do produto e dos módulos](product-specification.md)** — escopo, terminologia, modos de uso, contratos, agentes, armazenamento, canvas, RAW, linha do tempo, tecnologias, critérios de aceite e pendências.
2. **[Registro da evolução da conversa e das decisões](session-decisions-2026-11-15.md)** — sequência de requisitos, correções do usuário, experimentos e decisões de escopo. É uma reconstrução identificada, não uma transcrição literal ou exportação integral do chat.
3. **[Estado do código e evidências de validação](validation-2026-11-15.md)** — revisão examinada, testes efetivamente executados e entradas/saídas fictícias reproduzíveis.
4. [Integração de eventos e contratos](event-integration-blueprint.md) — proposta anterior de RAW/inbox, canônico/outbox, revisão e consumidores.
5. [Simuladores offline](simulators.md) — contrato de entrada e limites do normalizador sintético existente.
6. [Pedido canônico fictício](canonical-delivery-order.md) — schema de pedido completo proposto, distinto do evento parcial produzido pelo simulador.

O **nome comercial da ferramenta permanece pendente**: o usuário esclareceu que o nome/título do repositório não é o nome do produto e mencionou uma tabela anterior que não está disponível no trecho consultado. Não tratar o título deste repositório como confirmação de naming.

Para continuar o trabalho, começar pela especificação e pelas pendências. Não interpretar diagramas, nomes propostos, screenshots conceituais ou arquivos de schema como funcionalidades já implementadas.
