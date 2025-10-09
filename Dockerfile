FROM python:latest@sha256:081e7d0f7e520a653648602d10dcf11a832c8480b98698795d5fe8f456bbba4d

RUN apt-get update && apt-get install -y \
    mdbtools \
    fonts-dejavu \
    && fc-cache -f -v \
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
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000",  "-t", "120", "run:app"]