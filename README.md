# Django Book Assignment

## Repository layout

- `book_lib/` — Django project and app code
- `tests/` — top-level test helpers
- `book_lib/tests/` — app-specific tests
- `pyproject.toml` — project metadata
- `.github/workflows/ci.yml` — CI for running tests and publishing results

## Requirements

- Python 3.11+
- `uv` (UV) globally installed

## Setup (local)

1. Create/activate a virtual environment and install dependencies:

```bash
uv sync                    # if you use uv; alternatively: pip install -r requirements.txt
```

2. Spin up the docker-compose
```bash
docker-compose up -d
```

3. Run migrations (if using DB-backed tests) or rely on in-memory tests configured for CI:

```bash
uv run python manage.py migrate
```

4. [Optional] Load the seed data (has admins, users and permissions given at superuser and database level)
```bash
docker exec -t library-postgres-1 pg_dump \
-U postgres \
--data-only \
--column-inserts \
library_db > db_dump.sql
```

## Running tests

- Run tests via pytest directly (fast, explicit):

```bash
uv run pytest -n auto tests --junitxml=results/junit.xml --cov=books --cov-report=xml:results/coverage.xml --cov-report=html:results/coverage_html
```


## Continuous Integration

CI is configured in `.github/workflows/ci.yml`. The workflow:

- Sets up Python
- Installs `uv` (via a GitHub action or pipx in different variants)
- Runs `uv sync` to install dependencies
- Executes tests and writes artifacts to `results/`
- Uploads JUnit and coverage artifacts and reports test results

Common CI troubleshooting:

- If artifact uploads fail, ensure the test step creates `results/junit.xml` and `results/coverage.xml`. The workflow is tolerant of missing files if the upload step sets `if-no-files-found: ignore` or the test step writes placeholder files.
- Ensure `uv` is available in the PATH when running CI steps.

## Development notes

- If you see import errors like `No module named 'book_lib'` or `No module named 'config'`, confirm running tests from `book_lib`
- `db_dump.sql` includes the permission sets given through super user. The idea is to make things simple for you to review. You can directly load the dump data to postgres running inside docker container.

    - Users:

            Superuser:
                name: admin
                pass: admin

            Admin:
                name: AdminAnkit
                pass: demo@123

            User:
                name: UserAnkit
                pass: demo@123

        Otherwise, you would have to create users and groups by yourself & assign permissions.

- For dropdown, I have hardcoded the data as of now.
- For each category, I am scraping all the webpages.
- Tests run on each pull-request and generates a report.
