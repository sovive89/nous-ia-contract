# Contrato canônico fictício — nous.delivery.order.v1

**Escopo:** pedido de delivery para simulações iFood e 99Food. Modelo **interno NØUS**, não schema oficial de qualquer plataforma. O contrato JSON Schema está em `schemas/nous.delivery.order.v1.json`.

## Identidade e eventos
- `order_id`: identidade interna NØUS; não usar diretamente o ID da plataforma como identidade global.
- `external_order_id`: identificador da origem, com `source`, `merchant_id` e `tenant_id` como contexto.
- `event_id` pertence ao **envelope de evento** (`schemas/event-envelope.schema.json`), não ao agregado de pedido. O envelope carrega `event_type`, `occurred_at`, `schema_ref` e o pedido no `payload`.
- `source_status` preserva o valor recebido. `status=UNKNOWN` quando não houver mapeamento de status aprovado; **não inventar equivalência**.
- O contrato de pedido inclui `occurred_at` como instante da versão observada; em eventos, usar o timestamp do envelope como fonte de verdade e reconciliar explicitamente.

## Financeiro
Inteiros em centavos de BRL. A regra esperada é `subtotal_minor + delivery_fee_minor - discount_minor = total_minor`, mas JSON Schema sozinho não verifica a igualdade; implementar validação de domínio. Cada `line_total_minor` deve ser coerente com quantidade, preço e descontos por item; como o MVP não modela descontos por item, exigir `quantity * unit_price_minor == line_total_minor` nos fixtures.

## Estados e valores ausentes
Enums de status e pagamento são **vocabulário NØUS fictício**. `UNKNOWN` indica falta de conhecimento; não equivale a `PENDING`. Cliente é opcional e pode ser null para evitar PII desnecessária. O status de entrega não é o mesmo que status de pedido.

## Pipeline esperado
RAW original imutável → identificação do conector → validação estrutural → mapeamento explícito de campos e unidades → consulta RAG a contratos versionados → avaliação opcional Jev/ML → auditor → Policy Engine → revisão humana para ambiguidade → persistência canônica + outbox. No MVP atual, apenas normalização sintética parcial existe; o schema novo não está automaticamente aplicado ao endpoint.

## Próximos gates
1. Gerar fixtures completos equivalentes de duas fontes.
2. Implementar `normalize_order` para este contrato com validação de domínio.
3. Exibir comparação RAW/campo mapeado/canônico no dashboard.
4. Persistir decisões, versão do mapeamento e referências documentais.
