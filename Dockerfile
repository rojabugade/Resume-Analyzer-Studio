FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests

RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["sh", "-c", "uvicorn ai_agent_system.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
