FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend/ /app/backend/ 
COPY src/database/ /app/database/
COPY src/model/ /app/model/
COPY data/ /data/
COPY src/main.py .
EXPOSE 5000

CMD ["sh", "-c", "python main.py && python backend/KPI.py"]