import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from auth_service import AuthorizationService
from datetime import datetime

from calculation_service import CalculationService, DailyLimitStrategy
from budget_cycle import BudgetCycle
from expense_service import ExpenseService
from budget_service import BudgetService
from notification_service import NotificationService


# =====================================================
# BASE CONFIG
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = os.urandom(24)

auth_service = AuthorizationService()

# =====================================================
# SINGLETON SERVICES (FIXED)
# =====================================================

expense_service = ExpenseService()
budget_service = BudgetService()

calc_service = CalculationService()
calc_service.set_calculation_strategy(DailyLimitStrategy())

notif_service = NotificationService()


# =====================================================
# HELPERS (USER-SAFE DATA)
# =====================================================

def load_budget():
    try:
        with open(os.path.join(BASE_DIR, "data", "budgets.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def load_expenses():
    try:
        with open(os.path.join(BASE_DIR, "data", "expenses.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# =====================================================
# AUTH ROUTES
# =====================================================

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


# =====================================================
# DASHBOARD (FIXED USER FILTERING)
# =====================================================

@app.route("/")
def dashboard():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # =======================
    # LOAD BUDGET (SAFE)
    # =======================
    budgets = load_budget()

    if isinstance(budgets, list):
        budgets = {}

    budget = budgets.get(str(user_id), {})

    # =======================
    # LOAD EXPENSES
    # =======================
    expenses = load_expenses()

    # SAFE TYPE CAST (IMPORTANT FIX)
    user_expenses = [
        e for e in expenses
        if int(e.get("user_id", 0)) == int(user_id)
    ]

    total_spent = sum(float(e.get("amount", 0)) for e in user_expenses)

    total_budget = float(budget.get("total_budget", 0))
    remaining = total_budget - total_spent

    # =======================
    # BUDGET CYCLE
    # =======================
    active_cycle = budget_service.get_active_cycle(user_id)

    safe_daily_limit = 0
    is_positive_rollover = True
    is_final_day = False

    if active_cycle:
        result = budget_service.get_dynamic_daily_limit(user_id)

        if result:
            safe_daily_limit, is_final_day = result

        total_days = max(
            (active_cycle.end_date - active_cycle.start_date).days,
            1
        )

        base_daily_limit = active_cycle.total_allowance / total_days
        is_positive_rollover = safe_daily_limit >= base_daily_limit

    # =======================
    # WARNINGS
    # =======================
    warning_80 = None
    warning_over = None

    if total_budget > 0:
        if total_spent >= 0.8 * total_budget:
            warning_80 = "⚠ You have used 80% of your budget"

        if total_spent >= total_budget:
            warning_over = "❌ Budget Exhausted!"

    return render_template(
        "dashboard.html",
        total_budget=total_budget,
        remaining=remaining,
        start_date=budget.get("start_date", "-"),
        end_date=budget.get("end_date", "-"),
        expenses=user_expenses,
        warning_80=warning_80,
        warning_over=warning_over,
        total_spent=total_spent,
        safe_daily_limit=safe_daily_limit,
        is_positive_rollover=is_positive_rollover,
        is_final_day=is_final_day
    )


# =====================================================
# CHART API (FIXED USER ISOLATION)
# =====================================================

@app.route("/chart-data")
def chart_data_api():

    if 'user_id' not in session:
        return jsonify({})

    user_id = session['user_id']

    transactions = [
        e for e in load_expenses()
        if e["user_id"] == user_id
    ]

    if not transactions:
        return jsonify({})

    category_totals = expense_service.aggregateByCategory(transactions)

    percentages = calc_service.calculatePercentages(category_totals)

    return jsonify(percentages)


# =====================================================
# ADD EXPENSE (FIXED SERVICE USAGE)
# =====================================================

@app.route("/add", methods=["GET", "POST"])
def add_expense():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":

        try:
            amount = float(request.form["amount"])
            user_id = session['user_id']

            # get active cycle for this user
            active_cycle = budget_service.get_active_cycle(user_id)

            # link cycle to expense service (if needed for observer logic)
            expense_service.budget_cycle = active_cycle

            expense_service.add_expense(
                user_id=user_id,
                cycle_id=active_cycle.cycle_id if active_cycle else 1,
                amount=amount,
                category_id=request.form["category_id"],  # ✅ STRING (NO int)
                timestamp=request.form["expense_date"] if request.form.get("expense_date") else None
            )

            flash("Expense saved successfully!", "success")
            return redirect(url_for('dashboard'))

        except ValueError as e:
            flash(str(e), "error")

        except Exception as e:
            flash(f"Unexpected error: {str(e)}", "error")

    return render_template("add_expense.html")
# =====================================================
# HISTORY (FIXED USER SAFE QUERY)
# =====================================================

@app.route("/history")
def history():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    active_cycle = budget_service.get_active_cycle(user_id)
    cycle_id = active_cycle.cycle_id if active_cycle else 1

    transactionsList = expense_service.getTransactionsByCycleID(
        user_id,
        cycle_id
    )

    sortedList = sorted(
        transactionsList,
        key=lambda x: x.get("date", ""),
        reverse=True
    )

    return render_template("history.html", transactions=sortedList)
# =====================================================
# SETUP BUDGET (FIXED GLOBAL OVERWRITE ISSUE)
# =====================================================

@app.route("/setup", methods=["GET", "POST"])
def setup():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == "POST":

        try:
            amount = request.form.get("amount", type=float)
            start_date_str = request.form.get("start_date")
            end_date_str = request.form.get("end_date")

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            cycle = budget_service.create_cycle(
                amount, start_date, end_date, user_id
            )

            daily_limit = calc_service.execute_calculation(cycle)

            notif_service.notifyCycleCreated()

            flash(
                f"Budget created! Daily limit: {daily_limit:.2f}",
                "success"
            )

            return redirect(url_for('dashboard'))

        except ValueError as e:
            flash(str(e), "error")

    return render_template("setup.html")


# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)