from flask import Flask, render_template

app = Flask(__name__)

@app.get("/")
def index():
    expenses = [
        {"category": "Food", "description": "Lunch", "amount": 8.50},
        {"category": "Transport", "description": "Tube", "amount": 3.20},
        {"category": "Bills", "description": "Phone", "amount": 12.00},
    ]
    total = sum(e["amount"] for e in expenses)
    return render_template("index.html", expenses=expenses, total=total)

if __name__ == "__main__":
    app.run(debug=True)

