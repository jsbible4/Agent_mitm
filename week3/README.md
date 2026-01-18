## proxy & burp suite simple descritption

https://blog.naver.com/unpatched_winner/224150678089



**In a restricted environment, MITM testing is performed using a proxy(Burp Suite) to verify the feasibility of message interception, retransmission, and modification**


## difference week2 to week3

<img width="414" height="598" alt="image" src="https://github.com/user-attachments/assets/9d76b501-208d-4d40-aef5-9d60c9b9f970" />


to reuse the code week2 and make traffic go through the procy(Burp Suite), explicitly use Environment variable in .yml file. <br>
- PYTHONUNBUFFERED=1: Used to prevent delayed Docker logs caused by Python’s output buffering, enabling real-time log output for effective debugging.<br>
- extra_hosts: Forces a manual mapping in the container’s /etc/hosts file (host.docker.internal → host-gateway), allowing the container to correctly resolve and connect to the host machine (e.g., Burp Suite on port 8080).

##  troubleshooting

1. can't see **tool_call packet** in burp suite history

<br>cause of problem : server healthcheck 

<br> <img width="673" height="293" alt="image" src="https://github.com/user-attachments/assets/877062d0-38e4-4764-a973-e700f8e5c958" />
<br>
resolution
<br>: turn off intercept and just check the packet in http history hh..
<br>+ in docker desktop, restart agent_a and finally found!! 


2. when i turn on intercept, agent_a cannot connect to agent_b
<br>cause of problem : timeout (agent_b to tool_server)
<img width="688" height="87" alt="image" src="https://github.com/user-attachments/assets/7535de38-3cdf-4d0a-9946-6a08adac2887" />
<br>
code
<br> <img width="678" height="97" alt="image" src="https://github.com/user-attachments/assets/515ed018-3128-4bbf-88ae-f01403494cf3" />

<br>resolution
<br>: change timeout 3 to 600

<br>
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








