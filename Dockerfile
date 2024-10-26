# Stage 1
FROM python:3.8-slim-buster AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

COPY ./proto /app/proto
RUN python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/prediction.proto

# Stage 2
FROM python:3.8-slim-buster

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY ./proto /app/proto
COPY . .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 5001

CMD ["./entrypoint.sh"]
