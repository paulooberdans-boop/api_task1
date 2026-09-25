# Backlog por Release — Micro-API de Gerenciamento de Tarefas

Este backlog organiza a entrega incremental sem adiar requisitos obrigatórios. Os itens do **Core** materializam o núcleo do produto; Qualidade e Entrega/estabilização ampliam sua confiabilidade e capacidade de publicação.

## Convenções

- **Status inicial:** situação observada no início deste planejamento.
- **Prioridade:** `Must` é obrigatório para o MVP; `Should` é importante para qualidade ou entrega; `Could` é desejável e não bloqueia o núcleo.
- Itens obrigatórios não podem ser reclassificados como `Should` ou `Could` para adiar sua implementação.

## Release 1 — Core

### [x] CORE-001 — Modelos e schemas da tarefa

- **Release:** Core
- **Descrição:** manter o modelo SQLAlchemy `Task` e os schemas Pydantic de entrada, atualização e resposta, com `id`, `title` e `status`.
- **Requisito relacionado:** RF-001 a RF-009; RNF-002; RNF-003.
- **Prioridade:** Must
- **Dependências:** Python, Pydantic e SQLAlchemy.
- **Critério de aceite:** uma tarefa possui os campos mínimos; `status` aceita somente `pending` ou `completed`; payloads inválidos retornam `422`.
- **Status inicial:** Concluído

### [x] CORE-002 — Persistência SQLAlchemy com SQLite

- **Release:** Core
- **Descrição:** configurar engine, sessões, criação de tabelas e repositório usando SQLite em arquivo por padrão.
- **Requisito relacionado:** RF-008; RNF-003; RNF-004; RNF-005; RNF-008.
- **Prioridade:** Must
- **Dependências:** CORE-001.
- **Critério de aceite:** dados são gravados em banco relacional SQLite e permanecem disponíveis após reiniciar a aplicação; `DATABASE_URL` permite configurar a conexão.
- **Status inicial:** Em andamento

### [x] CORE-003 — Criar e listar tarefas

- **Release:** Core
- **Descrição:** implementar `POST /tasks` e `GET /tasks`.
- **Requisito relacionado:** RF-001; RF-002.
- **Prioridade:** Must
- **Dependências:** CORE-001 e CORE-002.
- **Critério de aceite:** criação retorna `201` e uma tarefa pendente; listagem retorna as tarefas persistidas com `200`.
- **Status inicial:** Concluído

### [x] CORE-004 — Consultar, atualizar e excluir tarefas

- **Release:** Core
- **Descrição:** implementar `GET /tasks/{task_id}`, `PATCH /tasks/{task_id}` e `DELETE /tasks/{task_id}`.
- **Requisito relacionado:** RF-003; RF-004; RF-005.
- **Prioridade:** Must
- **Dependências:** CORE-001 e CORE-002.
- **Critério de aceite:** consulta e atualização retornam `200`; exclusão retorna `204`; ID inexistente retorna `404`.
- **Status inicial:** Concluído

### [x] CORE-005 — Conclusão de tarefas

- **Release:** Core
- **Descrição:** permitir marcar uma tarefa como concluída usando a atualização normal do recurso.
- **Requisito relacionado:** RF-006.
- **Prioridade:** Must
- **Dependências:** CORE-004.
- **Critério de aceite:** `PATCH /tasks/{task_id}` com `{"status":"completed"}` persiste e retorna o status `completed`.
- **Status inicial:** Concluído

### [x] CORE-006 — Filtro por status

- **Release:** Core
- **Descrição:** aceitar o parâmetro `status` na listagem de tarefas.
- **Requisito relacionado:** RF-007.
- **Prioridade:** Must
- **Dependências:** CORE-003 e CORE-005.
- **Critério de aceite:** `GET /tasks?status=pending` e `GET /tasks?status=completed` retornam somente tarefas do status solicitado; status inválido retorna `422`.
- **Status inicial:** Concluído

### [x] CORE-007 — Disponibilidade básica da API

- **Release:** Core
- **Descrição:** expor `GET /health` para verificar se a aplicação está disponível.
- **Requisito relacionado:** RF-010.
- **Prioridade:** Must
- **Dependências:** inicialização FastAPI.
- **Critério de aceite:** o endpoint retorna `200` e `{"status":"ok"}` sem depender de IA ou de serviço externo.
- **Status inicial:** Concluído

### [x] CORE-008 — Suíte mínima do núcleo

- **Release:** Core
- **Descrição:** manter testes automatizados dos comportamentos centrais do CRUD, conclusão, filtro, validações, erros e persistência.
- **Requisito relacionado:** RNF-006; critérios de sucesso do escopo.
- **Prioridade:** Must
- **Dependências:** CORE-001 a CORE-007; ambiente Python funcional.
- **Critério de aceite:** `pytest` executa sem internet e cobre criação, listagem, consulta por ID, atualização, exclusão, conclusão, filtro, `404`, `422` e persistência.
- **Status inicial:** Concluído; a suíte executa sem internet no ambiente virtual do projeto.

