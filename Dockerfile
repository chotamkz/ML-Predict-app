FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./proto /app/proto

RUN python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/prediction.proto

COPY . .

EXPOSE 5001

CMD ["python", "main.py"]