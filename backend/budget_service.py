# class BudgetService <<control>> {
#  +createCycle(amount: double, startDate: Date, endDate: Date): BudgetCycle
#  +getActiveCycle(userId: int): BudgetCycle
#  +resetCycle(): void
#  +updateCycleBalance(): void
# }

# }
from budget_cycle import BudgetCycle
import os
import json
from datetime import datetime, date


class BudgetService:
    def __init__(self):
        self.cycles = []

        self.data_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "budgets.json"
        )

        self.expense_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "expenses.json"
        )

    # =================================================
    # CREATE CYCLE (FIXED - NO LIST/DICT CONFUSION)
    # =================================================
    def create_cycle(self, amount, start_date, end_date, user_id):

        if amount <= 0:
            raise ValueError("Allowance must be positive")

        if end_date <= start_date:
            raise ValueError("End date must be after start date")

        # ---------------- LOAD JSON SAFELY ----------------
        try:
            with open(self.data_file, "r") as f:
                budgets = json.load(f)
        except:
            budgets = {}

        if isinstance(budgets, list):
            budgets = {}

        # ---------------- CREATE CYCLE ----------------
        new_cycle_id = len(self.cycles) + 1

        cycle = BudgetCycle(
            cycle_id=new_cycle_id,
            user_id=user_id,
            total_allowance=amount,
            start_date=start_date,
            end_date=end_date
        )

        cycle.initialize_cycle(amount, start_date, end_date)

        # ---------------- SAVE PER USER ----------------
        budgets[str(user_id)] = {
            "cycle_id": new_cycle_id,
            "user_id": user_id,
            "total_budget": amount,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

        with open(self.data_file, "w") as f:
            json.dump(budgets, f, indent=4)

        self.cycles.append(cycle)
        return cycle

    # =================================================
    # GET ACTIVE CYCLE (FIXED SAFE PARSING)
    # =================================================
    def get_active_cycle(self, user_id):

        try:
            with open(self.data_file, "r") as f:
                budgets = json.load(f)
        except:
            budgets = {}

        if isinstance(budgets, list):
            budgets = {}

        b = budgets.get(str(user_id))

        if not b:
            return None

        start = datetime.strptime(b["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(b["end_date"], "%Y-%m-%d").date()

        cycle = BudgetCycle(
            b["cycle_id"],
            user_id,
            b["total_budget"],
            start,
            end
        )

        # ---------------- CALCULATE USER EXPENSES ONLY ----------------
        try:
            if os.path.exists(self.expense_file):
                with open(self.expense_file, "r") as ef:
                    expenses = json.load(ef)

                    spent = sum(
                        e["amount"]
                        for e in expenses
                        if int(e.get("user_id", 0)) == int(user_id)
                        and e.get("cycle_id") == b["cycle_id"]
                    )

                    cycle.remaining_balance -= spent
        except:
            pass

        return cycle

    # =================================================
    # DAILY LIMIT
    # =================================================
    def get_dynamic_daily_limit(self, user_id):

        cycle = self.get_active_cycle(user_id)

        if not cycle:
            return None, False

        from calculation_service import CalculationService, DailyLimitStrategy

        calc = CalculationService()
        calc.set_calculation_strategy(DailyLimitStrategy())

        safe_daily_limit = calc.execute_calculation(cycle)

        is_final_day = cycle.end_date == date.today()

        return safe_daily_limit, is_final_day

    # =================================================
    # RESET
    # =================================================
    def reset_cycle(self, cycle):
        cycle.reset_cycle()

    # =================================================
    # UPDATE BALANCE
    # =================================================
    def update_cycle_balance(self, cycle, expense_amount):

        cycle.remaining_balance -= expense_amount

        if cycle.remaining_balance <= 0:
            cycle.remaining_balance = 0
            cycle.is_active = False