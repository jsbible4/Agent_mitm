FROM python:3.10-slim

RUN apt-get update && apt-get install -y tcpdump

WORKDIR /app
RUN pip install fastapi uvicorn
COPY tool_server.py .

CMD ["uvicorn", "tool_server:app", "--host", "0.0.0.0", "--port", "8000"]
