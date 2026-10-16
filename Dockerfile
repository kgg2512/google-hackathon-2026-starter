FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements.lock.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt -r requirements.txt
COPY . .
CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}
