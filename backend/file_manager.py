from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ================= LOAD DATA =================
def load_budget():
    path = os.path.join(BASE_DIR, "data", "budgets.json")
    with open(path, "r") as f:
        return json.load(f)

def load_expenses():
    path = os.path.join(BASE_DIR, "data", "expenses.json")
    with open(path, "r") as f:
        return json.load(f)

def save_expenses(data):
    path = os.path.join(BASE_DIR, "data", "expenses.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def save_budget(data):
    path = os.path.join(BASE_DIR, "data", "budgets.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ================= DASHBOARD =================
@app.route("/")
def dashboard():
    budget = load_budget()
    expenses = load_expenses()

    return render_template(
        "dashboard.html",
        budget=budget,
        expenses=expenses
    )

# ================= ADD EXPENSE =================
@app.route("/add-expense", methods=["POST"])
def add_expense():
    amount = float(request.form["amount"])
    category = request.form["category"]

    expenses = load_expenses()
    budget = load_budget()

    new_expense = {
        "id": len(expenses) + 1,
        "amount": amount,
        "category": category
    }

    expenses.append(new_expense)

    # update budget
    budget["activeCycle"]["remainingBalance"] -= amount

    save_expenses(expenses)
    save_budget(budget)

    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)