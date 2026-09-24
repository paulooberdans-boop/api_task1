# Escopo do MVP — Micro-API de Gerenciamento de Tarefas

## 1. Problema

Pessoas precisam registrar e acompanhar tarefas de forma simples, mas o MVP ainda não oferece uma API centralizada para criar, consultar, atualizar, concluir, filtrar e excluir esses registros com persistência real.

## 2. Objetivo

Entregar uma Micro-API RESTful de Gerenciamento de Tarefas (To-Do List), pequena, testável e documentada, capaz de manter tarefas após o reinício da aplicação.

O núcleo do MVP não depende de internet, chave de API ou provedor de IA.

## 3. Usuários e atores

- **Cliente da API:** aplicação ou pessoa consumidora dos endpoints HTTP.
- **Desenvolvedor:** implementa, testa e mantém a API.
- **Banco de dados:** SQLite no MVP, com PostgreSQL como alternativa quando houver justificativa operacional.
- **IA generativa:** apoio opcional ao desenvolvimento; não é ator necessário em runtime.

## 4. Requisitos funcionais

Os itens abaixo são obrigatórios para o MVP. Não são desejáveis nem estão fora de escopo.

| ID | Requisito | Critério verificável |
| --- | --- | --- |
| RF-001 | Criar tarefas | `POST /tasks` cria uma tarefa e retorna HTTP `201`. |
| RF-002 | Listar tarefas | `GET /tasks` retorna as tarefas persistidas. |
| RF-003 | Consultar por ID | `GET /tasks/{task_id}` retorna a tarefa ou HTTP `404` quando inexistente. |
| RF-004 | Atualizar tarefas | `PATCH /tasks/{task_id}` altera os campos permitidos e retorna a tarefa atualizada. |
| RF-005 | Excluir tarefas | `DELETE /tasks/{task_id}` remove a tarefa e retorna HTTP `204`; recurso inexistente retorna `404`. |
| RF-006 | Marcar como concluída | A atualização aceita `status: "completed"`; uma nova tarefa inicia como `"pending"`. |
| RF-007 | Filtrar por status | `GET /tasks?status=pending` e `GET /tasks?status=completed` retornam somente o status solicitado. |
| RF-008 | Persistir tarefas | Dados gravados permanecem disponíveis após o encerramento e reinício da aplicação. |
| RF-009 | Validar entradas | Payloads inválidos ou status desconhecidos são rejeitados com HTTP `422`. |
| RF-010 | Disponibilidade básica | `GET /health` retorna HTTP `200` e informa `{"status":"ok"}`. |

### Modelo mínimo

Cada tarefa deve possuir, no mínimo:

- `id`;
- `title`;
- `status`, com os valores `pending` ou `completed`.

Os campos `created_at` e `updated_at` fazem parte da representação atual e podem permanecer no MVP por contribuírem para rastreabilidade básica.

## 5. Requisitos não funcionais

| ID | Requisito | Critério verificável |
| --- | --- | --- |
| RNF-001 | Stack Python | A aplicação deve usar Python 3.11 ou superior e FastAPI. |
| RNF-002 | Validação | Schemas de entrada e saída devem usar Pydantic. |
| RNF-003 | Persistência relacional | O acesso ao banco deve usar SQLAlchemy; armazenamento exclusivamente em memória não é permitido como solução final. |
| RNF-004 | Banco padrão | O MVP deve usar SQLite em arquivo. PostgreSQL pode ser adotado quando houver justificativa e configuração compatível. |
| RNF-005 | Configuração | A URL do banco deve ser configurável por `DATABASE_URL`; credenciais não podem ser hardcoded. |
| RNF-006 | Testabilidade | Testes devem poder usar banco SQLite isolado e não depender de internet, IA ou API paga. |
| RNF-007 | Documentação | O projeto deve manter README detalhado, este documento de escopo e docstrings úteis nas principais funções/classes. |
| RNF-008 | Manutenibilidade | HTTP, validação e persistência devem permanecer separados em rotas, schemas, modelos e repositório. |
| RNF-009 | IA opcional | A API principal deve funcionar sem integração LLM, chave de API ou provedor externo. |

## 6. Premissas

- O uso inicial é pequeno e compatível com SQLite em arquivo.
- O cliente consumirá uma API HTTP local ou acessível pela rede autorizada.
- O título é suficiente para o modelo mínimo de tarefa; descrição, prioridade e usuários não são necessários para validar o MVP.
- Os status válidos do MVP são somente `pending` e `completed`.
- A conclusão será realizada pela atualização normal da tarefa, sem endpoint específico adicional.
- Testes locais terão acesso às dependências Python declaradas no projeto.

## 7. Restrições

- O MVP deve permanecer pequeno e sem abstrações sem uso.
- SQLite é o banco padrão; PostgreSQL não deve ser introduzido sem justificativa.
- Não haverá dependência obrigatória de internet ou serviço de IA.
- Não serão adicionadas credenciais ao código ou ao repositório.
- Não serão introduzidas duas tecnologias para resolver a mesma responsabilidade.
- Migrações formais não são obrigatórias nesta fase; a criação inicial de tabelas pode ser simples.

## 8. Dependências

### Obrigatórias

- Python 3.11+;
- FastAPI;
- Pydantic;
- SQLAlchemy;
- SQLite;
- pytest;
- cliente de testes HTTP compatível com a suíte FastAPI.

### Opcionais

- PostgreSQL e seu driver, caso a implantação deixe de usar SQLite;
- IA generativa como apoio à revisão, implementação, testes, docstrings e documentação.

Uma integração de runtime, como `PriorityAdvisor` ou outro LLM, somente poderá ser adicionada como funcionalidade complementar. Ela não pode bloquear nem substituir RF-001 a RF-010.

## 9. Critérios de sucesso

O MVP será considerado bem-sucedido quando:

1. todos os requisitos RF-001 a RF-010 estiverem implementados;
2. a API iniciar com SQLite sem configuração externa obrigatória;
3. os endpoints CRUD, conclusão e filtro retornarem os códigos e dados documentados;
4. uma tarefa sobreviver ao reinício da aplicação;
5. os testes cobrirem criação, listagem, consulta por ID, atualização, exclusão, conclusão, filtro, `404`, `422` e persistência;
6. o README e este escopo descreverem somente funcionalidades implementadas ou explicitamente planejadas;
7. a suíte de testes executar sem internet, chave de IA ou provedor pago.

## 10. Fora de escopo do MVP

Os itens a seguir são deliberadamente excluídos da entrega atual e não substituem nenhum requisito obrigatório:

- autenticação, autorização e múltiplos usuários;
- frontend ou aplicativo móvel;
- colaboração em tempo real;
- notificações, lembretes e recorrência;
- anexos e comentários;
- paginação e busca textual avançada;
- prioridade e categorização de tarefas;
- migrações formais com Alembic;
- observabilidade avançada e métricas de produção;
- integração obrigatória com LLM, `PriorityAdvisor` ou outro provedor de IA.

PostgreSQL para produção, paginação, prioridade e autenticação são temas possíveis de versões futuras. A decisão de adoção de PostgreSQL permanece **A DEFINIR** conforme o ambiente de implantação; isso não altera o uso obrigatório de SQLite no MVP.
