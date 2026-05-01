# class BudgetService <<control>> {
#  +createCycle(amount: double, startDate: Date, endDate: Date): BudgetCycle
#  +getActiveCycle(userId: int): BudgetCycle
#  +resetCycle(): void
#  +updateCycleBalance(): void
# }

# }
from budget_cycle import BudgetCycle

class BudgetService:
    def __init__(self):
        self.cycles = []

    def create_cycle(self, amount, start_date, end_date, user_id):

        if amount <= 0:
            raise ValueError("Allowance must be positive")

        if end_date <= start_date:
            raise ValueError("End date must be after start date")

        cycle = BudgetCycle(
            cycle_id=len(self.cycles) + 1,
            user_id=user_id,
            total_allowance=amount,
            start_date=start_date,
            end_date=end_date
        )

        cycle.initialize_cycle(amount, start_date, end_date)

        self.cycles.append(cycle)
        return cycle

    def get_active_cycle(self, user_id):
        # Quick file load for JSON persistence compatibility
        import os, json
        from datetime import datetime
        DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "budgets.json")
        try:
            with open(DATA_FILE, "r") as f:
                b = json.load(f)
                if b.get("total_budget"):
                    start = datetime.strptime(b["start_date"], "%Y-%m-%d").date()
                    end = datetime.strptime(b["end_date"], "%Y-%m-%d").date()
                    cycle = BudgetCycle(1, user_id, b["total_budget"], start, end)
                    
                    # Deduct expenses to get correct remaining balance
                    expense_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "expenses.json")
                    if os.path.exists(expense_file):
                        with open(expense_file, "r") as ef:
                            expenses = json.load(ef)
                            spent = sum(e["amount"] for e in expenses)
                            cycle.remaining_balance -= spent
                    return cycle
        except:
            pass

        for cycle in self.cycles:
            if cycle.user_id == user_id and cycle.is_active:
                return cycle
        return None

    def get_dynamic_daily_limit(self, user_id):
        cycle = self.get_active_cycle(user_id)
        if not cycle:
            return None, False
            
        from calculation_service import CalculationService, DailyLimitStrategy
        from datetime import date
        
        calc = CalculationService()
        calc.set_calculation_strategy(DailyLimitStrategy())
        safe_daily_limit = calc.execute_calculation(cycle)
        
        is_final_day = cycle.end_date == date.today()
        
        return safe_daily_limit, is_final_day

    def reset_cycle(self, cycle):
        cycle.reset_cycle()

    def update_cycle_balance(self, cycle, expense_amount):
        cycle.remaining_balance -= expense_amount

        if cycle.remaining_balance <= 0:
            cycle.is_active = False