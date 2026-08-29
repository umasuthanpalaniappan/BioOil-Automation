FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY ml/models /ml/models
COPY ml/reports/benchmark_results.json /ml/reports/benchmark_results.json
COPY ml/src/physics.py ml/src/feature_engineering.py /ml/src/

ENV MODELS_DIR=/ml/models
ENV ML_SRC_DIR=/ml/src
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
