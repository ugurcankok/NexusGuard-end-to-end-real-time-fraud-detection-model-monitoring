FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /app/src/
COPY data/ /app/data/
ENV PYTHONPATH=/app
CMD ["python", "src/training/train.py"]