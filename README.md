# NØUS IA — Contract Intelligence

MVP inicial do motor de contratos semânticos da NØUS.

## Documentação e continuidade

O [índice de documentação e handoff](docs/README.md) reúne a [especificação detalhada](docs/product-specification.md), o [registro da evolução da conversa de 15/11/2026](docs/session-decisions-2026-11-15.md) e o [relatório de validação](docs/validation-2026-11-15.md). Os documentos distinguem código existente, requisitos, propostas e decisões pendentes, incluindo o nome comercial da ferramenta.

## Estado atual
- API FastAPI
- Avaliação inicial de mapeamento de campos, tipos e unidades
- Validação de payloads com JSON Schema Draft 2020-12
- Parecer REVIEW/REJECT com aprovação humana obrigatória
- Testes de API e Dockerfile

**Ainda não implementado:** Jev, OpenAI RAG, Python ML treinável, Mem0, agente auditor, autenticação multi-tenant e persistência. A similaridade nominal atual é apenas uma heurística, não uma avaliação semântica confiável. Não utilizar em produção.

## Instalar e executar

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse http://localhost:8000/docs

## Testes

```bash
pytest -q
```

## Docker

```bash
docker build -t nous-ia-contract .
docker run --rm -p 8000:8000 nous-ia-contract
```

## Endpoints

- `GET /health`
- `POST /v1/contracts/evaluate`
- `POST /v1/contracts/validate`

### Exemplo

```json
{
  "tenant_id": "demo",
  "source_field": "vl_total",
  "target_field": "total_amount",
  "source_type": "number",
  "target_type": "number",
  "source_unit": "BRL",
  "target_unit": "BRL"
}
```

## Próximas fases

1. PostgreSQL + pgvector, versionamento e isolamento de tenant.
2. RAG semântico e adaptador OpenAI.
3. Modelo Python ML com dados rotulados.
4. Adaptador Jev com API oficialmente verificada.
5. Mem0 e agente auditor com ferramentas somente leitura.
6. Política de aprovação e trilha de auditoria persistente.
