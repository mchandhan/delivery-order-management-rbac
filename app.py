from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from dotenv import load_dotenv
import requests
import os

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DB_PATH = 'orders.db'
HF_API_KEY = os.getenv("HF_API_KEY")

@app.route('/api/chat', methods=['POST'])
def chat_proxy():
    data = request.json
    try:
        # Find the system message and update it
        for msg in data.get('messages', []):
            if msg.get('role') == 'system':
                msg['content'] = """You are Nova, an expert manufacturing assistant. 
                Your goal is to help users place orders. Even if the user makes typos or combines words (like 'platesdue'), 
                carefully extract the part name, material, quantity, and deadline.
                
                If you identify an order, append this EXACT JSON block at the end:
                {"action": "create_order", "data": {"partName": "...", "material": "...", "quantity": ..., "deadline": "..."}}
                
                Fill the values based on user input. Quantity MUST be a number.
                Keep your conversation professional and helpful."""

        response = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            headers={"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"},
            json=data,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Orders table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            part_name TEXT,
            material TEXT,
            quantity INTEGER,
            deadline TEXT,
            status TEXT
        )
    ''')
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    # Chat History table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT name, email, role FROM users')
        users = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/chat_history', methods=['POST'])
def save_chat():
    data = request.json
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO chat_history (user_email, role, content)
            VALUES (?, ?, ?)
        ''', (data['email'], data['role'], data['content']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/chat_history/<email>', methods=['GET'])
def get_user_chat(email):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM chat_history WHERE user_email = ? ORDER BY timestamp ASC', (email,))
        history = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/')
def index():
    return send_from_directory('.', 'log_siign.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO orders (id, part_name, material, quantity, deadline, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['id'],
            data['partName'],
            data['material'],
            data['quantity'],
            data['deadline'],
            data.get('status', 'Received')
        ))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Order saved to database"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM orders')
        rows = c.fetchall()
        orders = [dict(row) for row in rows]
        conn.close()
        return jsonify(orders)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.json
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        ''', (data['name'], data['email'], data['password'], data['role']))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Registration successful"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email already exists"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/orders/<id>', methods=['DELETE'])
def delete_order(id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM orders WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Order deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/orders/<id>/status', methods=['PUT'])
def update_order_status(id):
    data = request.json
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE orders SET status = ? WHERE id = ?', (data['status'], id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Status updated"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.json
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('''
            SELECT * FROM users WHERE email = ? AND password = ? AND role = ?
        ''', (data['email'], data['password'], data['role']))
        user = c.fetchone()
        conn.close()
        if user:
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid email, password or role"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == '__main__':
    init_db()
    app.run(port=8080, debug=True)
