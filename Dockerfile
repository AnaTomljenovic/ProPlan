FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

COPY pyproject.toml /app/
RUN uv sync --no-install-project --compile-bytecode

COPY . /app
RUN uv sync --compile-bytecode

# 👇 Add this line so /app/.venv/bin is used by default
ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "proplan.main:app", "--host", "0.0.0.0", "--port", "8000"]
