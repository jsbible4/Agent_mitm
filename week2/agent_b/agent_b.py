from fastapi import FastAPI
from pydantic import BaseModel
import requests

TOOL_URL = "http://tool_server:8000/tool"

app = FastAPI()

class AgentRequest(BaseModel):
    trace_id: str
    stage: str
    prompt: str

def decide_tool(prompt: str) -> dict:
    """
    규칙 기반 '판단' 로직.
    - prompt를 해석해서 tool-call을 결정한다.
    """
    p = prompt.lower().strip()

    if "read" in p and "file" in p:
        return {
            "tool": "read_file",
            "args": {"path": "/data/hello.txt"}
        }

    # 그 외는 echo로 처리
    return {
        "tool": "echo",
        "args": {"message": f"echo from Agent B (prompt='{prompt}')" }
    }

@app.post("/agent")
def agent_endpoint(req: AgentRequest):
    # 1) prompt 수신(네트워크에서 온 입력)
    prompt = req.prompt

    # 2) 내부 처리 단계: tool-call 결정
    tool_call = decide_tool(prompt)
    tool_payload = {
        "trace_id": req.trace_id,
        "stage": "tool-call",
        "tool": tool_call["tool"],
        "args": tool_call["args"],
    }

    # 3) tool_server 호출 (이 HTTP가 tool-call 패킷으로 캡처됨)
    tool_resp = requests.post(TOOL_URL, json=tool_payload, timeout=3).json()

    # 4) 최종 response 구성 (A로 돌아가는 response 패킷)
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
