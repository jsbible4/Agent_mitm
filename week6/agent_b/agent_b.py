from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import requests
import os
import sys
import ssl
import hmac
import hashlib
import json
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# stdout 버퍼링 비활성화
sys.stdout.flush()

TOOL_URL = os.getenv("TOOL_URL", "https://tool-server:8000/tool")
HMAC_SECRET = os.getenv("HMAC_SECRET", "default-secret").encode('utf-8')

# Burp Proxy 설정
PROXIES = {
    "http": os.getenv("HTTP_PROXY"),
    "https": os.getenv("HTTPS_PROXY"),
} if os.getenv("HTTP_PROXY") else None

# TLS 1.2 강제 어댑터 (cipher suite 명시적 설정!)
class TLS12Adapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.check_hostname = False
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.maximum_version = ssl.TLSVersion.TLSv1_2
        # TLS 1.2 호환 ciphers만 명시적으로 설정
        ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        ctx = create_urllib3_context()
        ctx.check_hostname = False
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.maximum_version = ssl.TLSVersion.TLSv1_2
        # TLS 1.2 호환 ciphers만 명시적으로 설정
        ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        proxy_kwargs['ssl_context'] = ctx
        return super().proxy_manager_for(proxy, **proxy_kwargs)

app = FastAPI()

# 시작 시 환경변수 출력
print("=" * 50, flush=True)
print(f"HTTP_PROXY: {os.getenv('HTTP_PROXY')}", flush=True)
print(f"HTTPS_PROXY: {os.getenv('HTTPS_PROXY')}", flush=True)
print(f"PROXIES: {PROXIES}", flush=True)
print("=" * 50, flush=True)

class AgentRequest(BaseModel):
    trace_id: str
    prompt: str
    stage: Optional[str] = None

def decide_tool(prompt: str) -> dict:
    p = prompt.lower().strip()
    if "read" in p and "file" in p:
        return {
            "tool": "read_file",
            "args": {"path": "/data/hello.txt"}
        }
    return {
        "tool": "echo",
        "args": {"message": f"echo from Agent B (prompt='{prompt}')" }
    }

@app.post("/agent")
def agent_endpoint(req: AgentRequest):
    print(f"\n[Agent B] Received request: {req.prompt}", flush=True)
    print(f"[Agent B] Using proxy: {PROXIES}", flush=True)
    
    prompt = req.prompt
    tool_call = decide_tool(prompt)
    print(f"[Agent B] Decided tool: {tool_call}", flush=True)

    # HMAC 서명 생성: tool과 args를 기반으로 무결성 검증
    message_to_sign = json.dumps({
        "tool": tool_call["tool"],
        "args": tool_call["args"],
    }, sort_keys=True)  # 순서 고정으로 재현 가능하게

    signature = hmac.new(
        HMAC_SECRET,
        message_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    print(f"[Agent B] HMAC signature generated: {signature[:16]}...", flush=True)

    tool_payload = {
        "trace_id": req.trace_id,
        "stage": "tool-call",
        "tool": tool_call["tool"],
        "args": tool_call["args"],
        "hmac": signature,  # HMAC 서명 추가
    }

    print(f"[Agent B] Calling tool_server at {TOOL_URL}", flush=True)
    print(f"[Agent B] With proxies: {PROXIES}", flush=True)

    try:
        session = requests.Session()
        session.mount('https://', TLS12Adapter())
        tool_resp = session.post(
            TOOL_URL,
            json=tool_payload,
            timeout=600,
            proxies=PROXIES,
            verify="/usr/local/share/ca-certificates/burp.crt"
        ).json()
        print(f"[Agent B] Tool response received", flush=True)
    except Exception as e:
        print(f"[Agent B] ERROR calling tool_server: {e}", flush=True)
        raise

    response_payload = {
        "trace_id": req.trace_id,
        "stage": "response",
        "prompt_received": {
            "stage": req.stage,
            "prompt": req.prompt
        },
        "tool_call_sent": tool_payload,
        "tool_result_received": tool_resp,
        "final_response": {
            "text": f"Agent B processed prompt and executed tool '{tool_call['tool']}'."
        }
    }
    return response_payload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        ssl_keyfile="/app/server.key",
        ssl_certfile="/app/server.crt",
        ssl_version=ssl.PROTOCOL_TLSv1_2,
    )
