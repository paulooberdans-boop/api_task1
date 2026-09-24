# Micro-API de Gerenciamento de Tarefas

## Visão geral

API RESTful em Python/FastAPI para gerenciamento de tarefas (To-Do List). O núcleo usa Pydantic para validação, SQLAlchemy para persistência e SQLite em arquivo como banco padrão do MVP.

A API principal funciona sem internet, chave de API ou provedor de IA.

## Objetivo

Oferecer um MVP pequeno, testável e documentado para criar, listar, consultar, atualizar, concluir, filtrar e excluir tarefas, preservando os dados após o reinício da aplicação.

## Funcionalidades implementadas

- criação de tarefas pendentes;
- listagem de tarefas;
- consulta por ID;
- atualização parcial de título e status;
- exclusão de tarefas;
- conclusão por `status: "completed"`;
- filtro por `pending` ou `completed`;
- persistência em SQLite em arquivo;
- validação de payloads com Pydantic;
- respostas `404` para recursos inexistentes e `422` para entradas inválidas;
- health check em `/health`;
- documentação OpenAPI automática em `/docs`;
- `TaskService` separado da camada HTTP;
- `TaskRepository` separado da camada de persistência;
- `PriorityAdvisor` opcional com heurística local e fallback.

Não existe endpoint HTTP de prioridade. O `PriorityAdvisor` é um componente interno opcional e não altera o CRUD.

## Arquitetura

O fluxo principal é:

```text
Cliente HTTP
  -> FastAPI/router (app/routes.py)
  -> schemas Pydantic (app/schemas.py)
  -> TaskService (app/services/task_service.py)
  -> TaskRepository (app/repositories/tasks.py)
  -> SQLAlchemy/session (app/db.py)
  -> SQLite em arquivo
```

- `app/main.py`: cria a aplicação, registra rotas e inicializa as tabelas.
- `app/routes.py`: define endpoints, injeta dependências e converte erros de domínio em HTTP.
- `app/schemas.py`: valida entrada e serializa saída.
- `app/services/task_service.py`: coordena os casos de uso sem depender do protocolo HTTP.
- `app/repositories/tasks.py`: executa operações SQLAlchemy de tarefas.
- `app/models.py`: define `Task` e `TaskStatus`.
- `app/db.py`: configura engine, sessões e criação das tabelas.
- `app/services/priority_advisor.py`: sugere prioridade sem ser requisito do CRUD.

O diagrama detalhado está em [docs/arquitetura.md](docs/arquitetura.md).

## Estrutura relevante

```text
app/
  db.py
  main.py
  models.py
  schemas.py
  repositories/
    __init__.py
    tasks.py
  services/
    __init__.py
    task_service.py
    priority_advisor.py
tests/
  conftest.py
  test_tasks.py
  test_task_routes.py
  test_repository.py
  test_task_service.py
  test_priority_advisor.py
docs/
  escopo-mvp.md
  backlog.md
  arquitetura.md
```

## Requisitos e pré-requisitos

- Python 3.11 ou superior;
- PowerShell no exemplo de comandos abaixo;
- dependências listadas em `requirements.txt`;
- SQLite, incluído no Python, para o banco padrão.

PostgreSQL não é necessário para o MVP. Pode ser adotado futuramente quando houver justificativa e um driver compatível.

## Instalação e ambiente virtual

No PowerShell, na raiz do projeto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

O workspace também está configurado para usar `.venv\Scripts\python.exe`. Se a política do PowerShell impedir a ativação, use diretamente o executável do ambiente:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configuração e variáveis de ambiente

A aplicação usa estas variáveis opcionais:

| Variável | Padrão | Uso |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./tasks.db` | URL SQLAlchemy do banco. |
| `PRIORITY_LLM_API_KEY` | não definida | Habilita o cliente LLM injetado no `PriorityAdvisor`; não é necessária para a API. |
| `PRIORITY_LLM_TIMEOUT_SECONDS` | `2.0` | Limite de espera do cliente externo de prioridade. |

Exemplo para escolher outro arquivo SQLite:

```powershell
$env:DATABASE_URL = "sqlite:///./outro-banco.db"
```

Um modelo está disponível em [.env.example](.env.example). Não coloque chaves reais no código, no `.env.example` ou no Git. Arquivos `.env`, `.db` e `.sqlite3` são ignorados pelo [`.gitignore`](.gitignore).

## Banco e persistência

O padrão é SQLite em arquivo: `sqlite:///./tasks.db`. As tabelas são criadas na inicialização da aplicação e as sessões são fechadas após o uso. Os dados persistem após o encerramento e a nova inicialização quando o mesmo arquivo é utilizado.

