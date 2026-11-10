# CorpAssist

CorpAssist is a modern, fully asynchronous REST API backend built with FastAPI that provides corporate workflow tooling — user authentication, support tickets, leave management and an AI assistant layer.

## Features

- **Authentication** — JWT access/refresh tokens, Argon2 password hashing, refresh-token rotation
- **Support tickets** — create, retrieve and filter tickets by priority and status
- **Leave management** — full CRUD on leave requests with type/status filtering and pagination
- **AI assistant** — LangGraph agent workflow with a Groq-hosted LLM
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
└── ai/              # AI agent (LLM client, LangGraph state and workflow)
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

## API

### Authentication (public)

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Create an account |
| `POST` | `/auth/login` | Authenticate and receive access + refresh tokens |
| `POST` | `/auth/refresh-token` | Exchange a refresh token for a new access token |

All other endpoints are protected and require the header `Authorization: Bearer <access_token>`.

### Tickets

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/ticket/ticket` | Create a ticket (`title`, `description`, optional `status`, `priority`) |
| `GET` | `/ticket/ticket/{ticket_id}` | Retrieve a ticket |
| `GET` | `/ticket/ticket` | List tickets (filters: `priority`, `status`; pagination: `page_number`, `page_size`) |

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

## Migrations

```bash
# Apply all migrations
uv run alembic upgrade head

# Generate a new migration from model changes
uv run alembic revision --autogenerate -m "describe the change"
```

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).
