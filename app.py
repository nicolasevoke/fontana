from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ODOO_URL = "https://fontanasrl.odoo.com"
ODOO_DB = "marjorie82-fontana-srl-fontana-1087170"
ODOO_USER = "admin"
ODOO_PASS = "@Fontana$2025@"

def get_session_id():
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": ODOO_DB,
            "login": ODOO_USER,
            "password": ODOO_PASS
        }
    }
    res = requests.post(f"{ODOO_URL}/web/session/authenticate", json=payload)
    session_id = res.cookies.get("session_id")
    if not session_id:
        raise ValueError("No se pudo obtener session_id.")
    return session_id

@app.route("/product_template")
def get_product_template():
    try:
        # Leer offset y limit desde la URL
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 100))

        session_id = get_session_id()
        headers = {"Content-Type": "application/json", "Cookie": f"session_id={session_id}"}

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "product.template",
                "method": "search_read",
                "args": [[]],
                "kwargs": {
                    "offset": offset,
                    "limit": limit,
                    "fields": [
                        "name", "type", "categ_id", "list_price",
                        "uom_id", "seller_ids", "default_code", "id",
                        "classification_category", "cost_history","volume","weight","weight_kg","empaque","x_studio_m3","standard_price"
                    ]
                }
            }
        }

        res = requests.post(f"{ODOO_URL}/web/dataset/call_kw/product.template/search_read", json=payload, headers=headers)
        json_res = res.json()

        if "error" in json_res:
            return jsonify({"error": json_res["error"]}), 500

        return jsonify(json_res.get("result", []))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
