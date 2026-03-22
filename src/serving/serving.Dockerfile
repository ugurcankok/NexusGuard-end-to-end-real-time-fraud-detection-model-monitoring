FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc python3-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/serving/ /app/
COPY src/ /app/src/
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]