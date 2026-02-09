import os
import json
import uuid
import requests
import ssl
import time
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

AGENT_B_URL = os.getenv("AGENT_B_URL", "https://agent-b:8001/agent")
PROMPT = os.getenv("PROMPT", "read a file")

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

def main():
    trace_id = str(uuid.uuid4())
    payload = {
        "trace_id": trace_id,
        "prompt": PROMPT,
    }

    print(f"[Agent A] Target URL: {AGENT_B_URL}")
    print(f"[Agent A] Using proxy: {PROXIES}")

    # Docker 환경에서만 대기 (로컬 실행 시 스킵)
    if "agent-b" in AGENT_B_URL and "localhost" not in AGENT_B_URL:
        print("[Agent A] Waiting 3 seconds for agent-b to be ready...")
        time.sleep(3)

    session = requests.Session()
    session.mount('https://', TLS12Adapter())
    r = session.post(
        AGENT_B_URL,
        json=payload,
        timeout=600,
        proxies=PROXIES,
        verify="/usr/local/share/ca-certificates/burp.crt"
    )

    # 실패해도 이유를 눈으로 보기 좋게
    print("status:", r.status_code, "ctype:", r.headers.get("Content-Type"))
    print("body(head):", r.text[:300])

    r.raise_for_status()

    resp = r.json()
    print("\n===== Agent A received (from Agent B) =====")
    print(json.dumps(resp, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
