# Validação executada — 15/11/2026

## Alcance e ambiente

Revisão examinada: `5ea7f79960a5ac387b3f92e339f45517d5b082c1`, origem `feat/ifood-99food-simulators`.

Os resultados abaixo foram **executados nesta sessão em Linux**, em venv isolado, sobre o código dessa revisão. Não são uma execução remota no Windows do usuário. O usuário também relatou pytest aprovado e respostas fictícias de iFood/99Food no notebook, mas não forneceu o relatório numérico completo daquele ambiente.

Foram lidos `app/main.py`, `app/simulators.py`, os dois schemas, `requirements.txt`, os dois arquivos de testes, README e documentação existente. Nenhum código de aplicação foi alterado para produzir estes resultados.

Dependências instaladas a partir das faixas de `requirements.txt`:

| Componente | Versão observada |
| --- | --- |
| Python | 3.12.14 |
| FastAPI | 0.163.1 |
| Uvicorn | 0.54.0 |
| Pydantic | 2.14.3 |
| jsonschema | 4.26.0 |
| pytest | 9.2.0 |
| HTTPX | 0.28.1 |
| Starlette | 1.10.0 |

Essas versões registram esta execução; as faixas do projeto não são um lockfile e não comprovam a mesma resolução no Windows.

## 1. Suíte existente

Comando no venv isolado: `python -m pytest -q`.

```text
.........                                                                [100%]
9 passed, 1 warning in 0.43s
```

Cobertura existente:

- Saúde do serviço.
- Avaliação de mapeamento exige revisão e não publica.
- Rejeição de unidades incompatíveis.
- Validação de payload incompatível com JSON Schema.
- Rejeição de avaliação sem tenant.
- Normalização iFood sintética e valor em centavos.
- Normalização 99Food sintética e conversão de horário para UTC.
- Rejeição de valor com mais de duas casas decimais.
- Rejeição de identificador obrigatório ausente.

Aviso observado: `StarletteDeprecationWarning` sobre uso de `httpx` com `starlette.testclient`, sugerindo `httpx2`. Não causou falha. Não foi feita alteração de dependências para suprimir esse aviso; ele depende das versões resolvidas nesta instalação.

Não há testes aprovados de RAG, Jev, ML treinado, geração de contrato, persistência, autenticação, UI, Event Bus ou ERP. Essas capacidades não existem no runtime examinado.

## 2. HTTP real em loopback

Uvicorn foi iniciado nesta sessão em socket próprio de loopback com porta livre. Endereço desta execução: `http://127.0.0.1:41607`. O processo pertencente à demonstração foi encerrado após os testes; essa porta **não é um serviço permanente**.

Foram utilizadas apenas chamadas locais. Não houve requisições para iFood/99Food, deploy ou provisionamento AWS.

Evidência completa com requests, responses, versões, checks e horário UTC: **[normalize-http-evidence.json](examples/normalize-http-evidence.json)**. Log do processo: **[uvicorn-local-demo.txt](examples/uvicorn-local-demo.txt)**.

### 2.1 Resumo dos sete cenários

| Cenário | HTTP esperado/obtido | Resultado |
| --- | --- | --- |
| iFood fictício válido | 200 / 200 | Campos canônicos e flags conferidos |
| 99Food fictício válido | 200 / 200 | Campos canônicos e flags conferidos |
| Pedido sem `orderId` | 422 / 422 | `orderId must be a nonempty string` |
| Valor `1.999` | 422 / 422 | `amount must be nonnegative with at most two decimals` |
| Moeda USD | 422 / 422 | `only BRL is supported by the simulator` |
| Horário sem fuso | 422 / 422 | `occurred_at must include a timezone` |
| Valor float `49.9` | 422 / 422 | `amount must be a decimal string or integer` |

Os cinco erros são **casos negativos esperados**. Nenhum dos sete checks da demonstração falhou.

### 2.2 Entrada e saída iFood fictício

Request reproduzível: [ifood-normalize-request.json](examples/ifood-normalize-request.json).

```json
{
  "tenant_id": "demo-local",
  "source": "ifood",
  "payload": {
    "orderId": "PEDIDO-IFOOD-001",
    "eventId": "EVENTO-IFOOD-001",
    "code": "CONFIRMED",
    "total": "49.90",
    "currency": "BRL",
    "occurred_at": "2026-11-15T12:00:00-03:00"
  }
}
```

Resposta HTTP 200 observada:

```json
{
  "canonical_event": {
    "tenant_id": "demo-local",
    "source": "ifood",
    "event_id": "EVENTO-IFOOD-001",
    "event_type": "order.status_changed",
    "schema_ref": "nous.order-status.v1",
    "occurred_at": "2026-11-15T15:00:00Z",
    "subject": {"entity_type": "order", "external_id": "PEDIDO-IFOOD-001"},
    "payload": {
      "order_id": "PEDIDO-IFOOD-001",
      "source_status": "CONFIRMED",
      "total_minor": 4990,
      "currency": "BRL"
    },
    "simulation": true
  },
  "requires_human_review": true,
  "persisted": false,
  "published": false,
  "warning": "Synthetic simulation only; no official provider integration or durable idempotency."
}
```

