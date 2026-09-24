# Micro-API de Gerenciamento de Tarefas

API REST para criar, consultar, atualizar, concluir, filtrar e excluir tarefas. O MVP usa SQLite para persistir os dados e funciona sem chave ou serviço de IA.

## Objetivo

Entregar uma Micro-API de Gerenciamento de Tarefas pequena, testável e persistente, com um contrato REST adequado ao desenvolvimento do MVP.

## Requisitos obrigatórios atendidos

- criar tarefas;
- listar tarefas;
- consultar uma tarefa por ID;
- atualizar tarefas;
- excluir tarefas;
- marcar tarefas como concluídas por atualização do status;
- filtrar tarefas por status;
- persistir dados em banco SQLite;
- validar payloads e retornar erros HTTP coerentes;
- testar as operações principais, incluindo persistência e recursos inexistentes.

## Funcionalidades

- CRUD de tarefas;
- conclusão por atualização do campo `status`;
- filtro por status (`pending` ou `completed`);
- persistência relacional em SQLite;
- documentação interativa gerada pelo FastAPI em `/docs`.

## Stack

- Python 3.11 ou superior;
- FastAPI e Uvicorn;
- Pydantic;
- SQLAlchemy 2;
- SQLite;
- pytest.

O `PriorityAdvisor` é um componente opcional e separado do CRUD. Ele pode sugerir `low`, `medium` ou `high` por heurística local e aceitar um cliente LLM injetado; sem configuração, usa somente a heurística. A IA generativa também foi usada como apoio ao desenvolvimento, mas não é necessária em runtime.

Quando habilitada, a integração externa usa `PRIORITY_LLM_API_KEY` e `PRIORITY_LLM_TIMEOUT_SECONDS`. Chaves não são armazenadas no código.

## Instalação

No Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se a política do PowerShell impedir a ativação, execute os comandos usando diretamente `.venv\Scripts\python.exe`.

## Configuração e banco

Por padrão, a API usa `sqlite:///./tasks.db`. A tabela `tasks` é criada na inicialização e o arquivo local é ignorado pelo Git. Para alterar o banco, defina `DATABASE_URL`:

```powershell
$env:DATABASE_URL = "sqlite:///./outro-banco.db"
```

Não há credenciais hardcoded. PostgreSQL pode ser usado futuramente informando uma URL compatível e instalando o driver correspondente.

## Execução

```powershell
uvicorn app.main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`. A documentação OpenAPI está em `http://127.0.0.1:8000/docs`.

## Endpoints

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/tasks` | Cria uma tarefa pendente; retorna `201` |
| `GET` | `/tasks` | Lista tarefas; retorna `200` |
| `GET` | `/tasks/{task_id}` | Consulta uma tarefa; retorna `404` se ausente |
| `PATCH` | `/tasks/{task_id}` | Atualiza título/status; retorna `200` |
| `DELETE` | `/tasks/{task_id}` | Exclui uma tarefa; retorna `204` |
| `GET` | `/health` | Verifica a disponibilidade da API e retorna `{"status":"ok"}` |

O health check usa uma resposta estática de disponibilidade e não inclui timestamp; por isso, não há data/hora a formatar em ISO 8601.

Exemplo de criação:

```json
{
  "title": "Estudar FastAPI"
}
```

O status inicial é `pending`. Para concluir:

```json
{
  "status": "completed"
}
```

Filtragem:

```text
GET /tasks?status=pending
GET /tasks?status=completed
```

Títulos devem ter entre 1 e 200 caracteres. Payloads inválidos e status desconhecidos retornam `422`, conforme o FastAPI.

## Testes

```powershell
pytest
```

Os testes cobrem criação, listagem, consulta por ID, atualização, conclusão, exclusão, filtro, recurso inexistente, payload inválido e persistência em banco temporário. Não usam internet nem API paga.

## Estrutura

```text
app/
  db.py       # engine, sessões e criação das tabelas
  models.py   # modelo SQLAlchemy e enum de status
  schemas.py  # entrada e saída Pydantic
  repositories/
    tasks.py   # operações de persistência de tarefas
  services/
    task_service.py # casos de uso e regras de negócio
    priority_advisor.py # sugestão opcional de prioridade
  routes.py   # endpoints HTTP
  main.py     # aplicação FastAPI
 tests/
  conftest.py
  test_tasks.py
  test_repository.py
```

## GenAI

IA generativa foi usada como apoio no desenvolvimento e na revisão dos modelos, schemas, endpoints, testes, docstrings e desta documentação. Não existe integração de IA em runtime; portanto, a API principal não exige chave, fallback externo ou serviço adicional.

## Roadmap

Os itens abaixo são planejados e ainda não estão implementados:

- autenticação e usuários;
- paginação;
- migrações formais com Alembic;
- suporte de produção a PostgreSQL;
- prioridade de tarefas.
