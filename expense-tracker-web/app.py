from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect
from db import get_conn, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"

init_db()

@app.get("/")
def index():
    with get_conn() as conn:
        expenses = conn.execute(
            "SELECT * FROM expenses Order By created_at DESC"
        ).fetchall()

        total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses"
        ).fetchone()["total"]

    return render_template("index.html", expenses=expenses, total=total)


@app.get("/add")
def add_page():
    return render_template("add.html")

@app.post("/add")
def add_expense():
    amount_raw = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()

    try:
        amount = float(amount_raw)
        if amount < 0:
            raise ValueError
    except ValueError:
        flask("Amount must be a number ≥ 0.")
        return redirect(url_for("add_page"))
    
    created_at = datetime.now().isoformat(timespec="seconds")

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO expenses (amount, category, description, created_at) VALUES (?, ?, ?, ?)",
            (amount, category, description, created_at),
        )
        conn.commit()

    Flask("Expense added.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
