# Arquitetura — Micro-API de Gerenciamento de Tarefas

## Visão geral

O projeto é uma aplicação Python/FastAPI organizada para separar HTTP, validação, regras de uso e persistência. A estrutura atual possui router/API, schemas Pydantic, `TaskService`, modelos SQLAlchemy, banco/configuração e repository.

A API principal funciona sem internet, chave de API ou provedor de IA.

## Responsabilidades por camada

| Camada | Localização atual | Responsabilidade |
| --- | --- | --- |
| Aplicação | `app/main.py` | Cria a aplicação FastAPI, registra rotas e inicializa tabelas no lifespan. |
| Router/API | `app/routes.py` | Recebe requisições HTTP, usa dependências FastAPI, aplica respostas e erros HTTP. |
| Schemas | `app/schemas.py` | Define validação e serialização Pydantic para criação, atualização e leitura. |
| Service | `app/services/task_service.py` | Coordena CRUD, conclusão, filtro e erros de domínio sem depender de HTTP. |
| Repository | `app/repositories/tasks.py` | Encapsula consultas, inserções, atualizações e exclusões de tarefas. |
| Modelos | `app/models.py` | Define `Task` e `TaskStatus` para o mapeamento SQLAlchemy. |
| Banco/configuração | `app/db.py` | Configura engine e sessões, fornece dependência de banco e cria tabelas. |
| Banco relacional | SQLite por padrão | Persiste os dados em arquivo. PostgreSQL é alternativa futura quando houver justificativa e driver compatível. |
| IA | `app/services/priority_advisor.py` | `PriorityAdvisor` oferece heurística local e integração externa injetável; não é usado pelo CRUD. |

## Dependências permitidas

A direção preferencial das dependências é:

```text
API/router -> service -> repository -> modelos/db -> SQLite ou PostgreSQL
API/router -> schemas Pydantic
service -> schemas/domínio, quando necessário
IA opcional -> service, somente como extensão não bloqueante
```

Regras:

- `routes.py` pode depender de FastAPI, schemas e da composição de dependências.
- A camada de service, quando criada, não deve depender de objetos HTTP, `HTTPException` ou detalhes de FastAPI.
- O service deve chamar repositories para persistência, e não executar SQLAlchemy diretamente.
- O repository pode depender de `Session` do SQLAlchemy e dos modelos persistentes.
- Modelos não devem depender de routers ou schemas HTTP.
- Schemas não devem acessar o banco diretamente.
- A integração de IA, se criada, deve ser opcional, isolada e possuir caminho local determinístico ou fallback que mantenha a API principal funcionando.

### Estado atual versus arquitetura-alvo

O router injeta `TaskService`, que recebe um repository por dependência. O service não conhece FastAPI nem converte erros em HTTP; essa conversão permanece no router.

## Fluxo principal de dados

1. O cliente envia uma requisição HTTP para uma rota de tarefas.
2. FastAPI encontra o endpoint no router e valida o payload ou os parâmetros com Pydantic e tipos declarados.
3. O router injeta `TaskService`, que coordena o caso de uso e consulta o repository.
4. O repository usa SQLAlchemy para consultar ou alterar o modelo `Task`.
5. SQLAlchemy grava ou lê dados no SQLite em arquivo, configurado por `DATABASE_URL`; PostgreSQL é uma alternativa futura.
6. O resultado volta ao router e é serializado pelo schema de resposta `TaskRead`.
7. FastAPI retorna o status HTTP e o JSON ao cliente.

O service mantém o router livre de regras de negócio e o repository livre de decisões HTTP.

## Diagrama

```mermaid
flowchart TD
    C[Cliente HTTP] --> R[Router/API<br/>app/routes.py]
    R --> S[Schemas Pydantic<br/>app/schemas.py]
    R --> TR[TaskRepository<br/>app/repositories/tasks.py]
    TR --> M[Modelos SQLAlchemy<br/>app/models.py]
    TR --> D[Database Session/Engine<br/>app/db.py]
    D --> DB[(SQLite em arquivo<br/>padrão)]
    D -. alternativa futura .-> PG[(PostgreSQL)]

    R --> SV[TaskService<br/>app/services/task_service.py]
    SV --> TR
    AI[PriorityAdvisor<br/>opcional] -. extensão não bloqueante .-> SV

    DB --> D
    D --> TR
    TR --> R
    R --> C
```

As linhas contínuas representam o fluxo implementado atualmente. As linhas tracejadas representam componentes ou caminhos planejados, opcionais ou futuros.

## Limites do MVP

A arquitetura cobre CRUD, conclusão, filtro por status, validação Pydantic e persistência real com SQLAlchemy + SQLite. O `PriorityAdvisor` é opcional e possui heurística local; não há integração obrigatória de LLM, autenticação ou paginação.
