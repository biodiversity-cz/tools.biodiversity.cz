FROM python:latest@sha256:4ea77121eab13d9e71f2783d7505f5655b25bb7b2c263e8020aae3b555dbc0b2

RUN apt-get update && apt-get install -y \
    mdbtools \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

RUN useradd --uid 1000  --shell /bin/bash appuser

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

COPY htdocs ./htdocs
COPY run.py .
RUN chown -R appuser:appuser /app

USER appuser
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "run:app"]