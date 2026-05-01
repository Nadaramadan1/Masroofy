import os
import json
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify # أضفنا jsonify
from auth_service import AuthorizationService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.urandom(24)

auth_service = AuthorizationService()

# ================= HELPER FUNCTIONS =================
def load_budget():
    try:
        with open(os.path.join(BASE_DIR, "data", "budgets.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"total_budget": 0, "start_date": "-", "end_date": "-"}

def load_expenses():
    try:
        with open(os.path.join(BASE_DIR, "data", "expenses.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def calculate_chart_data(expenses):
    totals = defaultdict(float)
    total_spent = 0
    for e in expenses:
        totals[e["category"]] += e["amount"]
        total_spent += e["amount"]
    if total_spent == 0: return {}
    return {cat: round((val / total_spent) * 100, 2) for cat, val in totals.items()}

# ================= AUTH ROUTES =================

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        success, token, user = auth_service.login(email, password)
        if success:
            session['user_id'] = user.user_id
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "error")
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['email']
        password = request.form['password']
        if password != request.form['confirm_password']:
            flash("Passwords do not match!", "error")
            return render_template('register.html')
        auth_service.register(user_name, email, password)
        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# ================= MAIN ROUTES =================

@app.route("/")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    budget = load_budget()
    expenses = load_expenses()
    total_spent = sum(e["amount"] for e in expenses)
    remaining = budget["total_budget"] - total_spent
    chart_data = calculate_chart_data(expenses)

    warning_80 = "⚠ You have used 80% of your budget" if total_spent >= 0.8 * budget["total_budget"] else None
    warning_over = "❌ Budget Exhausted!" if total_spent >= budget["total_budget"] else None

    return render_template(
        "dashboard.html",
        total_budget=budget["total_budget"],
        remaining=remaining,
        start_date=budget["start_date"],
        end_date=budget["end_date"],
        expenses=expenses,
        chart_data=chart_data,
        warning_80=warning_80,
        warning_over=warning_over,
        total_spent=total_spent
    )

@app.route("/chart-data")
def chart_data():
    if 'user_id' not in session:
        return jsonify({})
    expenses = load_expenses()
    data = calculate_chart_data(expenses)
    return jsonify(data)

@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == "POST":
        expenses = load_expenses()
        expenses.append({
            "amount": float(request.form["amount"]),
            "category": request.form["category_id"],
            "date": request.form["expense_date"],
            "note": request.form.get("note", "")
        })
        with open(os.path.join(BASE_DIR, "data", "expenses.json"), "w") as f:
            json.dump(expenses, f, indent=4)
        return redirect(url_for('dashboard'))
    return render_template("add_expense.html")

@app.route("/history")
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # getTransactionsByCycleID() is simulated by load_expenses() for now
    transactionsList = load_expenses()
    
    # sortByDateDescending(transactionsList)
    sortedList = sorted(transactionsList, key=lambda x: x.get('date', ''), reverse=True)
    
    return render_template("history.html", transactions=sortedList)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)