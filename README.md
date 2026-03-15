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
docker-compuse up -d
```

3. Run migrations (if using DB-backed tests) or rely on in-memory tests configured for CI:

```bash
uv run python manage.py migrate
```

4. Load the seed data (has admins, users and permissions given at superuser and database level)

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

- Tests are configured via `pytest.ini`. Django settings for tests are in `book_lib/tests/test_settings.py` (importing `book_lib.config.settings`).
- If you see import errors like `No module named 'book_lib'` or `No module named 'config'`, confirm the Python path includes the project root (CI uses `PYTHONPATH=.`, local runs may require adjusting `sys.path` or using the recommended `uv` tasks).
