from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, random, datetime
import requests

app = Flask(__name__)
app.secret_key = "forex_final_key"

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        balance REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        currency TEXT,
        action TEXT,
        amount REAL,
        profit REAL,
        time TEXT
    )
    """)

    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username,password,role,balance) VALUES (?,?,?,?)",
            ("admin","admin123","admin",0)
        )

    db.commit()
    db.close()

init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u = request.form["username"]
        p = request.form["password"]

        db = get_db()
        c = db.cursor()
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (u,p))
        r = c.fetchone()
        db.close()

        if r:
            session["user"] = u
            session["role"] = r[0]
            return redirect("/admin" if r[0]=="admin" else "/dashboard")

    return render_template("login.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        db = get_db()
        c = db.cursor()
        c.execute(
            "INSERT INTO users (username,password,role,balance) VALUES (?,?,?,?)",
            (request.form["username"], request.form["password"], "user", 100000)
        )
        db.commit()
        db.close()
        return redirect("/")
    return render_template("register.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    db = get_db()
    c = db.cursor()

    # ---- TRADE ----
    if request.method=="POST":
        amt = float(request.form["amount"])
        profit = round(random.uniform(-0.03, 0.05) * amt, 2)

        c.execute("UPDATE users SET balance = balance + ? WHERE username=?",
                  (profit, session["user"]))

        c.execute("""
        INSERT INTO trades (username,currency,action,amount,profit,time)
        VALUES (?,?,?,?,?,?)
        """, (session["user"], request.form["currency"],
              request.form["action"], amt, profit,
              str(datetime.datetime.now())))

        db.commit()

    # ---- BALANCE ----
    c.execute("SELECT balance FROM users WHERE username=?", (session["user"],))
    balance = c.fetchone()[0]

    # ---- TRADES ----
    c.execute("""
    SELECT currency,action,amount,profit FROM trades
    WHERE username=? ORDER BY id DESC
    """, (session["user"],))
    trades = c.fetchall()

    # ---- TRP SCORE ----
    c.execute("SELECT COUNT(*) FROM trades WHERE username=? AND profit>0",
              (session["user"],))
    win = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM trades WHERE username=?",
              (session["user"],))
    total = c.fetchone()[0]

    trp = round((win/total)*100,2) if total>0 else 0

    # ---- RISK ANALYSIS ----
    risk = "Low"
    risk_percent = 0

    if total > 0:
        last_amt = trades[0][2]
        risk_percent = round((last_amt / balance) * 100, 2)

        if risk_percent > 15:
            risk = "High"
        elif risk_percent > 5:
            risk = "Medium"

    db.close()

    return render_template(
        "dashboard.html",
        balance=balance,
        trades=trades,
        trp=trp,
        risk=risk,
        risk_percent=risk_percent
    )

# ---------- ADMIN ----------
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()
    c = db.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM trades")
    trades = c.fetchone()[0]

    c.execute("SELECT SUM(profit) FROM trades")
    profit = c.fetchone()[0] or 0

    db.close()
    return render_template("admin.html", users=users, trades=trades, profit=profit)

# ---------- MARKET TREND ----------
@app.route("/chart-data")
def chart_data():
    prices = [round(random.uniform(82,88),2) for _ in range(30)]
    trend = "UP" if prices[-1] > prices[0] else "DOWN"
    return jsonify({"prices":prices, "trend":trend})

# ---------- AI ----------
@app.route("/ai-predict")
def ai_predict():
    return jsonify({
        "trend": random.choice(["BUY","SELL"]),
        "confidence": random.randint(70,95)
    })

# ---------- CURRENCY CONVERTER (NEW FEATURE) ----------
@app.route("/convert-currency")
def convert_currency():
    base = request.args.get("from")
    target = request.args.get("to")
    amount = float(request.args.get("amount"))

    url = f"https://open.er-api.com/v6/latest/{base}"
    data = requests.get(url).json()

    rate = data["rates"].get(target)
    converted = round(amount * rate, 2)

    return jsonify({
        "from": base,
        "to": target,
        "amount": amount,
        "converted": converted
    })

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

app.run(debug=True)

