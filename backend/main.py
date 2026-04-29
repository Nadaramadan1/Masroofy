import os
import json
from flask import Flask, render_template

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

DATA_FILE = os.path.join(BASE_DIR, "data", "budgets.json")

def load_budget():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def dashboard():
    budget = load_budget()
    return render_template("dashboard.html", budget=budget)

if __name__ == "__main__":
    app.run(debug=True)
import os
import json
from collections import defaultdict
from flask import Flask, render_template

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

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

    chart_data = {}

    if total_spent == 0:
        return {}

    for cat, value in totals.items():
        chart_data[cat] = round((value / total_spent) * 100, 2)

    return chart_data

# ================= DASHBOARD =================
@app.route("/")
def dashboard():
    budget = load_budget()
    expenses = load_expenses()

    chart_data = calculate_chart_data(expenses)

    return render_template(
        "dashboard.html",
        budget=budget,
        expenses=expenses,
        chart_data=chart_data
    )

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)