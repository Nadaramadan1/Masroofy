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
    budget_file = os.path.join(BASE_DIR, "data", "budgets.json")
    if not os.path.exists(budget_file):
        return {"total_allowance": 0, "remaining": 0, "start_date": "", "end_date": ""}
    with open(budget_file, "r", encoding="utf-8") as f:
        return json.load(f)

def load_expenses():
    expense_file = os.path.join(BASE_DIR, "data", "expenses.json")
    if not os.path.exists(expense_file):
        return []
    with open(expense_file, "r", encoding="utf-8") as f:
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

# ================= ROUTES =================

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # 3 attempts logic
        attempts = session.get("login_attempts", 0)
        if attempts >= 3:
            flash("Account locked due to too many failed attempts. Please try again later.", "error")
            return render_template("login.html", locked=True)

        success, token, user = auth_service.login(email, password)
        
        if success:
            session["user_id"] = user.user_id
            session["user_name"] = user.user_name
            session["auth_token"] = token
            session["login_attempts"] = 0 # Reset attempts
            flash(f"Welcome back, {user.user_name}!", "success")
            return redirect(url_for("dashboard"))
        else:
            attempts += 1
            session["login_attempts"] = attempts
            remaining = 3 - attempts
            if remaining > 0:
                flash(f"Invalid credentials. {remaining} attempts remaining.", "error")
            else:
                flash("Account locked due to too many failed attempts.", "error")
            return render_template("login.html", locked=(remaining <= 0))

    return render_template("login.html", locked=(session.get("login_attempts", 0) >= 3))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    budget = load_budget()
    expenses = load_expenses()
    chart_data = calculate_chart_data(expenses)

    return render_template(
        "dashboard.html",
        budget=budget,
        expenses=expenses,
        chart_data=chart_data,
        user_name=session.get("user_name")
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        user_name = request.form.get("user_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("register.html")

        # Check if email already exists
        users = auth_service.repository.load_all()
        if any(u["email"] == email for u in users):
            flash("Email already registered!", "error")
            return render_template("register.html")

        user = auth_service.register(user_name, email, password)
        if user:
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        else:
            flash("Registration failed. Please try again.", "error")
            return render_template("register.html")

    return render_template("register.html")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)