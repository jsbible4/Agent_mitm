# communication between multi agents

##code explanation

###agent_a
<img width="500" height="633" alt="image" src="https://github.com/user-attachments/assets/51950fae-ea99-462c-9d04-485a0f334d59" />

***PROMPT = os.getenv("PROMPT", "read a file")***
- Control input via environment variable for reproducible experiments
- we can change this field to check out how different outcome we get if we give a little change to prompt.

trace_id = str(uuid.uuid4())
- to check the request flow in network packer, create trace_id

payload = { ... }
- Transmit the prompt stage as a JSON payload over HTTP

r = requests.post(AGENT_B_URL, json=payload, timeout=2)
resp = r.json()
- agent_a  send POST requests to agent_b /agent endpoint.
- get response from agent_b tby r.json
- print tool-call response

  
###agent_b
1.
<img width="249" height="17" alt="image" src="https://github.com/user-attachments/assets/79c4a133-e9a7-4150-aaa9-a2e27d4171e9" />
communications between server and agent_b use port 8000
tool_server /tool endpoint

2.
<img width="408" height="293" alt="image" src="https://github.com/user-attachments/assets/18c211a9-b8e4-4d4f-be28-5f796dee9d4b" />
agent_b analyzes the received prompt and decides which tool should be called.

class AgentRequest(BaseModel):
- Definition of the HTTP request format sent from Agent A

def decide_tool(prompt: str) -> dict:
- Rule-based decision logic
- If specific keywords (read and file) exist in the prompt, the read_file tool is selected
- Otherwise, the echo tool is selected

3.
<img width="480" height="409" alt="image" src="https://github.com/user-attachments/assets/a39d182c-e2e0-4093-83be-a35919fc643f" />

***tool_call = decide_tool(prompt)***
- Decide which tool to invoke based on the prompt

tool_payload = { "stage": "tool-call", ... }
- compose tool_call as a JSON payload

***requests.post(TOOL_URL, ...)***
- Send the tool-call request to the tool server
- variable tool_resp will get the returned value(tool_call response from tool_server)
  
***response_payload = { "stage": "response", ... }***
- Create the final response including prompt, tool-call, and tool-result
- This response is returned to Agent A as an HTTP response



###tool_server
<img width="399" height="676" alt="image" src="https://github.com/user-attachments/assets/55abf675-8b2c-4a9d-97dd-c83661bf14b3" />

ToolRequest()
- Definition of the HTTP tool_call request format sent from Agent B

@app.post("/tool")
def run_tool(req: ToolRequest):
- tool server endpoint
- ***return the tool_call response***

if req.tool == "read_file":
- Read the specified file and return its content

if req.tool == "echo":
- Return the received message as-is


###docker-compose.yml
<img width="319" height="376" alt="image" src="https://github.com/user-attachments/assets/894f2810-473d-4715-8ac1-fa2807abe4a7" />
agent_b 
- use port 8001

tool_server
- use port 8000

environment:
    -PROMT= ~~ 
- input can also be controled in docker-compose.yml file

