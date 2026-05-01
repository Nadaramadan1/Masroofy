import os
import json
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from auth_service import AuthorizationService
from datetime import datetime
from calculation_service import CalculationService, DailyLimitStrategy
from budget_cycle import BudgetCycle
from expense_service import ExpenseService
from budget_service import BudgetService
from notification_service import NotificationService

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


    # Implement Dynamic Daily Limit View
    safe_daily_limit = 0
    is_positive_rollover = True
    is_final_day = False
    
    budget_service = BudgetService()
    active_cycle = budget_service.get_active_cycle(session['user_id'])
    
    if active_cycle:
        safe_daily_limit, is_final_day = budget_service.get_dynamic_daily_limit(session['user_id'])
        
        total_days = max((active_cycle.end_date - active_cycle.start_date).days, 1)
        base_daily_limit = active_cycle.total_allowance / total_days
        is_positive_rollover = safe_daily_limit >= base_daily_limit

    warning_80 = "⚠ You have used 80% of your budget" if total_spent >= 0.8 * budget["total_budget"] else None
    warning_over = "❌ Budget Exhausted!" if total_spent >= budget["total_budget"] else None

    return render_template(
        "dashboard.html",
        total_budget=budget["total_budget"],
        remaining=remaining,
        start_date=budget["start_date"],
        end_date=budget["end_date"],
        expenses=expenses,
        warning_80=warning_80,
        warning_over=warning_over,
        total_spent=total_spent,
        safe_daily_limit=safe_daily_limit,
        is_positive_rollover=is_positive_rollover,
        is_final_day=is_final_day
    )

@app.route("/chart-data")
def chart_data_api():
    if 'user_id' not in session:
        return jsonify({})
        
    transactions = load_expenses()
    if not transactions:
        return jsonify({})
        
    expense_service = ExpenseService()
    category_totals = expense_service.aggregateByCategory(transactions)
    
    calc_service = CalculationService()
    percentages = calc_service.calculatePercentages(category_totals)
    
    return jsonify(percentages)

@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            expense_service = ExpenseService()
            expense_service.load_expenses_from_json()
            
            budget_service = BudgetService()
            active_cycle = budget_service.get_active_cycle(session['user_id'])
            
            expense_service.budget_cycle = active_cycle
            
            expense_service.add_expense(
                user_id=session['user_id'],
                cycle_id=active_cycle.cycle_id if active_cycle else 1,
                amount=amount,
                category_id=request.form["category_id"],
                timestamp=request.form["expense_date"]
            )
            flash("Expense saved successfully!", "success")
            return redirect(url_for('dashboard'))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("add_expense.html")
    return render_template("add_expense.html")

@app.route("/history")
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    budget_service = BudgetService()
    active_cycle = budget_service.get_active_cycle(session['user_id'])
    cycle_id = active_cycle.cycle_id if active_cycle else 1
    
    expense_service = ExpenseService()
    transactionsList = expense_service.getTransactionsByCycleID(cycle_id)
    
    sortedList = expense_service.sortByDateDescending(transactionsList)
    
    return render_template("history.html", transactions=sortedList)

@app.route("/setup", methods=["GET", "POST"])
def setup():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    if request.method == "POST":
        amount = request.form.get("amount", type=float)
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")
        
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            budget_service = BudgetService()
            cycle = budget_service.create_cycle(amount, start_date, end_date, session['user_id'])
            
            calc_service = CalculationService()
            calc_service.set_calculation_strategy(DailyLimitStrategy())
            daily_limit = calc_service.execute_calculation(cycle)
            
            # DB Insert Equivalent
            budget_data = {
                "total_budget": amount,
                "start_date": start_date_str,
                "end_date": end_date_str
            }
            with open(os.path.join(BASE_DIR, "data", "budgets.json"), "w") as f:
                json.dump(budget_data, f, indent=4)
                
            notification_service = NotificationService()
            notification_service.notifyCycleCreated()
            
            flash(f"Budget cycle created successfully! Safe Daily Limit is {daily_limit:.2f} EGP", "success")
            return redirect(url_for('dashboard'))
            
        except ValueError as e:
            flash(str(e), "error")
            return render_template("setup.html")
            
    return render_template("setup.html")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)