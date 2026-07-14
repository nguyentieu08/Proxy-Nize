from flask import Flask, request, Response
import requests
import json
import re

app = Flask(__name__)
REAL_SERVER = "https://clientbp.ggpolarbear.com"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    # Lấy body request từ client
    body = request.get_data(as_text=True)
    
    # Nếu là request bắn -> sửa thành headshot
    if any(key in path.lower() for key in ['shoot', 'fire', 'attack', 'hit', 'damage']):
        try:
            # Parse body JSON
            data = json.loads(body) if body else {}
            
            # Sửa thông tin trúng thành HEAD
            if isinstance(data, dict):
                # Sửa hitbox
                if "hitbox" in data:
                    data["hitbox"] = "head"
                if "bodyPart" in data:
                    data["bodyPart"] = "head"
                if "part" in data:
                    data["part"] = "head"
                # Sửa tọa độ trúng (nếu có)
                if "hitPos" in data:
                    data["hitPos"] = {"x": 0, "y": 0, "z": 0}
                if "position" in data:
                    data["position"] = {"x": 0, "y": 0, "z": 0}
                # Đánh dấu headshot
                data["isHeadshot"] = True
                data["hitType"] = "head"
            
            # Chuyển lại thành JSON
            body = json.dumps(data)
            print(f"[+] SỬA REQUEST BẮN -> HEADSHOT")
        except:
            pass
    
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
        return {"error": str(e)}, 502
