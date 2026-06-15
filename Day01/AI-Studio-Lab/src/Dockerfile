FROM python:3.11-slim

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# Cloud Run sets the PORT environment variable automatically
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
