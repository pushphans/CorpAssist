# CorpAssist

CorpAssist is a modern, fully asynchronous REST API backend built with FastAPI that provides corporate workflow tooling — user authentication, support tickets, leave management and an AI assistant layer.

## Features

- **Authentication** — JWT access/refresh tokens, Argon2 password hashing, refresh-token rotation
- **Support tickets** — create, retrieve, update, delete and filter tickets by priority and status
- **Leave management** — full CRUD on leave requests with type/status filtering and pagination
- **AI assistant** — authenticated, stateless chat with a LangGraph supervisor routing to ticket and leave workflows, powered by Groq
- **Async throughout** — SQLAlchemy 2.x (async) on PostgreSQL, Alembic migrations

## Tech Stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.14 |
| Web framework | FastAPI |
| Database / ORM | PostgreSQL, SQLAlchemy 2.x (async, asyncpg) |
| Migrations | Alembic |
| Validation / settings | Pydantic v2, pydantic-settings |
| Authentication | PyJWT, pwdlib (Argon2) |
| AI | LangChain, LangGraph, Groq |
| Packaging | uv |

## Project Structure

```
src/corpassist/
├── main.py          # FastAPI application entrypoint, router wiring
├── core/            # Shared infrastructure
│   ├── config.py    # Settings loaded from .env
│   ├── db.py        # Async engine, session factory, declarative Base
│   ├── enums.py     # Domain enums (leave/ticket types and statuses)
│   └── errors.py    # Domain exceptions
├── auth/            # Authentication module
│   ├── model/       # users, refresh_token models
│   ├── router/      # /auth endpoints
│   ├── schema/      # Pydantic request/response schemas
│   ├── services/    # register / login / refresh-token business logic
│   └── utils/       # JWT helpers, password hashing, current-user dependency
├── tickets/         # Support ticket module (model / router / schema / service)
├── leaves/          # Leave management module (model / router / schema / service)
└── ai/              # Supervisor-based AI assistant
    ├── core/        # LLM clients, graph state and authenticated runtime context
    ├── router/      # POST /ai/chat
    ├── schema/      # Chat request/response schemas
    ├── service/     # Stateless supervisor invocation
    ├── supervisor_workflow/ # Routing between domain workflows
    ├── ticket_workflow/     # Ticket agent and service-backed tools
    └── leave_workflow/      # Leave agent and service-backed tools
```

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (manages the Python 3.14 interpreter and dependencies)
- PostgreSQL

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure the environment

