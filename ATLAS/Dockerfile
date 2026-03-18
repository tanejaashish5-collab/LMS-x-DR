FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agents/ agents/
COPY atlas_orchestrator.py .
COPY atlas_backend.py .

# Railway injects PORT env var — default to 8000
ENV PORT=8000

EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Run the orchestrator
CMD ["python", "atlas_orchestrator.py"]
