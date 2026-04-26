from datetime import date
from .budget_service import BudgetService
from .budget_cycle import BudgetCycle

service = BudgetService()

cycle = service.create_cycle(
    amount=5000,
    start_date=date.today(),
    end_date=date.today(),
    user_id=1
)

print(cycle.remaining_balance)