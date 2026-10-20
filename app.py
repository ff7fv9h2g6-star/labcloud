
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

ALLOWED_CATEGORIES = {"computer", "network", "software"}
ALLOWED_PRIORITIES = {"low", "medium", "high"}

requests_db = {}
next_id = 1


@app.get("/")
def index():
    return jsonify({
        "application": "LabCloud",
        "status": "running",
        "environment": os.getenv("APP_ENV", "development")
    }), 200


@app.get("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.get("/api/requests")
def get_requests():
    return jsonify(list(requests_db.values())), 200


@app.post("/api/requests")
def create_request():
    global next_id

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON объекті қажет"}), 400

    title = data.get("title")
    category = data.get("category")
    priority = data.get("priority")
    description = data.get("description", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title бос болмауы керек"}), 400

    if category not in ALLOWED_CATEGORIES:
        return jsonify({"error": "category мәні жарамсыз"}), 400

    if priority not in ALLOWED_PRIORITIES:
        return jsonify({"error": "priority мәні жарамсыз"}), 400

    if not isinstance(description, str):
        return jsonify({"error": "description мәтін болуы керек"}), 400

    if len(title.strip()) > 120 or len(description) > 1000:
        return jsonify({"error": "Мәтін ұзындығы шектен асты"}), 400

    item = {
        "id": next_id,
        "title": title.strip(),
        "category": category,
        "priority": priority,
        "description": description.strip()
    }

    requests_db[next_id] = item
    next_id += 1

    return jsonify(item), 201


@app.get("/api/requests/<int:request_id>")
def get_request(request_id):
    item = requests_db.get(request_id)

    if item is None:
        return jsonify({"error": "Өтінім табылмады"}), 404

    return jsonify(item), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
