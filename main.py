from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

REAL_SERVER = "https://clientbp.ggpolarbear.com"

@app.route('/', methods=['GET'])
def home():
    return "Proxy Headshot is running!"

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    body = request.get_data()
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}
    
    # ====== CHỈ SỬA REQUEST BẮN (KHÔNG ĐỤNG VÀO LOGIN) ======
    if any(key in path.lower() for key in ['shoot', 'fire', 'attack', 'hit', 'damage']):
        try:
            data = json.loads(body.decode('utf-8')) if body else {}
            if isinstance(data, dict):
                if "hitbox" in data:
                    data["hitbox"] = "head"
                if "bodyPart" in data:
                    data["bodyPart"] = "head"
                if "part" in data:
                    data["part"] = "head"
                data["isHeadshot"] = True
                data["hitType"] = "head"
            body = json.dumps(data).encode('utf-8')
            print(f"[+] SỬA REQUEST BẮN -> HEADSHOT")
        except Exception as e:
            print(f"[-] LỖI SỬA: {e}")
    
    # ====== FORWARD TẤT CẢ (KỂ CẢ MAJORLOGIN) ======
    try:
        resp = requests.request(
            method=request.method,
            url=f"{REAL_SERVER}/{path}",
            headers=headers,
            data=body,
            timeout=10
        )
        return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        print(f"[-] LỖI FORWARD: {e}")
        return {"error": str(e)}, 502
