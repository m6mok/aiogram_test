FROM python:3.10

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root

COPY . /app

EXPOSE 8000
