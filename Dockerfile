# Use the official Python base image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=100 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1 \
  POETRY_VERSION=1.5.0

# Install poetry:
# RUN pip install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version "$POETRY_VERSION"
ENV PATH="/root/.local/bin:$PATH"

# Copy the poetry.lock and pyproject.toml files to the working directory
COPY poetry.lock pyproject.toml README.md ./

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install project dependencies
RUN poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-ansi

# Copy the entire project to the working directory
COPY ./1337ft ./1337ft


# Set the environment variable for Flask
ENV FLASK_APP=1337ft/__main__.py \
  FLASK_DEBUG=0 \
  FLASK_RUN_PORT=8008

# Expose the port on which the Flask app will run
EXPOSE 8008

# Run the Flask application
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]
