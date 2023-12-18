# python-env-setup: Base stage with a slim Python image and environment variables
FROM python:3.12.1-slim-bookworm as python-env-setup

# Environment variables setup
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1 \
    POETRY_VIRTUALENVS_CREATE=false

# requirements-stage: Stage for resolving Python dependencies using Poetry
FROM python-env-setup as requirements-stage
WORKDIR /tmp
RUN pip install poetry=="$POETRY_VERSION"
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final image stage
FROM python-env-setup

WORKDIR /code

# Copy requirements and install
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Principle of least privilege: create a new user for running the application
RUN groupadd -g 1001 python_application && \
    useradd -r -u 1001 -g python_application python_application

# Copy application files and set permissions
COPY --chown=python_application:python_application ./app /code/app

# Switch to the unprivileged user
USER 1001

ENTRYPOINT ["python", "-m", "app.main"]