FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Note: Playwright browsers are not installed in this image by default.
# For local dev you may run `playwright install` or extend this Dockerfile.

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
