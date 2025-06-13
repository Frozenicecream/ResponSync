FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary directories
COPY src/backend/ /app/backend/
COPY src/database/ /app/database/
COPY src/model/ /app/model/
COPY data/ /data/
COPY src/main.py /app/

EXPOSE 5000

# Change to the correct directory and run the application
WORKDIR /app
CMD ["python", "main.py"]