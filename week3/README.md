## proxy & burp suite simple descritption

https://blog.naver.com/unpatched_winner/224150678089



**In a restricted environment, MITM testing is performed using a proxy(Burp Suite) to verify the feasibility of message interception, retransmission, and modification**


## difference week2 to week3

<img width="414" height="598" alt="image" src="https://github.com/user-attachments/assets/9d76b501-208d-4d40-aef5-9d60c9b9f970" />


to reuse the code week2 and make traffic go through the procy(Burp Suite), explicitly use Environment variable in .yml file. <br>
- PYTHONUNBUFFERED=1: Used to prevent delayed Docker logs caused by Python’s output buffering, enabling real-time log output for effective debugging.<br>
- extra_hosts: Forces a manual mapping in the container’s /etc/hosts file (host.docker.internal → host-gateway), allowing the container to correctly resolve and connect to the host machine (e.g., Burp Suite on port 8080).

##  troubleshooting

1) Duplicate packets were repeatedly sent

<br>Symptom<br>
Multiple identical packets (same `trace_id`) appeared in Burp, even though I intended to intercept and modify the request only once.<br>
<br>
**Root Cause**   <br>
`agent_a` was configured to retry up to 30 times, and the timeout was too short.  <br>
When Burp Intercept was ON, the request was held before forwarding. During this time, the client hit the timeout and retried the same request, causing multiple packets to be sent.<br>
<img width="716" height="605" alt="image" src="https://github.com/user-attachments/assets/5d820707-6e92-4b0d-9dbb-850a074952ee" />

<br>
<br>** Resolution**
<br>
- Removed the retry loop so the request is sent only once.<br>
- Increased the timeout to a sufficiently long value (**600 seconds**) to allow enough time for interception and modification before forwarding.
<br><br>
---

2) `/agent` returned `500 Internal Server Error` after tampering with `tool_call`

<br>Symptom<br>
After turning Intercept ON and modifying the `tool_call` arguments (e.g., the file path), the final `/agent` response returned **500 Internal Server Error** instead of a normal result.
<br><br>
** Root Cause ** <br>
<img width="688" height="87" alt="image" src="https://github.com/user-attachments/assets/b1550ef6-59dd-4d7b-b608-814b49d0c9ab" />
<br>
Docker container logs showed that the request from `agent_b` to `tool_server` used a **3-second timeout**.  <br>
While the request was held in Burp for modification, this timeout was exceeded, triggering a `ReadTimeout` exception and causing the `/agent` endpoint to fail with a 500 error.
<br><img width="678" height="97" alt="image" src="https://github.com/user-attachments/assets/93f45b16-7687-40e4-abdc-cebf1d6ee8ab" />

<br><br>
**Resolution**
<br>
- Increased the timeout for the `agent_b → tool_server` request from **3 seconds to 600 seconds**.
<br>- After this change, `/agent` returned **200 OK**, and the tampered tool response was successfully propagated to the final output.


3. using repeater, there is no response packets for sended packets

<br>cause of problem : Burp Suite doesn't follow the Docker internal name/DNS 
```
TOOL_URL
host.docker.internal:8000
tool_server:8000 

```

<br>resolution
<br>: I've already mapped the code to work through host.docker.internal 
so just mapp the URL 
<br> <img width="1156" height="810" alt="image" src="https://github.com/user-attachments/assets/3f01ae48-db2f-4195-8bf3-b1074883571a" />








