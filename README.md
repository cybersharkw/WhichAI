# WhichAI

A learning project for comparing AI models and, later, RAG pipelines using your own datasets.
Steps 4 and 5 are implemented: configuration, routers, dependency injection, and persistent datasets/test cases.
`POST /generations` still echoes the model configuration; it does not call a model yet.

## Start locally (PowerShell)

Run all commands from the repository root. SQLite database paths and `.env` paths are relative to this directory.

```powershell
uv sync
Copy-Item .env.example .env
uv run alembic upgrade head
uv run fastapi dev
```

Copy the example only once; keep your own `.env` when it already exists.
Open <http://127.0.0.1:8000/docs> to try the API.
The migration creates `which.db` locally. Data remains available after restarting the server.
The app does not automatically create or migrate tables: run `alembic upgrade head` after adding migrations.

Alternatively, `uv run whichai` starts Uvicorn using `WHICH_HOST` and `WHICH_PORT`.
For FastAPI's development command, pass host/port flags explicitly when changing them:

```powershell
uv run fastapi dev --host 127.0.0.1 --port 8100
```

## Project structure and request flow

```text
src/backend/
  main.py             # Creates the application and includes routers
  config.py           # Validated environment settings
  cli.py              # The `whichai` terminal command
  api/                # HTTP routes and Depends dependencies
  schemas/            # Pydantic request/response models
  services/           # Dataset/test-case application logic
  db/                 # SQLAlchemy tables, engine and sessions
  adapters/           # Reserved for future model integrations
  Model/              # Existing model schemas and compatibility imports
migrations/           # Versioned Alembic schema changes
tests/                # Isolated SQLite tests using real migrations
```

For a dataset request: **router → injected DatasetService → SQLAlchemy Session → database**.
Pydantic checks request data and serializes responses; it does not save records.
The service owns commits. Each request receives its own session, which is closed after the request.
Database endpoints use synchronous `def` functions so FastAPI runs the blocking work outside its event loop.
The health endpoint is a liveness check and does not test database readiness.

The old `Model.TestCaseCreate` and `Model.TestCaseRead` imports remain available.
They now expose the schemas in `schemas/test_cases.py`. A test case contains an input, reference answer,
and evaluation criteria. IDs and creation timestamps are assigned by the backend; run dates and model lists
belong to the later experiment layer.

## Configuration

`Settings` reads `.env` and environment variables with the `WHICH_` prefix.
Environment variables take precedence over `.env`; explicit constructor values take precedence over both.
Restart the server after changing settings.

| Variable | Default | Meaning |
| --- | --- | --- |
| `WHICH_APP_NAME` | `WhichAI` | API title |
| `WHICH_DEBUG` | `false` | FastAPI debug mode |
| `WHICH_DATABASE_URL` | `sqlite:///./which.db` | SQLAlchemy connection URL |
| `WHICH_HOST` | `127.0.0.1` | Bind host for `uv run whichai` |
| `WHICH_PORT` | `8000` | Bind port for `uv run whichai` |
| `WHICH_REQUEST_TIMEOUT_SECONDS` | `30` | Reserved for future model calls; not enforced yet |
| `WHICH_MODEL_API_KEY` | unset | Optional secret for a future adapter; unused for now |

`.env` files and local SQLite database files are ignored by Git. `.env.example` contains no real credentials.
Use `app.dependency_overrides[get_dataset_service]` to replace a service in tests without editing routes.

## API

| Method | Path | Result |
| --- | --- | --- |
| GET | `/` | Existing hello-world response |
| GET | `/health` | Liveness status |
| POST | `/generations` | Existing model-configuration echo |
| POST | `/datasets` | Create a dataset (201) |
| GET | `/datasets` | List datasets |
| GET | `/datasets/{id}` | Read one dataset |
| POST | `/datasets/{id}/cases` | Create a test case (201) |
| GET | `/datasets/{id}/cases` | List that dataset's cases |

List endpoints accept `offset` (default 0) and `limit` (default 50, maximum 100).
Unknown datasets return 404. Invalid input returns 422.
Updates and deletion are not implemented in this step.

Create a dataset in Swagger or with PowerShell:

```powershell
$dataset = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/datasets -ContentType 'application/json' -Body '{"name":"Support classification","description":"Sample tasks"}'

$caseBody = @{
    name = 'Refund request'
    input = 'Please refund my order.'
    reference_answer = 'billing'
    evaluation_criteria = @('Correct category', 'No invented facts')
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/datasets/$($dataset.id)/cases" -ContentType 'application/json' -Body $caseBody
Invoke-RestMethod -Uri "http://127.0.0.1:8000/datasets/$($dataset.id)/cases"
```

## Change the database schema

1. Edit the SQLAlchemy tables in `src/backend/db/models.py`.
2. Generate a candidate migration:

   ```powershell
   uv run alembic revision --autogenerate -m "describe the schema change"
   ```

3. Read and review the generated migration, including its downgrade behavior.
4. Back up important data, then apply the migration with `uv run alembic upgrade head`.
5. Run `uv run alembic check` to check for differences between the tables and ORM models.

Initial migration `0001` creates `datasets`, `test_cases`, and an index on `test_cases.dataset_id`.
SQLite foreign-key enforcement is enabled for every connection.

To switch to PostgreSQL later, install `uv add "psycopg[binary]"`, create a database, and set
`WHICH_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/which` in your local configuration.
Then apply the migrations to that database. This creates its schema; it does not copy SQLite records.
Only SQLite has been exercised by this project's current tests.

## Verify

```powershell
uv run pytest -q
```

Tests use temporary database files and apply real Alembic migrations. They check validation,
dataset isolation, persistence across application restarts, dependency overrides, and migration round trips.
They do not contact AI providers or write records into your development database.

## Documentation to study

- [Pydantic Settings: environment variables and dotenv](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI: bigger applications and APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI: dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI: response models](https://fastapi.tiangolo.com/tutorial/response-model/)
- [SQLAlchemy: ORM quick start](https://docs.sqlalchemy.org/en/latest/orm/quickstart.html)
- [SQLAlchemy: session basics](https://docs.sqlalchemy.org/en/latest/orm/session_basics.html)
- [Alembic: tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Alembic: autogenerated migrations must be reviewed](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [FastAPI: testing and dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

These are local-development building blocks. User authentication, model execution, evaluation, background
jobs, and RAG remain later steps of the plan.
