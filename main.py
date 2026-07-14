from flask import Flask, request, Response
import requests
import json
import os

app = Flask(__name__)

REAL_SERVER = "https://clientbp.ggpolarbear.com"

# ====== ROUTE GỐC ======
@app.route('/')
def home():
    return "Proxy Headshot is running! Visit /health to check."

@app.route('/health')
def health():
    return "OK", 200

# ====== CATCH ALL REQUEST (TRỪ ROOT VÀ HEALTH) ======
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    # Lấy body request từ client
    body = request.get_data(as_text=True)
    
    # Nếu là request bắn -> sửa thành headshot
    if any(key in path.lower() for key in ['shoot', 'fire', 'attack', 'hit', 'damage']):
        try:
            data = json.loads(body) if body else {}
            if isinstance(data, dict):
                if "hitbox" in data:
                    data["hitbox"] = "head"
                if "bodyPart" in data:
                    data["bodyPart"] = "head"
                if "part" in data:
                    data["part"] = "head"
                if "hitPos" in data:
                    data["hitPos"] = {"x": 0, "y": 0, "z": 0}
                data["isHeadshot"] = True
                data["hitType"] = "head"
            body = json.dumps(data)
            print(f"[+] SỬA REQUEST BẮN -> HEADSHOT")
        except Exception as e:
            print(f"[-] LỖI SỬA REQUEST: {e}")
    
    # Forward request đã sửa lên server thật
    try:
        resp = requests.request(
            method=request.method,
            url=f"{REAL_SERVER}/{path}",
            headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
            data=body,
            timeout=10
        )
        return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        print(f"[-] LỖI FORWARD: {e}")
        return {"error": str(e)}, 502
