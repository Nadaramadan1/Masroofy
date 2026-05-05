"""
calculation_service.py
======================
Provides the **Strategy** pattern for budget calculations in Masroofy.

Three public symbols are exported:

* :class:`DailyLimitStrategy` — calculates a safe daily spending limit.
* :class:`RemainingBalanceStrategy` — returns the raw remaining balance.
* :class:`CalculationService` — context class that delegates to a strategy.
"""

from abc import ABC, abstractmethod
from datetime import date
import os
import json


class CalculationStrategy(ABC):
    """Abstract base class for budget calculation strategies.

    Concrete subclasses implement :meth:`calculate` with a specific
    algorithm.  The context (:class:`CalculationService`) calls
    :meth:`calculate` without knowing which strategy is active.
    """

    @abstractmethod
    def calculate(self, budget_cycle) -> float:
        """Execute the strategy's calculation.

        Args:
            budget_cycle (BudgetCycle): The active cycle to calculate for.

        Returns:
            float: The computed result (semantics depend on the strategy).
        """


class DailyLimitStrategy(CalculationStrategy):
    """Strategy that distributes the remaining balance over remaining days.

    Formula::

        daily_limit = remaining_balance / remaining_days

    If the cycle is inactive or there are no remaining days, the full
    remaining balance is returned unchanged.

    Example:
        >>> strategy = DailyLimitStrategy()
        >>> strategy.calculate(some_active_cycle)
        250.0
    """

    def calculate(self, budget_cycle) -> float:
        """Compute the safe daily spending limit.

        Args:
            budget_cycle (BudgetCycle): Must have ``is_active``,
                ``end_date``, and ``remaining_balance`` attributes.

        Returns:
            float: EGP per day, or the full remaining balance when
                fewer than one day remains.
        """
        if not budget_cycle or not budget_cycle.is_active:
            return 0.0

        remaining_days = (budget_cycle.end_date - date.today()).days
        if remaining_days <= 0:
            return budget_cycle.remaining_balance

        return budget_cycle.remaining_balance / remaining_days


class RemainingBalanceStrategy(CalculationStrategy):
    """Strategy that simply returns the cycle's current remaining balance.

    Useful when the caller needs a strategy-compatible wrapper around a
    plain balance lookup.
    """

    def calculate(self, budget_cycle) -> float:
        """Return the remaining balance of the cycle.

        Args:
            budget_cycle (BudgetCycle | None): The cycle to inspect.

        Returns:
            float: Remaining balance, or ``0.0`` if ``budget_cycle`` is
                ``None``.
        """
        if not budget_cycle:
            return 0.0
        return budget_cycle.remaining_balance


class CalculationService:
    """Context class that delegates calculations to a :class:`CalculationStrategy`.

    Call :meth:`set_calculation_strategy` to choose an algorithm, then
    :meth:`execute_calculation` to run it.

    Attributes:
        strategy (CalculationStrategy | None): The currently active strategy.

    Example:
        >>> svc = CalculationService()
        >>> svc.set_calculation_strategy(DailyLimitStrategy())
        >>> svc.execute_calculation(cycle)
        175.0
    """

    def __init__(self) -> None:
        """Initialise with no strategy selected."""
        self.strategy: CalculationStrategy | None = None

    def set_calculation_strategy(self, strategy: CalculationStrategy) -> None:
        """Replace the active calculation strategy.

        Args:
            strategy (CalculationStrategy): New strategy to use.
        """
        self.strategy = strategy

    def execute_calculation(self, budget_cycle) -> float:
        """Run the active strategy against ``budget_cycle``.

        Args:
            budget_cycle (BudgetCycle): Cycle to calculate for.

        Returns:
            float: Result produced by the active strategy.

        Raises:
            ValueError: If no strategy has been set yet.
        """
        if self.strategy is None:
            raise ValueError("Strategy not set")
        return self.strategy.calculate(budget_cycle)

    def recalculateDailyLimit(self, budget_cycle) -> float:
        """Convenience wrapper — delegates to :meth:`execute_calculation`.

        Args:
            budget_cycle (BudgetCycle): The active cycle.

        Returns:
            float: Updated daily limit in EGP.
        """
        return self.execute_calculation(budget_cycle)

    def calculatePercentages(self, category_totals: dict) -> dict:
        """Convert absolute category totals to percentage shares.

        Args:
            category_totals (dict[str, float]): Mapping of category name
                to total amount spent.

        Returns:
            dict[str, float]: Same keys with values as rounded percentages
                (0–100).  Returns ``{}`` when total spending is zero.
        """
        total_spent = sum(category_totals.values())
        if total_spent == 0:
            return {}
        return {
            cat: round((val / total_spent) * 100, 2)
            for cat, val in category_totals.items()
        }

    def calculateTotalSpending(self, user_id: int, cycle_id: int) -> float:
        """Sum all expenses for a given user and cycle from persistent storage.

        Args:
            user_id (int): The user whose expenses to sum.
            cycle_id (int): The cycle to filter by.

        Returns:
            float: Total amount spent, or ``0.0`` on any read error.
        """
        DATA_FILE = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "expenses.json",
        )
        try:
            with open(DATA_FILE, "r") as f:
                expenses = json.load(f)
            return sum(
                e["amount"]
                for e in expenses
                if e["user_id"] == user_id and e["cycle_id"] == cycle_id
            )
        except Exception:
            return 0.0

    def calculatePercentage(self, total_spent: float, budget_cycle) -> float:
        """Calculate what percentage of the allowance has been spent.

        Args:
            total_spent (float): Amount spent so far.
            budget_cycle (BudgetCycle | None): Provides the total allowance.

        Returns:
            float: Percentage (0–100+).  Returns ``0.0`` if the cycle is
                ``None`` or its allowance is zero.
        """
        if not budget_cycle or budget_cycle.total_allowance == 0:
            return 0.0
        return (total_spent / budget_cycle.total_allowance) * 100
