# Use python:3.12-slim-bookworm as base image for both stages
FROM python:3.12-slim-bookworm as build-dependencies-stage

# Set environment variables for Poetry
ENV POETRY_VERSION=1.7.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/root/.local/bin:$PATH"

# Update and install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    pipx \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry using pipx
RUN pipx install poetry==${POETRY_VERSION}

# Set working directory for dependencies
WORKDIR /dependencies

# Copy the poetry lock file and pyproject.toml for efficient caching
COPY ./poetry.lock ./pyproject.toml /dependencies/

# Install only production dependencies
RUN poetry install --no-interaction --no-root --without dev

###########################################################

# Define the production stage
FROM python:3.12-slim-bookworm AS production-stage

# Set environment variables for Python runtime
ENV PATH="/application_root/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 

# Create a dedicated working directory
WORKDIR /application_root

# Principle of least privilege: create a new user for running the application
RUN groupadd -g 1001 python_application && \
    useradd -r -u 1001 -g python_application python_application

# Copy the virtual environment from the build stage
COPY --chown=python_application:python_application --from=build-dependencies-stage ./dependencies/.venv /application_root/.venv

# Copy application files
COPY --chown=python_application:python_application /app /application_root/app/

# Ensure the user has the correct permissions
RUN chown -R python_application:python_application /application_root

# Switch to the unprivileged user
USER 1001

# Set the entrypoint for the container
ENTRYPOINT ["python", "-m", "app.main"]