

## Proxy & Burp Suite – Simple Description
<br>

Reference  
https://blog.naver.com/unpatched_winner/224150678089
<br><br>

**In a restricted environment, MITM testing is performed using a proxy (Burp Suite) to verify the feasibility of message interception, retransmission, and modification.**
<br><br>

---

## Difference Between Week 2 and Week 3
<br>

<img width="414" height="598" alt="image" src="https://github.com/user-attachments/assets/9d76b501-208d-4d40-aef5-9d60c9b9f970" />
<br><br>

To reuse the Week 2 code and route traffic through a proxy (Burp Suite),  
environment variables were explicitly defined in the `.yml` file.
<br><br>

**Key Environment Settings**
<br>

- **PYTHONUNBUFFERED=1**  
  Used to prevent delayed Docker logs caused by Python’s output buffering, enabling real-time log output for effective debugging.
  <br><br>

- **extra_hosts**  
  Forces a manual mapping in the container’s `/etc/hosts` file  
  (`host.docker.internal → host-gateway`), allowing the container to correctly resolve and connect to the host machine (e.g., Burp Suite on port 8080).
  <br><br>

---

## Modification Tests
<br>

### 1. Prompt Poisoning
<br><br>

**Original request**
<br>
<img width="472" height="427" alt="image" src="https://github.com/user-attachments/assets/a6076ea4-5fc8-4135-a522-45e47d8ac8b4" />
<br><br>

**Modified request**
<br>
<img width="404" height="90" alt="image" src="https://github.com/user-attachments/assets/3804548b-d449-4819-8781-45eac452376d" />
<br><br>

**Modified result**
<br>
<img width="721" height="642" alt="image" src="https://github.com/user-attachments/assets/edf38c00-bf20-4d97-a769-ec4ebbf2e4e5" />
<br><br>

---

### 2. Tool Call Poisoning
<br><br>

Change the tool arguments to read a different file or modify the message.
<br><br>

**Modify message**
<br>
<img width="542" height="500" alt="tool_call_tool변조" src="https://github.com/user-attachments/assets/1904e278-883b-4c92-b4ad-da85a41d23d8" />
<br><br>

**Modify path argument**
<br><br>

- **Original**
<br>
<img width="531" height="408" alt="tool_call_path변조원본" src="https://github.com/user-attachments/assets/c6c3dc64-ccbc-4a58-b50f-410313d61f5b" />
<br><br>

- **Modified**
<br>
<img width="535" height="520" alt="tool_call_path변조" src="https://github.com/user-attachments/assets/a551cd4a-4250-4908-bef4-24a1d25712da" />
<br><br>

---

### 3. Tool Response Poisoning
<br><br>

Used a **Match and Replace** rule to automatically modify the response.
<br><br>

**Add rule**
<br>
<img width="900" height="440" alt="response_poisoning_rule" src="https://github.com/user-attachments/assets/fcef73b6-79aa-4b99-a024-3d1abcaa5b00" />
<br><br>

**Enable rule**
<br>
<img width="790" height="218" alt="response_poisoning_rule0" src="https://github.com/user-attachments/assets/545c185d-87fb-4256-b16d-b91597dda7de" />
<br><br>

**Result**
<br>
<img width="548" height="474" alt="response_poisoning_result" src="https://github.com/user-attachments/assets/6809cd9c-77a2-4898-8339-34c0febbdf47" />
<br><br>

---

## Troubleshooting
<br>

### 1) Duplicate Packets Were Repeatedly Sent
<br><br>

**Symptom**
<br>
Multiple identical packets (same `trace_id`) appeared in Burp, even though the request was intended to be intercepted and modified only once.
<br><br>

**Root Cause**
<br>
<img width="503" height="176" alt="image" src="https://github.com/user-attachments/assets/c6cb6658-ed13-4e16-8c0a-66390ec91470" />
<br><br>

`agent_a` was configured to retry up to 30 times, and the timeout was too short.  
When Burp Intercept was ON, the request was held before forwarding.  
During this time, the client hit the timeout and retried the same request, causing multiple packets to be sent.
<br><br>

<img width="716" height="605" alt="image" src="https://github.com/user-attachments/assets/5d820707-6e92-4b0d-9dbb-850a074952ee" />
<br><br>

**Resolution**
<br>
- Removed the retry loop so the request is sent only once.  
- Increased the timeout to a sufficiently long value (**600 seconds**) to allow enough time for interception and modification before forwarding.
<br><br>

---

### 2) `/agent` Returned `500 Internal Server Error` After Tampering With `tool_call`
<br><br>

**Symptom**
<br>
After turning Intercept ON and modifying the `tool_call` arguments (e.g., the file path), the final `/agent` response returned **500 Internal Server Error** instead of a normal result.
<br><br>

**Root Cause**
<br>
<img width="688" height="87" alt="image" src="https://github.com/user-attachments/assets/b1550ef6-59dd-4d7b-b608-814b49d0c9ab" />
<br><br>

Docker container logs showed that the request from `agent_b` to `tool_server` used a **3-second timeout**.  
While the request was held in Burp for modification, this timeout was exceeded, triggering a `ReadTimeout` exception and causing the `/agent` endpoint to fail.
<br><br>

<img width="678" height="97" alt="image" src="https://github.com/user-attachments/assets/93f45b16-7687-40e4-abdc-cebf1d6ee8ab" />
<br><br>

**Resolution**
<br>
- Increased the timeout for the `agent_b → tool_server` request from **3 seconds to 600 seconds**.  
- After this change, `/agent` returned **200 OK**, and the tampered tool response was successfully propagated to the final output.
<br><br>

---

### 3) No Response When Sending Packets via Repeater
<br><br>

**Symptom**
<br>
When using Burp Repeater, no response packets were received.
<br><br>

**Root Cause**
<br>
Burp Suite does not automatically resolve Docker internal service names.
<br><br>


```
TOOL_URL
host.docker.internal:8000
tool_server:8000 

```

<br><br>

**Resolution**
<br>
The code was already configured to work through `host.docker.internal`,  
so the request URL was manually updated to use that address.
<br><br>

<img width="1156" height="810" alt="image" src="https://github.com/user-attachments/assets/3f01ae48-db2f-4195-8bf3-b1074883571a" />

if isn't working, check out hosts file. 
host.docker.internal could be mapped to different ip address.