Create a `.env` file in the project root (see [Environment Variables](#environment-variables)).

### 3. Create the database and run migrations

```bash
psql -c "CREATE DATABASE corp_assist;"
uv run alembic upgrade head
```

### 4. Run the API

```bash
uv run uvicorn corpassist.main:app --reload
```

The interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.

## Environment Variables

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | Async PostgreSQL DSN, e.g. `postgresql+asyncpg://postgres:postgres@localhost:5432/corp_assist` |
| `ACCESS_TOKEN_EXPIRY_IN_MINUTES` | Lifetime of a JWT access token |
| `REFRESH_TOKEN_EXPIRY_IN_DAYS` | Lifetime of a refresh token |
| `JWT_SECRET_KEY` | Secret used to sign JWT access tokens |
| `ALGORITHM` | JWT signing algorithm (e.g. `HS256`) |
| `GROQ_API_KEY` | Groq API key used by the AI module |

All variables above are required by the settings model. AI model clients are initialized
when the application imports the AI router. Model selections are configured in
`src/corpassist/ai/core/llm.py`; use models available to your Groq account that support
tool calling and the supervisor's structured output.

## API

### Authentication (public)

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Create an account |
| `POST` | `/auth/login` | Authenticate and receive access + refresh tokens |
| `POST` | `/auth/refresh-token` | Exchange a refresh token for a new access token |

Ticket, leave and AI endpoints are protected and require the header
`Authorization: Bearer <access_token>`. The health endpoint `GET /` is public.

### Tickets

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/ticket/ticket` | Create a ticket (`title`, `description`, optional `status`, `priority`) |
| `GET` | `/ticket/ticket/{ticket_id}` | Retrieve a ticket |
| `GET` | `/ticket/ticket` | List tickets (filters: `priority`, `status`; pagination: `page_number`, `page_size`) |
| `PUT` | `/ticket/ticket/{ticket_id}` | Update a ticket (`title`, `description`, `status`, `priority` are required) |
| `DELETE` | `/ticket/ticket/{ticket_id}` | Delete a ticket |

The repeated `/ticket/ticket` path reflects the current router prefix and route paths.
Ticket priorities are `LOW`, `MEDIUM`, `HIGH`; statuses are `OPEN`, `IN_PROGRESS`, `RESOLVED`.

### Leaves

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/leave` | Request leave (`leave_type`, `start_date`, `end_date`, `days_count`, `reason`) — created as `PENDING` |
| `GET` | `/leave/{leave_id}` | Retrieve a leave request |
| `GET` | `/leave` | List leave requests (filters: `leave_type`, `status`; pagination: `page_number`, `page_size`) |
| `PUT` | `/leave/{leave_id}` | Update a leave request (partial updates supported) |
| `DELETE` | `/leave/{leave_id}` | Delete a leave request |

Enums:

- `leave_type` — `CASUAL`, `SICK`, `EARNED`
- `status` — `PENDING`, `APPROVED`, `REJECTED`

### AI Chat

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/ai/chat` | Send one message to the ticket/leave assistant |

Send an access token in the authorization header and a JSON body:

```json
{
  "message": "List my open support tickets."
}
```

The response contains the last workflow message's content:

```json
{
  "message": "Assistant response based on the tool results."
}
```

The request accepts a non-empty string; surrounding whitespace is removed.
Missing or invalid authentication returns `401`, invalid request data returns `422`,
and workflow failures return a generic `500` response without internal error details.
Do not send `user_id`: the router derives it from the authenticated user.

## AI Workflow

```mermaid
flowchart TD
    Request[POST /ai/chat] --> Auth[Authenticate user]
    Auth --> Service[run_ai_workflow]
    Service --> Supervisor[Supervisor]
    Supervisor -->|ticket_agent| Ticket[Ticket workflow]
    Supervisor -->|leave_agent| Leave[Leave workflow]
    Ticket --> TicketTools[Ticket tools]
    TicketTools --> Ticket
    Leave --> LeaveTools[Leave tools]
    LeaveTools --> Leave
    Ticket -->|Workflow complete| Supervisor
    Leave -->|Workflow complete| Supervisor
    Supervisor -->|FINISH| Response[Return last message content]
```

- The supervisor chooses `ticket_agent`, `leave_agent`, or `FINISH` using structured LLM output and `Command(goto=...)`.
- Ticket and leave nodes are compiled child workflows, each containing an LLM agent and a tool execution loop.
- Ticket tools support creation, retrieval and listing. Ticket update/delete operations are currently REST-only.
- Leave tools support creation, retrieval, listing, partial updates and deletion. New leave requests start as `PENDING`.
- Shared `messages` state uses the `add_messages` reducer. Agents receive the accumulated conversation, including tool results, within the current invocation.
- The service supplies `AiContext(user_id=...)`. Tools read trusted identity through `ToolRuntime` and call existing domain services using a separate async DB session per invocation.

### Current Limits

- Chat is stateless across HTTP requests: no history parameter, checkpointer or `thread_id` is configured. Include all necessary information in each request; a subsequent reply does not automatically retain an earlier clarification question.
- A mixed ticket/leave request can route to both workers sequentially, but there is no final summary node. The API returns only the last message, not a combined transcript or summary.
- The supervisor does not generate a user-facing answer itself. If it finishes before a worker replies, the last message can still be the original user message.
- Tool operations are not one atomic transaction across the entire AI request. A completed write is not automatically undone if a later step fails.
- The leave prompt prohibits approval/rejection, but prompts are not authorization controls. The existing update service/tool exposes status updates; manager-only approval requires a service-level permission check before production use.

## Migrations

```bash
# Apply all migrations
uv run alembic upgrade head

# Generate a new migration from model changes
uv run alembic revision --autogenerate -m "describe the change"
```

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).
