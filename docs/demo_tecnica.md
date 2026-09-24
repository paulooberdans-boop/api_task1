# Demonstração Técnica em 5 Minutos

Roteiro para stakeholders técnicos. A demonstração usa somente a API local e um arquivo SQLite descartável; não depende de internet, provider LLM ou chave de IA.

## Preparação

Na raiz do projeto, com Python e `.venv` disponíveis:

```powershell
$env:DATABASE_URL = "sqlite:///./demo_tasks.db"
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8003
```

Execute o segundo comando em um terminal próprio. Ao final, interrompa o processo com `Ctrl+C` e remova `demo_tasks.db`.

## Roteiro cronometrado

### 0:00–0:30 — Contexto, objetivo e stack

- O problema: manter tarefas com operações CRUD e acompanhamento de conclusão.
- Objetivo: uma Micro-API To-Do pequena, testável e persistente.
- Stack: Python, FastAPI, Pydantic, SQLAlchemy, SQLite e pytest.
- A API funciona sem internet ou IA em runtime.

Com a aplicação iniciada, o contrato pode ser visto em:

```text
http://127.0.0.1:8003/docs
http://127.0.0.1:8003/openapi.json
```

### 0:30–1:10 — Arquitetura e persistência

Mostre [docs/arquitetura.md](arquitetura.md) e destaque o fluxo:

```text
HTTP -> router -> Pydantic -> TaskService -> TaskRepository
    -> SQLAlchemy/session -> SQLite em arquivo
```

- `app/routes.py` traduz HTTP e injeta o service.
- `app/services/task_service.py` coordena casos de uso.
- `app/repositories/tasks.py` acessa o banco via SQLAlchemy.
- `app/db.py` fornece sessões e configura `DATABASE_URL`.
- `app/models.py` define `Task` e os status `pending`/`completed`.

### 1:10–2:50 — CRUD, conclusão e filtro

Use dados descartáveis. O primeiro comando confirma disponibilidade:

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8003/health -UseBasicParsing
```

Crie uma tarefa:

```powershell
$task = Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8003/tasks `
  -ContentType "application/json" `
  -Body '{"title":"Demo descartavel"}'
$id = $task.id
$task
```

Liste e consulte:

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8003/tasks
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8003/tasks/$id"
```

Atualize o título e conclua pela mesma operação `PATCH`:

```powershell
Invoke-RestMethod -Method Patch `
  -Uri "http://127.0.0.1:8003/tasks/$id" `
  -ContentType "application/json" `
  -Body '{"title":"Demo atualizada"}'

Invoke-RestMethod -Method Patch `
  -Uri "http://127.0.0.1:8003/tasks/$id" `
  -ContentType "application/json" `
  -Body '{"status":"completed"}'
```

Filtre concluídas e pendentes:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8003/tasks?status=completed"
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8003/tasks?status=pending"
```

Exclua a tarefa:

```powershell
Invoke-WebRequest -Method Delete `
  -Uri "http://127.0.0.1:8003/tasks/$id" `
  -UseBasicParsing
```

### 2:50–3:30 — Evidência do banco e persistência

O processo foi iniciado com `DATABASE_URL=sqlite:///./demo_tasks.db`, portanto a persistência é um arquivo SQLite real, não um dicionário em memória. Durante a demonstração, confirme no terminal:

```powershell
Test-Path demo_tasks.db
```

O resultado esperado é `True`. Os testes de repository também comprovam leitura em uma nova sessão SQLite. Ao terminar a demonstração, remova o arquivo descartável:

```powershell
Remove-Item demo_tasks.db -Force
```

### 3:30–4:10 — GenAI, heurística e fallback

A IA generativa foi usada como apoio ao desenvolvimento de código, testes e documentação. Em runtime, `PriorityAdvisor` é opcional e não é chamado pelas rotas CRUD.

A demonstração não usa LLM remoto. A heurística local classifica:

- `urgente`, `urgent`, `crítico` ou `critical` como `high`;
- `importante`, `prazo`, `deadline` ou `impacto alto` como `medium`;
- outros textos como `low`.

Se um cliente LLM for injetado, respostas inválidas, erros e timeout retornam à heurística local. Os cenários são demonstrados sem rede em:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_priority_advisor.py -q
```

Não há endpoint de prioridade e não há dependência de chave de API para o CRUD.

### 4:10–4:45 — Testes e qualidade

Execute a suíte completa:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

A suíte cobre schemas, rotas, service, repository, persistência, conclusão, filtros, erros HTTP e advisor. Os testes usam banco temporário e não fazem chamadas pagas.

### 4:45–5:00 — Limitações e próximo passo

Limitações atuais:

- sem autenticação ou múltiplos usuários;
- sem paginação;
- prioridade não é persistida em `Task`;
- sem migrações formais;
- sem provider LLM específico incluído;
- PostgreSQL permanece alternativa futura, não o banco padrão.

Próximo passo: usar o checklist de release e o backlog em [docs/backlog.md](backlog.md) para priorizar automação, auditoria e estabilização.

## Plano alternativo sem rede ou LLM

Se a rede estiver indisponível, execute somente a API local, os comandos HTTP locais e a suíte pytest. Se não quiser iniciar servidor, use os testes de rotas com `TestClient`:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_task_routes.py -q
```

Esse caminho continua demonstrando o contrato HTTP, o banco temporário e o fallback local sem qualquer serviço externo.

## Limpeza

Depois da demonstração:

```powershell
Remove-Item demo_tasks.db -Force -ErrorAction SilentlyContinue
```

Não adicione `docs/demo_tecnica.md` ao `.gitignore`: o roteiro não contém credenciais nem dados confidenciais e deve ser versionado junto com a documentação do projeto.
