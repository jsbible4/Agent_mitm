from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os
import hmac
import hashlib
import json

app = FastAPI()

# HMAC Secret 로드
HMAC_SECRET = os.getenv("HMAC_SECRET", "default-secret").encode('utf-8')

class ToolRequest(BaseModel):
    trace_id: str
    stage: Optional[str] = None
    tool: str
    args: dict
    hmac: str  # HMAC 서명 필드 추가

@app.post("/tool")
def run_tool(req: ToolRequest):
    # HMAC 무결성 검증
    message_to_verify = json.dumps({
        "tool": req.tool,
        "args": req.args,
    }, sort_keys=True)

    expected_signature = hmac.new(
        HMAC_SECRET,
        message_to_verify.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 타이밍 공격 방지를 위한 안전한 비교
    if not hmac.compare_digest(req.hmac, expected_signature):
        print(f"[Tool Server] HMAC verification FAILED!", flush=True)
        print(f"[Tool Server] Expected: {expected_signature[:16]}...", flush=True)
        print(f"[Tool Server] Received: {req.hmac[:16]}...", flush=True)
        return {
            "trace_id": req.trace_id,
            "stage": "tool-response",
            "status": "error",
            "tool": req.tool,
            "args": req.args,
            "error": "HMAC verification failed - message integrity compromised"
        }

    print(f"[Tool Server] HMAC verification SUCCESS", flush=True)

    # tool 서버는 '판단' 안 함: 요청대로만 실행
    if req.tool == "read_file":
        path = req.args.get("path", "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "trace_id": req.trace_id,
                "stage": "tool-response",
                "status": "ok",
                "tool": req.tool,
                "args": req.args,
                "result": {"content": content}
            }
        except Exception as e:
            return {
                "trace_id": req.trace_id,
                "stage": "tool-response",
                "status": "error",
                "tool": req.tool,
                "args": req.args,
                "error": str(e)
            }

    if req.tool == "echo":
        return {
            "trace_id": req.trace_id,
            "stage": "tool-response",
            "status": "ok",
            "tool": req.tool,
            "args": req.args,
            "result": {"content": req.args.get("message", "")}
        }

    return {
        "trace_id": req.trace_id,
        "stage": "tool-response",
        "status": "error",
        "tool": req.tool,
        "args": req.args,
        "error": "unknown tool"
    }

if __name__ == "__main__":
    import uvicorn
    import ssl
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="/app/server.key",
        ssl_certfile="/app/server.crt",
        ssl_version=ssl.PROTOCOL_TLSv1_2,
    )
