FROM python:3.12-slim

# Force stdout/stderr to be unbuffered to see logs immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies directly to bypass hatchling packaging requirements
RUN pip install --no-cache-dir \
    fastapi>=0.110.0 \
    uvicorn>=0.28.0 \
    "google-adk[gcp]>=2.0.0,<3.0.0" \
    "google-cloud-aiplatform[evaluation,agent-engines]>=1.156.0" \
    jinja2>=3.1.3

# Copy main application code
COPY main.py .

# Run the web service on container startup
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
