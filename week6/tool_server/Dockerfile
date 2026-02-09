FROM python:3.9-slim-bullseye

WORKDIR /app
COPY tool_server.py /app/tool_server.py

RUN pip install --no-cache-dir fastapi uvicorn
RUN apt-get update && apt-get install -y ca-certificates openssl && rm -rf /var/lib/apt/lists/*

CMD ["uvicorn", "tool_server:app", "--host", "0.0.0.0", "--port", "8000"]
