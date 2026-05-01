import os
import json
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, session, flash
from auth_service import AuthorizationService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)
app.secret_key = os.urandom(24)

auth_service = AuthorizationService()

# ================= LOAD DATA =================
def load_budget():
    with open(os.path.join(BASE_DIR, "data", "budgets.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def load_expenses():
    with open(os.path.join(BASE_DIR, "data", "expenses.json"), "r", encoding="utf-8") as f:
        return json.load(f)

# ================= CHART LOGIC =================
def calculate_chart_data(expenses):
    totals = defaultdict(float)
    total_spent = 0

    for e in expenses:
        totals[e["category"]] += e["amount"]
        total_spent += e["amount"]

    if total_spent == 0:
        return {}

    return {
        cat: round((value / total_spent) * 100, 2)
        for cat, value in totals.items()
    }

# ================= ROUTES =================

@app.route("/")
def dashboard():
    budget = load_budget()
    expenses = load_expenses()

    # total spent
    total_spent = sum(e["amount"] for e in expenses)

    # remaining budget
    remaining = budget["total_budget"] - total_spent

    # chart data
    chart_data = calculate_chart_data(expenses)

    # alerts
    warning_80 = None
    warning_over = None

    if total_spent >= 0.8 * budget["total_budget"]:
        warning_80 = "⚠ You have used 80% of your budget"

    if total_spent >= budget["total_budget"]:
        warning_over = "❌ Budget Exhausted!"

    return render_template(
        "dashboard.html",

        # budget info
        total_budget=budget["total_budget"],
        remaining=remaining,
        start_date=budget["start_date"],
        end_date=budget["end_date"],

        # data
        expenses=expenses,
        chart_data=chart_data,

        # alerts
        warning_80=warning_80,
        warning_over=warning_over,

        # extra (optional useful in UI)
        total_spent=total_spent
    )

# 👇 ده اللي كان ناقص عندك
@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":

        amount = float(request.form["amount"])
        category = request.form["category_id"]
        date = request.form["expense_date"]
        note = request.form.get("note", "")

        expenses = load_expenses()

        expenses.append({
            "amount": amount,
            "category": category,
            "date": date,
            "note": note
        })

        with open(os.path.join(BASE_DIR, "data", "expenses.json"), "w") as f:
            json.dump(expenses, f, indent=4)

        return redirect("/")

    return render_template("add_expense.html")

@app.route("/chart-data")
def chart_data_api():
    expenses = load_expenses()
    return jsonify(calculate_chart_data(expenses))
# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
