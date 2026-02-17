import csv
import io
from datetime import datetime, date
from flask import Flask, render_template, request, url_for, redirect, flash, Response
from db import get_conn, init_db
import re


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"
MONTH_RE = re.compile(r"^\d{4}-\d{2}$")

init_db()

def get_months(conn):
    rows = conn.execute(
        """
        SELECT DISTINCT SUBSTR(created_at, 1, 7) AS month
        FROM expenses
        ORDER BY month DESC
        """
    ).fetchall()
    return [r["month"] for r in rows]



def last_n_months(n: int = 12) -> list[str]:
    """Return a list like ['2026-01', '2025-12', ...] for the last n months."""
    y = date.today().year
    m = date.today().month

    months = []
    for _ in range(n):
        months.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return months

def describe_filters(category: str, month: str) -> str:
    if not category and not month:
        return "No filters (showing all expenses)."
    parts = []
    if category:
        parts.append(f"Category: {category}")
    if month:
        parts.append(f"Month: {month}")
    return "Active filters: " + " • ".join(parts)


def get_categories(conn):
    return conn.execute(
        "SELECT DISTINCT category FROM expenses ORDER BY category"
    ).fetchall()

def get_filters():
    """Read filters from the URL query string (GET params)."""
    category = request.args.get("category", "").strip()
    month = request.args.get("month", "").strip()
    
    if month and not MONTH_RE.match(month):
        month = ""
    
    return category, month

def build_where_sql(category: str, month: str):
    """
    Build a safe SQL WHERE clause +parameters list based on filters.

    Returns:
        where_sql (str): "" or " WHERE ... AND ..."
        params (list): values matching the ? placeholders 
    """
    conditions = []
    params = []

    if category:
        conditions.append("category = ?")
        params.append(category)

    if month:
        conditions.append("created_at LIKE ?")
        params.append(f"{month}%")
    
    where_sql = ""
    if conditions:
        where_sql = " WHERE " + " AND ".join(conditions)

    return where_sql, params

@app.get("/")
def index():
    category, month = get_filters()
    where_sql, params = build_where_sql(category, month)

    base_sql = "SELECT * FROM expenses" + where_sql + " ORDER BY created_at DESC"

    with get_conn() as conn:
        expenses = conn.execute(base_sql, params).fetchall()

        total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM (" + base_sql + ") AS filtered",
            params
        ).fetchone()["total"]

        categories = conn.execute(
                "SELECT DISTINCT category FROM expenses ORDER BY category"
        ).fetchall()

        months = get_months(conn)


    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        categories=categories,
        selected_category=category,
        selected_month=month,
        months=months,
        filters_text=describe_filters(category, month),
    )


@app.get("/stats")
def stats():
    category, month = get_filters()
    where_sql, params = build_where_sql(category, month)

    with get_conn() as conn:
        categories = get_categories(conn)
        months = get_months(conn)

        by_category = conn.execute(
            """
            SELECT category, COALESCE(SUM(amount), 0) AS total
            FROM expenses
            """ + where_sql + """
            GROUP BY category
            ORDER BY total DESC
            """,
            params,
        ).fetchall()

        by_month = conn.execute(
            """
            SELECT SUBSTR(created_at, 1, 7) AS month, COALESCE(SUM(amount), 0) AS total
            FROM expenses
            """ + where_sql + """
            GROUP BY month
            ORDER BY month DESC
            """,
            params,
        ).fetchall()

    return render_template(
        "stats.html",
        categories=categories,
        by_category=by_category,
        by_month=by_month,
        selected_category=category,
        selected_month=month,
        months=months,
        filters_text=describe_filters(category, month),
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

@app.get("/export.csv")
def export_csv():
    category, month = get_filters()
    where_sql, params = build_where_sql(category, month)

    sql = "SELECT id, created_at, category, description, amount FROM expenses" + where_sql + " ORDER BY created_at DESC"

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()

    # CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(["id", "created_at", "category", "description", "amount"])

    # Data rows
    for r in rows:
        writer.writerow([r["id"], r["created_at"], r["category"], r["description"], r["amount"]])

    csv_text = output.getvalue()
    output.close()

    # professional file name w/ filters and timestamp
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    parts = ["expenses"]
    if category:
        parts.append(f"category-{category}")
    if month:
        parts.append(f"month-{month}")
    filename = "_".join(parts) + f"_{ts}.csv"

    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )



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
