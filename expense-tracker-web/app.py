from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, flash
from db import get_conn, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"

init_db()

@app.get("/")
def index():
    category = request.args.get("category", "").strip()
    month = request.args.get("month", "").strip()

    sql = "SELECT * FROM expenses"
    conditions = []
    params = []

    if category:
        conditions.append("category = ?")
        params.append(category)

    if month:
        conditions.append("created_at LIKE ?")
        params.append(f"{month}%")

    if conditions:
        sql += " WHERE " + " AND".join(conditions)

    sql += " ORDER BY created_at DESC"

    with get_conn() as conn:
        expenses = conn.execute(sql, params).fetchall()

        total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM (" + sql + ") AS filtered",
            params
        ).fetchone()["total"]

        categories = conn.execute(
            "SELECT DISTINCT category FROM expenses ORDER BY category"
        ).fetchall()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        categories=categories,
        selected_category=category,
        selected_month=month

    )


@app.get("/add")
def add_page():
    return render_template("add.html")

@app.get("/edit/<int:expense_id>")
def edit_page(expense_id: int):
    with get_conn() as conn:
        exp = conn.execute(
            "SELECT * FROM expenses WHERE id = ?",
            (expense_id,)
        ).fetchone()

    if exp is None:
        flash("Expense not found.")
        return redirect(url_for("index"))
    
    return render_template("edit.html", exp=exp)


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
        flash("Amount must be a number ≥ 0.")
        return redirect(url_for("add_page"))
   
    if not category or not description:
        flash("Category and description are required.")
        return redirect(url_for("add_page"))
    
    created_at = datetime.now().isoformat(timespec="seconds")

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO expenses (amount, category, description, created_at) VALUES (?, ?, ?, ?)",
            (amount, category, description, created_at),
        )
        conn.commit()

    flash("Expense added.")
    return redirect(url_for("index"))

@app.post("/delete/<int:expense_id>")
def delete_expense(expense_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()

    if cur.rowcount == 0:
        flash("Expense not found.")
    else:
        flash("Expense deleted.")
    
    return redirect(url_for("index"))

@app.post("/edit/<int:expense_id>")
def edit_expense(expense_id: int):
    amount_raw = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()

    try:
        amount = float(amount_raw)
        if amount < 0:
            raise ValueError
    except ValueError:
        flash("Amount must be a number ≥ 0.")
        return redirect(url_for("edit_page", expense_id=expense_id))
    
    if not category or not description:
        flash("Category and description required.")
        return redirect(url_for("edit_page", expense_id=expense_id))
    
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE expenses SET amount = ?, category = ?, description = ? WHERE id = ?",
            (amount, category, description, expense_id),
        )
        conn.commit()

    if cur.rowcount == 0:
        flash("Expense not found.")
    else:
        flash("Expense updated.")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
