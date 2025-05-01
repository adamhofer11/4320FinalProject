FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a volume for the database
VOLUME /app/data

# Set environment variable for database path
ENV DATABASE_PATH=/app/data/reservations.db

EXPOSE 5000

CMD ["python", "app.py"] 