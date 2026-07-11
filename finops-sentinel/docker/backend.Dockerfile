FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code and mock data
COPY backend/ ./backend/
COPY mock_data/ ./mock_data/
COPY .env.example ./.env.example

# Copy .env if it exists (will be overridden by docker-compose env)
COPY .env* ./

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
