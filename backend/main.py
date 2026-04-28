from datetime import date

from expense import Expense
from category import Category
from budget_cycle import BudgetCycle
from expense_service import ExpenseService
from notification_service import NotificationService


if __name__ == "__main__":

    print("\n========== SYSTEM STARTED ==========\n")

    # ================= SERVICE =================
    service = ExpenseService()

    # ================= OBSERVER =================
    notifier = NotificationService()
    service.register_observer(notifier)

    # ================= CATEGORY =================
    food = Category(1, "Food")
    transport = Category(2, "Transport")

    # ================= BUDGET CYCLE =================
    cycle = BudgetCycle(
        cycle_id=1,
        user_id=1,
        total_allowance=1000,
        start_date=date.today(),
        end_date=date(2026, 12, 31)
    )

    service.budget_cycle = cycle

    # ================= ADD EXPENSES =================
    print("\n--- ADD EXPENSES ---")

    e1 = service.add_expense(1, 1, 200, food.category_id)
    e2 = service.add_expense(1, 1, 300, transport.category_id)
    e3 = service.add_expense(1, 1, 250, food.category_id)

    # ================= UPDATE =================
    print("\n--- UPDATE EXPENSE ---")
    service.update_expense(e1.expense_id, 220)

    # ================= DELETE =================
    print("\n--- DELETE EXPENSE ---")
    service.delete_expense(e2.expense_id)

    # ================= FINAL STATE =================
    print("\n========== FINAL STATE ==========")
    print("Remaining:", cycle.remaining_balance)
    print("Active:", cycle.is_active)
    print("Total:", len(service.get_expenses_by_cycle(1)))

    print("\n========== SYSTEM END ==========")