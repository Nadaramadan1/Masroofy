# class BudgetService <<control>> {
#  +createCycle(amount: double, startDate: Date, endDate: Date): BudgetCycle
#  +getActiveCycle(userId: int): BudgetCycle
#  +resetCycle(): void
#  +updateCycleBalance(): void
# }

# }
"""
budget_service.py
=================
Control-layer service for managing :class:`~budget_cycle.BudgetCycle`
objects in the Masroofy application.

:class:`BudgetService` creates, retrieves, and updates budget cycles,
persisting them to ``data/budgets.json``.
"""

from budget_cycle import BudgetCycle
import os
import json
from datetime import datetime, date


class BudgetService:
    """Control class responsible for budget-cycle lifecycle management.

    Provides operations to create new cycles, retrieve the active cycle
    for a user, calculate daily spending limits, and update balances.

    Attributes:
        cycles (list[BudgetCycle]): In-memory list of cycles created
            during the current application session.
        data_file (str): Absolute path to ``budgets.json``.
        expense_file (str): Absolute path to ``expenses.json``.
    """

    def __init__(self) -> None:
        """Initialise the service and resolve data-file paths."""
        self.cycles: list = []
        self.data_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "budgets.json",
        )
        self.expense_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "expenses.json",
        )

    def create_cycle(
        self,
        amount: float,
        start_date: date,
        end_date: date,
        user_id: int,
    ) -> BudgetCycle:
        """Create a new budget cycle for a user and persist it.

        Args:
            amount (float): Total allowance in EGP (must be > 0).
            start_date (date): Cycle start date.
            end_date (date): Cycle end date (must be after start_date).
            user_id (int): Owner's user identifier.

        Returns:
            BudgetCycle: The newly created and persisted cycle.

        Raises:
            ValueError: If ``amount`` ≤ 0 or ``end_date`` ≤ ``start_date``.
        """
        if amount <= 0:
            raise ValueError("Allowance must be positive")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")

        try:
            with open(self.data_file, "r") as f:
                budgets = json.load(f)
        except Exception:
            budgets = {}

        if isinstance(budgets, list):
            budgets = {}

        new_cycle_id = len(self.cycles) + 1
        cycle = BudgetCycle(new_cycle_id, user_id, amount, start_date, end_date)
        cycle.initialize_cycle(amount, start_date, end_date)

        budgets[str(user_id)] = {
            "cycle_id": new_cycle_id,
            "user_id": user_id,
            "total_budget": amount,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }

        with open(self.data_file, "w") as f:
            json.dump(budgets, f, indent=4)

        self.cycles.append(cycle)
        return cycle

    def get_active_cycle(self, user_id: int):
        """Load and return the active budget cycle for a user.

        Reads ``budgets.json`` to find the user's cycle, then deducts
        all matching expenses from ``expenses.json`` to produce an
        accurate remaining balance.

        Args:
            user_id (int): The user whose cycle to retrieve.

        Returns:
            BudgetCycle | None: The active cycle with updated balance,
                or ``None`` if no cycle is found for the user.
        """
        try:
            with open(self.data_file, "r") as f:
                budgets = json.load(f)
        except Exception:
            budgets = {}

        if isinstance(budgets, list):
            budgets = {}

        b = budgets.get(str(user_id))
        if not b:
            return None

        start = datetime.strptime(b["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(b["end_date"], "%Y-%m-%d").date()
        cycle = BudgetCycle(b["cycle_id"], user_id, b["total_budget"], start, end)

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
        except Exception:
            pass

        return cycle

    def get_dynamic_daily_limit(self, user_id: int):
        """Calculate the current safe daily spending limit.

        Args:
            user_id (int): The user to calculate for.

        Returns:
            tuple[float, bool] | tuple[None, bool]: ``(daily_limit, is_final_day)``
                where ``is_final_day`` is ``True`` when today equals the
                cycle's end date.  Returns ``(None, False)`` if no active
                cycle exists.
        """
        cycle = self.get_active_cycle(user_id)
        if not cycle:
            return None, False

        from calculation_service import CalculationService, DailyLimitStrategy

        calc = CalculationService()
        calc.set_calculation_strategy(DailyLimitStrategy())
        safe_daily_limit = calc.execute_calculation(cycle)
        is_final_day = cycle.end_date == date.today()
        return safe_daily_limit, is_final_day

    def reset_cycle(self, cycle: BudgetCycle) -> None:
        """Delegate a cycle reset to :meth:`~budget_cycle.BudgetCycle.reset_cycle`.

        Args:
            cycle (BudgetCycle): The cycle to reset.
        """
        cycle.reset_cycle()

    def update_cycle_balance(self, cycle: BudgetCycle, expense_amount: float) -> None:
        """Deduct an expense from the cycle's remaining balance.

        Clamps the balance to zero and deactivates the cycle if it
        reaches zero.

        Args:
            cycle (BudgetCycle): The cycle to update.
            expense_amount (float): Amount to deduct in EGP.
        """
        cycle.remaining_balance -= expense_amount
        if cycle.remaining_balance <= 0:
            cycle.remaining_balance = 0
            cycle.is_active = False
