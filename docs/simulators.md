# Simuladores offline — iFood e 99Food

**Estado:** implementado como normalizador em memória; **não integrado** a APIs oficiais, webhook, banco ou event bus. Payloads são **sintéticos** e não representam contratos oficiais verificados.

## Endpoint

`POST /v1/simulators/normalize` recebe `tenant_id`, `source` (`ifood` ou `99food`) e `payload`. Responde com evento canônico, `persisted=false`, `published=false`, `requires_human_review=true`.

Exemplo iFood:
```json
{"tenant_id":"demo","source":"ifood","payload":{"eventId":"if-evt-1","orderId":"if-001","code":"PLACED","total":"19.90","currency":"BRL","occurred_at":"2026-11-15T10:00:00Z"}}
```

Exemplo 99Food:
```json
{"tenant_id":"demo","source":"99food","payload":{"event_id":"99-evt-1","order_id":"99-001","status":"CREATED","amount":"19.90","currency":"BRL","occurred_at":"2026-11-15T10:00:00-03:00"}}
```

Os dois convergem para `nous.order-status.v1`, com `total_minor=1990` e instante UTC normalizado. O status de origem permanece como `source_status`: equivalência semântica entre estados ainda exige dicionário aprovado. Valores devem ser string decimal ou inteiro; floats são rejeitados.

## Limitações deliberadas

- Sem assinatura de webhook, OAuth, polling, autenticação de tenant ou autorização de produção.
- Sem gravação RAW, inbox/outbox, idempotência durável, DLQ ou replay.
- Sem chamadas de rede nem dependências de plataformas externas.
- O nome dos campos dos mocks foi escolhido para demonstrar heterogeneidade; **não usar em integração real** sem conferir os contratos e versões oficiais.
- Testes adicionados ao repositório, mas execução depende de ambiente Python configurado.
