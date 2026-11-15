# NØUS IA — Integração de eventos e contratos (proposta)

**Fonte:** skill enviada pelo usuário `aws-event-integration-lab-blueprint(1).skill` (SKILL.md, references/architecture-patterns.md, references/handoff-audit.md, references/research-and-cost.md).

**Estado:** especificado; **não implementado, não testado e não implantado na AWS**.

## Limites do MVP

O repositório atual contém FastAPI, avaliação heurística de campos, validação JSON Schema e testes de API. Ainda não há banco, autenticação real, inbox/outbox, event bus, AWS, Jev, RAG, ML treinado, Mem0 ou agente auditor. `tenant_id` fornecido no body **não constitui isolamento multi-tenant**.

## Fluxo canônico proposto

1. Autenticar origem e resolver `tenant_id` pela identidade autenticada, nunca confiar somente no payload.
2. Gravar `raw_event` e `inbox_receipt` na mesma transação; confirmar recebimento somente após commit durável.
3. Validar envelope, schema e semântica; classificar falha permanente versus transitória.
4. Gerar proposta de mapeamento com evidências, sem alterar o RAW.
5. Executar Python ML, Jev e OpenAI RAG quando habilitados; registrar provedores, versões e incerteza.
6. Submeter a fusão ao agente auditor (somente leitura); aplicar Policy Engine e revisão humana.
7. Persistir payload canônico, versão do contrato e outbox na transação de negócio.
8. Publicar outbox via worker, com entrega pelo menos uma vez, consumidor com inbox/idempotência e reconciliação.
9. Permitir replay auditável sem repetir efeitos já aplicados.

## Envelope de evento (proposto)

```json
{
  "event_id": "evt-0001",
  "source": "pos-demo",
  "tenant_id": "tenant-demo",
  "event_type": "order.created",
  "schema_ref": "pos.order.v1",
  "occurred_at": "2026-11-15T10:00:00Z",
  "correlation_id": "corr-0001",
  "causation_id": null,
  "subject": {"entity_type": "order", "external_id": "ord-001"},
  "payload": {"order_id": "ord-001", "total_minor": 1590, "currency": "BRL"}
}
```

`received_at` deve ser gerado pelo servidor e mantido separado de `occurred_at`. Dinheiro em unidades menores inteiras ou decimal textual, nunca float binário.

## Persistência proposta (PostgreSQL)

- `raw_events`: `tenant_id`, `source`, `event_id`, `payload_json`, `payload_sha256`, `received_at`, `occurred_at`, `schema_ref`; UNIQUE (`tenant_id`, `source`, `event_id`).
- `inbox_receipts`: identidade do evento, estado de ingestão, tentativas e erro classificado.
- `canonical_events`: payload canônico, `contract_version`, `mapping_version`, proveniência e status de revisão.
- `outbox_events`: identificador, tópico, payload, estado de envio, tentativas, próximo retry.
- `consumer_effects`: `consumer_id`, `effect_key` únicos por tenant; protege efeitos contra redelivery.
- `contract_evaluations`: propostas, evidências RAG, scores ML/Jev, parecer do auditor, política aplicada, ator aprovador.
- `entity_aliases`: chaves por tenant/local + sistema + tipo + external_id; correspondência de entidades é distinta da idempotência.

A retenção de RAW, políticas de privacidade, RLS e índices exigem decisões específicas antes da implementação.

## Regras de segurança e decisão

- Sem auto-merge por nome, email, telefone, preço ou timestamp isoladamente.
- Ausente, null, desconhecido, rejeitado e ambíguo são estados distintos.
- A memória Mem0 registra **somente decisões autorizadas**; não substitui dicionário semântico ou contrato oficial.
- O agente auditor emite parecer estruturado; não publica contratos.
- Chaves externas em secret store, nunca no repositório ou nos logs.
- Eventos com mesma identidade e payload diferente são conflitos, não duplicatas silenciosas.

## Resiliência e observabilidade

Implementar retries exponenciais limitados, DLQ, redrive, replay com `replay_run_id`, reconciliação entre RAW/canônico/outbox/consumidor, métricas de backlog, latência, falhas e divergências semânticas. Não prometer exactly-once ponta a ponta.

## Plano incremental

| Fase | Entrega | Gate |
| --- | --- | --- |
| 1 | Schemas de envelope + fixtures de duas fontes | Validação e casos negativos |
| 2 | PostgreSQL RAW/inbox com transação | ACK só após persistência; isolamento de tenant |
| 3 | Normalização + contrato versionado + outbox | Idempotência e concorrência |
| 4 | Worker + consumidor + DLQ/replay | Testes de falhas e reconciliação |
| 5 | RAG + ML + Jev + auditor + Mem0 | Comparação com labels; revisão humana |
| 6 | Adaptador AWS opcional | Orçamento/região/IAM verificados e autorização separada |

## Critérios de aceite antes de expansão

- Duas fontes sintéticas distintas com eventos de negócio reais (ex.: PDV e pagamento).
- Testes de assinatura/autenticação, tenant isolation, payload inválido, ACK após RAW, duplicação simultânea, conflito de hash, falha no relay, retry, DLQ, replay e reconciliação.
- Medição de precisão/recall/F1, falsos merges e taxa de abstenção com dataset rotulado independente.
- Testes executados em banco isolado e resultados registrados; arquivo presente não equivale a teste aprovado.
- AWS não provisionada sem aprovação específica, verificação de créditos, região, quotas e custos residuais.

## Distinção entre origem e extensão

**Derivado da skill:** preservar runtime e fonte de verdade; fluxo RAW → canônico → outbox → consumidor; separação entity resolution/idempotência; ACK durável; pelo-menos-uma-vez; segurança, orçamento e gates de teste.

**Adaptação proposta à NØUS IA:** incorporar Jev/OpenAI RAG/Python ML/Mem0 e auditor na etapa de avaliação de contratos; criar tabelas `contract_evaluations` e política de memória aprovada.
