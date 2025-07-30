from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = "data.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Получение кейсов ----------
@app.route("/get_cases", methods=["GET"])
def get_cases():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, image FROM cases")
    cases = cursor.fetchall()

    data = []
    for c in cases:
        data.append({
            "id": c["id"],
            "name": c["name"],
            "price": c["price"],
            "image": c["image"]
        })
    return jsonify(data)

# ---------- Получение подарков ----------
@app.route("/get_gifts", methods=["GET"])
def get_gifts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, emoji, rarity, image FROM gifts")
    gifts = cursor.fetchall()

    data = []
    for g in gifts:
        data.append({
            "id": g["id"],
            "name": g["name"],
            "emoji": g["emoji"],
            "rarity": g["rarity"],
            "image": g["image"]
        })
    return jsonify(data)

# ---------- Открытие кейса ----------
@app.route("/open_case", methods=["POST"])
def open_case():
    data = request.json
    user_id = data.get("user_id")
    case_id = data.get("case_id")

    conn = get_db()
    cursor = conn.cursor()

    # Получаем цену кейса
    cursor.execute("SELECT price FROM cases WHERE id=?", (case_id,))
    case = cursor.fetchone()
    if not case:
        return jsonify({"status": "error", "message": "Кейс не найден"})

    price = case["price"]

    # Проверяем баланс
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user or user["balance"] < price:
        return jsonify({"status": "error", "message": "Недостаточно звёзд"})

    # Снимаем звёзды
    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (price, user_id))
    conn.commit()

    # Выбираем случайный подарок
    cursor.execute("""
        SELECT g.id, g.name, g.emoji, g.rarity
        FROM case_gifts cg
        JOIN gifts g ON cg.gift_id = g.id
        WHERE cg.case_id=?
        ORDER BY RANDOM()
        LIMIT 1
    """, (case_id,))
    gift = cursor.fetchone()

    if not gift:
        return jsonify({"status": "error", "message": "В кейсе нет подарков"})

    # Добавляем в инвентарь
    cursor.execute("INSERT INTO inventory (user_id, gift_id) VALUES (?, ?)", (user_id, gift["id"]))
    conn.commit()

    return jsonify({
        "status": "success",
        "gift": {
            "id": gift["id"],
            "name": gift["name"],
            "emoji": gift["emoji"],
            "rarity": gift["rarity"]
        }
    })

# ---------- Получение баланса ----------
@app.route("/get_balance/<int:user_id>", methods=["GET"])
def get_balance(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"balance": 0})
    return jsonify({"balance": user["balance"]})

# ---------- Пополнение ----------
@app.route("/add_balance", methods=["POST"])
def add_balance():
    data = request.json
    user_id = data.get("user_id")
    amount = data.get("amount")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users(user_id, balance) VALUES(?, 0)", (user_id,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

    return jsonify({"status": "success", "message": f"Баланс пополнен на {amount}⭐"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
