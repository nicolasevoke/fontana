from flask import Flask, request, jsonify
import requests
from datetime import datetime

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

@app.route("/sale_order_incremental")
def get_sale_orders_incremental():
    from_date = request.args.get("from", "2025-04-24")  # default desde el 23 de abril 2025
    try:
        datetime.strptime(from_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}), 400

    try:
        session_id = get_session_id()
        headers = {"Content-Type": "application/json", "Cookie": f"session_id={session_id}"}

        offset = 0
        limit = 100
        all_records = []

        while True:
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": "sale.order",
                    "method": "search_read",
                    "args": [[["date_order", ">", from_date]]],
                    "kwargs": {
                        "offset": offset,
                        "limit": limit,
                        "fields": [
                            "name", "state", "date_order", "validity_date", "create_date",
                            "partner_id", "currency_id", "user_id", "invoice_status",
                            "amount_untaxed", "amount_tax", "amount_total", "team_id", "id",
                            "warehouse_id", "cancel_reason_id", "x_for_main",
                            "x_studio_tipo_de_cliente_1", "payment_term_id", "currency_rate"
                        ]
                    }
                }
            }

            res = requests.post(f"{ODOO_URL}/web/dataset/call_kw/sale.order/search_read", json=payload, headers=headers)
            json_res = res.json()

            if "error" in json_res:
                return jsonify({"error": json_res["error"]}), 500

            data = json_res.get("result", [])
            if not data:
                break

            all_records.extend(data)
            offset += limit

        return jsonify(all_records)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
