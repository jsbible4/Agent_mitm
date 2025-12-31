import time
import requests

tool_call = {
    "tool": "read_file",
    "args": {"path": "/hello.txt"}
}

url = "http://agent_b:8000/tool"

for i in range(30):  # 최대 30초 대기
    try:
        r = requests.post(url, json=tool_call, timeout=2)
        print("서버 응답:", r.json())
        break
    except requests.exceptions.RequestException as e:
        print(f"[{i+1}/30] 아직 서버 준비 안 됨… 재시도")
        time.sleep(1)
else:
    raise RuntimeError("agent_b가 끝내 준비되지 않았음")

time.sleep(10**9)
