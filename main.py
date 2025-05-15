import os
import sqlite3
import json
import subprocess
from flask import Flask, request, make_response

app = Flask(__name__)
DATABASE = 'users.db'

# Insecure Database Initialization (no input validation)
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    conn.commit()
    conn.close()

# Insecure Route: SQL Injection
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    c.execute(query)  # 🔥 Vulnerable to SQL Injection
    user = c.fetchone()
    conn.close()
    if user:
        return "Welcome!"
    else:
        return "Invalid credentials"

# Insecure Route: Command Injection
@app.route("/ping", methods=["GET"])
def ping():
    ip = request.args.get("ip")
    output = subprocess.getoutput(f"ping -c 1 {ip}")  # 🔥 Command Injection
    return f"<pre>{output}</pre>"

# Insecure Route: XSS
@app.route("/greet", methods=["GET"])
def greet():
    name = request.args.get("name", "")
    return f"<h1>Hello {name}</h1>"  # 🔥 XSS Vulnerability

# Insecure Route: Insecure Deserialization
@app.route("/load", methods=["POST"])
def load():
    data = request.data.decode()
    obj = json.loads(data)  # 🔥 No schema validation — prone to logic abuse
    return f"Received object with keys: {', '.join(obj.keys())}"

# Insecure Route: Hardcoded Credentials
@app.route("/admin")
def admin_panel():
    auth = request.headers.get("Authorization")
    if auth == "Basic YWRtaW46cGFzc3dvcmQ=":  # 🔥 Base64 for "admin:password"
        return "Admin Access Granted"
    else:
        return "Forbidden", 403

# Insecure Route: Sensitive Data Exposure via Debug
@app.route("/debug")
def debug():
    return str(request.__dict__)  # 🔥 Leaks internal request state

# Insecure File Write (Path Traversal)
@app.route("/write", methods=["POST"])
def write_file():
    filename = request.args.get("filename")
    content = request.data.decode()
    with open(f"./uploads/{filename}", "w") as f:  # 🔥 Path Traversal Risk
        f.write(content)
    return "File written." # changes in file

if __name__ == "__main__":
    init_db()
    app.run(debug=True)  # 🔥 Debug mode enabled — remote code execution risk