### 2.3 Entrada e saída 99Food fictício

Request reproduzível: [99food-normalize-request.json](examples/99food-normalize-request.json).

```json
{
  "tenant_id": "demo-local",
  "source": "99food",
  "payload": {
    "order_id": "PEDIDO-99FOOD-001",
    "event_id": "EVENTO-99FOOD-001",
    "status": "ACCEPTED",
    "amount": "49.90",
    "currency": "BRL",
    "occurred_at": "2026-11-15T15:00:00Z"
  }
}
```

Resposta HTTP 200 observada:

```json
{
  "canonical_event": {
    "tenant_id": "demo-local",
    "source": "99food",
    "event_id": "EVENTO-99FOOD-001",
    "event_type": "order.status_changed",
    "schema_ref": "nous.order-status.v1",
    "occurred_at": "2026-11-15T15:00:00Z",
    "subject": {"entity_type": "order", "external_id": "PEDIDO-99FOOD-001"},
    "payload": {
      "order_id": "PEDIDO-99FOOD-001",
      "source_status": "ACCEPTED",
      "total_minor": 4990,
      "currency": "BRL"
    },
    "simulation": true
  },
  "requires_human_review": true,
  "persisted": false,
  "published": false,
  "warning": "Synthetic simulation only; no official provider integration or durable idempotency."
}
```

As duas estruturas convergem. Fonte, ID e status da fonte continuam distintos. Isso não prova que CONFIRMED e ACCEPTED sejam estados semanticamente equivalentes; o código apenas preserva os valores.

### 2.4 Erro correspondente ao observado no Swagger

Entrada:

```json
{"tenant_id":"demo-local","source":"ifood","payload":{}}
```

Resposta HTTP 422:

```json
{"detail":"orderId must be a nonempty string"}
```

Na documentação Swagger, a lista de respostas possíveis e o exemplo de `200 Successful response` não comprovam que a chamada concreta teve sucesso. Conferir o código efetivo de `Server response`.

## 3. Observações de compatibilidade dos schemas

Foram feitas duas chamadas locais adicionais a `/v1/contracts/validate` para esclarecer o alcance do resultado. Ambas responderam HTTP 200 porque a operação de validação ocorreu, com **`valid: false`** porque o payload não corresponde ao schema fornecido.

1. **Evento do simulador contra `event-envelope.schema.json`:** rejeição por propriedade adicional `simulation`, já que o envelope declara `additionalProperties: false`.
2. **Payload parcial do simulador contra `nous.delivery.order.v1.json`:** rejeição por campos obrigatórios ausentes e por `total_minor` na posição diferente da estrutura completa de `totals`.

São lacunas de integração entre os artefatos atuais, não testes aprovados de um pedido completo. O arquivo de pedido completo já informa que não é aplicado automaticamente ao endpoint. A referência `nous.order-status.v1` não tem arquivo de schema próprio nesta revisão.

Também é importante distinguir `Draft202012Validator.check_schema` de validação de domínio: a igualdade financeira de totais não é verificada apenas pelo schema. O endpoint atual não configura um `FormatChecker`; por isso não se deve afirmar que todo campo `format: date-time` de um schema fornecido será fiscalizado por esse endpoint. O simulador tem sua própria validação explícita de timestamp.

## 4. Reprodução no Windows, com o servidor já aberto

Em outra janela PowerShell, na raiz do checkout:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/v1/simulators/normalize' -Method Post -ContentType 'application/json' -Body (Get-Content -Raw '.\docs\examples\ifood-normalize-request.json') | ConvertTo-Json -Depth 10
```

Depois:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/v1/simulators/normalize' -Method Post -ContentType 'application/json' -Body (Get-Content -Raw '.\docs\examples\99food-normalize-request.json') | ConvertTo-Json -Depth 10
```

Os arquivos estarão disponíveis somente no checkout que contiver esta branch de documentação. Não assumir que já existem no Desktop do usuário. O código do servidor permanece o da branch dos simuladores; não há necessidade de deploy.

## 5. Funcionalidades ainda não implementadas

- LLM interpretando formatos ou gerando contrato/mapeamento.
- Jev, RAG, Python ML treinado, Mem0 e auditor/revisor operacional.
- Editor personalizado, tabela de destino e autosave.
- Registro persistente de contratos e versões efetivamente aplicadas.
- RAW/inbox, canônico/outbox, idempotência durável, retries, DLQ e replay.
- Timeline correlacionada, logs por etapa e métricas reais de latência do produto.
- UI de canvas/nós/configuração ou atualização em tempo real.
- Conversão do pedido completo com itens, totais, pagamento e entrega.
- Autenticação/autorização multi-tenant.
- Integração oficial de iFood/99Food, API do ERP, Event Bus e confirmações de destino.

## 6. Conclusão verificável

A normalização fictícia parcial funciona localmente nos cenários executados, por **regras determinísticas em Python**. A suíte existente passou e os dois formatos sintéticos produziram eventos na mesma estrutura, com conversão monetária e temporal verificadas. Não houve publicação, persistência de negócio ou IA. A documentação descreve a evolução pretendida sem apresentá-la como pronta.
