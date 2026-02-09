from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class ToolRequest(BaseModel):
    trace_id: str
    stage: Optional[str] = None
    tool: str
    args: dict

@app.post("/tool")
def run_tool(req: ToolRequest):
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
