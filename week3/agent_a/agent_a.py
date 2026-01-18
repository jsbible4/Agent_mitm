import os
import json
import uuid
import requests

AGENT_B_URL = os.getenv("AGENT_B_URL", "http://host.docker.internal:8001/agent")
PROMPT = os.getenv("PROMPT", "read a file")

PROXIES = {
    "http": os.getenv("HTTP_PROXY"),
    "https": os.getenv("HTTPS_PROXY"),
} if os.getenv("HTTP_PROXY") else None

def main():
    trace_id = str(uuid.uuid4())
    payload = {
        "trace_id": trace_id,
        "stage": "prompt",
        "prompt": PROMPT,
    }

    print(f"[Agent A] Using proxy: {PROXIES}")
    #input("Press Enter to send ONE request (turn Intercept ON first)...")

    # Intercept로 오래 잡고 있어도 안 죽게 timeout을 크게
    r = requests.post(
        AGENT_B_URL,
        json=payload,
        timeout=600,      # 10분 (원하면 더)
        proxies=PROXIES
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
