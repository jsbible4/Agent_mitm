from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ToolRequest(BaseModel):
    tool: str
    args: dict

@app.post("/tool")
def run_tool(req: ToolRequest):
    print("받은 요청:", req)
    return {
        "status": "ok",
        "tool": req.tool,
        "args": req.args
    }