## Release 2 — Qualidade

### [x] QUAL-001 — Teste de persistência entre reinicializações

- **Release:** Qualidade
- **Descrição:** fortalecer o teste de persistência usando novas sessões ou nova instância da aplicação após a gravação.
- **Requisito relacionado:** RF-008; RNF-006.
- **Prioridade:** Must
- **Dependências:** CORE-002 e CORE-008.
- **Critério de aceite:** uma tarefa criada antes do encerramento continua sendo encontrada depois de abrir nova sessão/cliente usando o mesmo banco SQLite.
- **Status inicial:** Concluído

### [x] QUAL-002 — Isolamento do banco nos testes

- **Release:** Qualidade
- **Descrição:** evitar que o lifespan dos testes crie ou utilize o banco padrão `tasks.db` quando a fixture usa banco temporário.
- **Requisito relacionado:** RNF-006; RNF-008.
- **Prioridade:** Must
- **Dependências:** CORE-002 e CORE-008.
- **Critério de aceite:** os testes usam apenas banco temporário configurado pela fixture e não geram dados no banco padrão do projeto.
- **Status inicial:** Concluído

### [x] QUAL-003 — Testes diretos do repositório

- **Release:** Qualidade
- **Descrição:** adicionar testes isolados para criação, consulta, atualização, filtro e exclusão no `TaskRepository`.
- **Requisito relacionado:** RNF-003; RNF-006; RNF-008.
- **Prioridade:** Should
- **Dependências:** CORE-002 e CORE-008.
- **Critério de aceite:** cada operação de persistência principal é verificada com banco temporário, sem depender de HTTP.
- **Status inicial:** Concluído

### [ ] QUAL-004 — Revisão de documentação e docstrings

- **Release:** Qualidade
- **Descrição:** revisar README, escopo, backlog e docstrings para que descrevam apenas o implementado ou o explicitamente planejado.
- **Requisito relacionado:** RNF-007.
- **Prioridade:** Should
- **Dependências:** CORE-001 a CORE-008.
- **Critério de aceite:** README e documentos de planejamento refletem endpoints, status, configuração, testes e limitações reais.
- **Status inicial:** Em andamento

## Release 3 — Entrega e estabilização

### [ ] REL-001 — Automação de validação

- **Release:** Entrega/estabilização
- **Descrição:** definir uma execução reproduzível de testes e validações para desenvolvimento e release.
- **Requisito relacionado:** RNF-006; RNF-007.
- **Prioridade:** Should
- **Dependências:** QUAL-001 a QUAL-004; ambiente Python configurado.
- **Critério de aceite:** um comando documentado executa a suíte completa e falha quando houver teste ou validação de código quebrada.
- **Status inicial:** A fazer

### [ ] REL-002 — Auditoria de configuração e secrets

- **Release:** Entrega/estabilização
- **Descrição:** revisar variáveis de ambiente, `.gitignore`, arquivos SQLite locais e ausência de credenciais versionadas.
- **Requisito relacionado:** RNF-005; RNF-009.
- **Prioridade:** Must
- **Dependências:** CORE-002 e QUAL-004.
- **Critério de aceite:** não há credenciais hardcoded ou secrets nos arquivos versionados; banco local e `.env` permanecem ignorados quando aplicável.
- **Status inicial:** Em andamento

### [ ] REL-003 — Demonstração do contrato da API

- **Release:** Entrega/estabilização
- **Descrição:** preparar uma sequência curta de demonstração cobrindo criação, listagem, conclusão, filtro, consulta, atualização e exclusão.
- **Requisito relacionado:** RF-001 a RF-010; RNF-007.
- **Prioridade:** Should
- **Dependências:** CORE-008 e QUAL-004.
- **Critério de aceite:** a demonstração pode ser executada localmente com SQLite, sem internet ou integração de IA, e seus resultados correspondem à documentação.
- **Status inicial:** A fazer

### [ ] REL-004 — Checklist de release

- **Release:** Entrega/estabilização
- **Descrição:** consolidar versão, status dos testes, documentação, configuração do banco e pendências conhecidas antes de uma entrega.
- **Requisito relacionado:** RNF-005; RNF-006; RNF-007; RNF-008.
- **Prioridade:** Should
- **Dependências:** REL-001 a REL-003.
- **Critério de aceite:** o checklist registra versão, validações executadas, riscos residuais e instruções de execução sem declarar como implementado algo planejado.
- **Status inicial:** A fazer

## Itens desejáveis futuros

Estes itens não fazem parte do núcleo obrigatório e não podem substituir os itens `Must`:

- adoção de PostgreSQL para um ambiente de produção, caso seja justificada;
- integração opcional com `PriorityAdvisor` ou outro LLM, sempre com fallback local e sem bloquear o CRUD;
- paginação, autenticação, prioridade e outras extensões já registradas como fora de escopo no documento do MVP.
