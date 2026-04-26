# class BudgetService <<control>> {
#  +createCycle(amount: double, startDate: Date, endDate: Date): BudgetCycle
#  +getActiveCycle(userId: int): BudgetCycle
#  +resetCycle(): void
#  +updateCycleBalance(): void
# }

# }
from .budget_cycle import BudgetCycle

class BudgetService:
    def __init__(self):
        self.cycles = []

    def create_cycle(self, amount, start_date, end_date, user_id):
        cycle = BudgetCycle(
            cycle_id=len(self.cycles) + 1,
            user_id=user_id,
            total_allowance=amount,
            start_date=start_date,
            end_date=end_date
        )
        cycle.initialize_cycle()
        self.cycles.append(cycle)

        return cycle

    def get_active_cycle(self, user_id):
        for cycle in self.cycles:
            if cycle.user_id == user_id and cycle.is_active:
                return cycle
        return None

    def reset_cycle(self, cycle):
        cycle.reset_cycle()

    def update_cycle_balance(self, cycle, expense_amount):
        cycle.remaining_balance -= expense_amount

        if cycle.remaining_balance <= 0:
            cycle.is_active = False