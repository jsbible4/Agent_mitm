FROM python:3.9-slim-bullseye

WORKDIR /app
COPY agent_a.py /app/agent_a.py

RUN pip install --no-cache-dir requests
RUN apt-get update && apt-get install -y ca-certificates curl openssl && rm -rf /var/lib/apt/lists/*

CMD ["bash", "-c", "update-ca-certificates 2>/dev/null; python agent_a.py"]
