# GACMS - Group Asset Custody Management System
# Use Bookworm for stable WeasyPrint system deps (libgdk-pixbuf etc.)
FROM python:3.11-slim-bookworm

WORKDIR /app

# System deps for WeasyPrint (PDF); libgdk-pixbuf-2.0-0 is the package name on newer Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Don't copy .env in production; use env vars
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run migrations then start server (see docker-compose for override)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