Testes usam banco SQLite temporário separado para evitar contaminar dados reais. SQLite em memória não é usado como persistência da aplicação.

## Execução

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`.

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Endpoints principais

| Método | Rota | Sucesso | Descrição |
| --- | --- | --- | --- |
| `POST` | `/tasks` | `201` | Cria tarefa com status inicial `pending`. |
| `GET` | `/tasks` | `200` | Lista tarefas. |
| `GET` | `/tasks/{task_id}` | `200` | Consulta tarefa por ID. |
| `PATCH` | `/tasks/{task_id}` | `200` | Atualiza `title`, `status` ou ambos. |
| `DELETE` | `/tasks/{task_id}` | `204` | Exclui tarefa sem corpo de resposta. |
| `GET` | `/health` | `200` | Retorna `{"status":"ok"}`. |

Recursos inexistentes retornam `404`. Payloads inválidos e status desconhecidos retornam `422`.

### Exemplos

Criar:

```json
{
  "title": "Estudar FastAPI"
}
```

Concluir:

```json
{
  "status": "completed"
}
```

Filtrar:

```text
GET /tasks?status=pending
GET /tasks?status=completed
```

Os únicos status aceitos são `pending` e `completed`. Títulos devem possuir entre 1 e 200 caracteres e não podem ser compostos somente por espaços.

## Testes

A suíte usa pytest, `TestClient` e SQLite temporário. Não há chamadas de rede, API paga ou dependência de IA nos testes.

Executar a suíte completa:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Executar somente as rotas:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_task_routes.py -q
```

Executar somente o service:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_task_service.py -q
```

A cobertura inclui schemas, CRUD do repository, persistência entre sessões, casos de uso do service, rotas HTTP, status/conclusão, filtros, erros `404`/`422`, health check e `PriorityAdvisor`.

## Priorização opcional

O `PriorityAdvisor` existe em [app/services/priority_advisor.py](app/services/priority_advisor.py), mas não é chamado pelas rotas CRUD e não é necessário para criar ou gerenciar tarefas.

### Heurística local

Sem um cliente LLM e sem chave configurada, o advisor classifica o texto localmente:

- termos como `urgente`, `urgent`, `crítico` ou `critical`: `high`;
- termos como `importante`, `prazo`, `deadline` ou `impacto alto`: `medium`;
- demais textos: `low`.

### LLM e fallback

Um cliente externo pode ser injetado no advisor. Sua resposta é validada contra `low`, `medium` e `high`. Se a integração não estiver configurada, falhar, exceder o timeout ou retornar valor inválido, a heurística local é usada. A chave não é registrada em logs e o CRUD não é interrompido pela indisponibilidade da IA.

## Segurança e secrets

- não há credenciais hardcoded;
- chaves devem vir de variáveis de ambiente;
- API keys não devem ser commitadas ou impressas em logs;
- `.env`, bancos locais e artefatos de teste estão no `.gitignore`;
- o `PriorityAdvisor` é opcional e não cria dependência operacional da API externa.

## Limitações atuais

- não há autenticação ou múltiplos usuários;
- não há paginação ou busca textual avançada;
- não há prioridade persistida no modelo `Task`; o advisor apenas sugere um valor;
- não há migrações formais com Alembic;
- PostgreSQL não está configurado como dependência padrão;
- o cliente LLM é uma dependência injetável, sem provider específico incluído;
- a aplicação cria tabelas na inicialização, adequada ao MVP, mas sem estratégia de migração para produção.

## Próximos passos e releases

- **Core:** CRUD, conclusão, filtro, schemas Pydantic, SQLAlchemy + SQLite, testes centrais e health check.
- **Qualidade:** ampliar testes de persistência e repository, isolamento, revisão de documentação e robustez.
- **Entrega/estabilização:** automação, auditoria de configuração/secrets, demonstração e checklist de release.

Autenticação, paginação, migrações, PostgreSQL de produção e integrações LLM específicas permanecem planejados ou fora do escopo do MVP. O backlog detalhado está em [docs/backlog.md](docs/backlog.md), e o escopo em [docs/escopo-mvp.md](docs/escopo-mvp.md).

## GenAI no desenvolvimento

IA generativa foi usada como apoio à criação e revisão de modelos, schemas, endpoints, testes, docstrings e documentação. Essa assistência não é requisito de runtime e a API principal permanece funcional sem internet ou provedor de IA.
