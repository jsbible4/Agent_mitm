# Agent_mitm
finding solution for mitm vulnerability of agent to agent ai communication 

purpose 
1. using Docker, simply implementing agent(client) to agent(server) HTTP communication 
2. checkout network packet

-------------
##container
1. agent_a(client)
- HTTP request
- method : POST
- message : tool-call(JSON)

2. agent_b(server)
- provide /tool endpoint
- HTTP response

##docker-compose.yml
<img width="220" height="296" alt="image" src="https://github.com/user-attachments/assets/5fd8dd56-e16f-4a8a-8cbf-4aae084f04cb" />

services: container service definitions
agent_b, agent_a: service names
build: uses the specified folder as the build context and builds the image using the Dockerfile inside that folder
ports: port forwarding; "8000:8000" maps host port 8000 to container port 8000
depends_on: controls startup order only; it does not guarantee that agent_b is ready to accept requests


##agent_a.py
<img width="492" height="390" alt="image" src="https://github.com/user-attachments/assets/e706eb76-6342-4cbb-94d0-fdaa023eb695" />

import time : used for sleeping beween retries
import requests : library for sending HTTP requests 

tool_call : start of data to send to server
- tool : : "tool name"    name of tool which will be implemented at server
- args : {"path": "/hello.txt"} arguments for the tool (read hello.txt)

url = "http://agent_b:8000/tool" 
- in docker compose, container communicates with each other through an internal docker network using service names as hostnames.

for else : executed only if all retry attempts fail


##agent_b.py
<img width="277" height="334" alt="image" src="https://github.com/user-attachments/assets/e380fa7f-cd9a-4007-aed3-811fc9bdefa0" />

from fastapi import FastAPI
- imports FastAPI to create a web server application

from pydantic import BaseModel
- imports BaseModel to define and validate the schema of request/response data

app = FastAPI()
- creates an instance of a FastAPI application

class ToolRequest(BaseModel):
- defines the schema of the request body

tool: str
- the request must contain a field named "tool" of type string

args: dict
- the request must contain a field named "args" of type dictionary

@app.post("/tool")
- registers an endpoint that handles HTTP POST requests to /tool

def run_tool(req: ToolRequest):
- defines the endpoint handler function
- automatically parses and validates the request body as ToolRequest

print("받은 요청:", req)
- prints the received request to the server console for debugging

return { ... }
- constructs and returns a JSON response to the client

"status": "ok"
- indicates successful handling of the request

"tool": req.tool
"args": req.args
- echoes the received tool name and arguments back in the response



command 
- docker compose up --build (terminal 1)
- docker exec -it week1-agent_b-1 tcpdump -i eth0 -s 0 -w /tmp/agent_http.pcap tcp port 8000 (terminal 2)
- docker compose restart agent_a (terminal 3)

- docker cp week1-agent_b-1:/tmp/agent_http.pcap ./agent_http.pcap (terminal 2)
<img width="260" height="37" alt="image" src="https://github.com/user-attachments/assets/25d551e8-13a9-47d9-9833-57472e692000" />



<img width="672" height="212" alt="image" src="https://github.com/user-attachments/assets/f3fade24-83a4-4763-be5b-78aa10731a83" />




