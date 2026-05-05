"""
budget_cycle.py
===============
Defines the :class:`BudgetCycle` entity for the Masroofy application.

A budget cycle represents a user-defined spending period with a fixed
allowance.  The cycle tracks remaining balance and automatically
deactivates when the budget is exhausted or the end date has passed.
"""

from datetime import date


class BudgetCycle:
    """Represents a single spending period (cycle) for a user.

    A :class:`BudgetCycle` is created with a total allowance and a
    date range.  As expenses are recorded, the remaining balance is
    reduced via :meth:`deduct_expense`.  The cycle deactivates
    automatically when the balance reaches zero or the end date passes.

    Attributes:
        cycle_id (int): Unique identifier for this cycle.
        user_id (int): The owner's user identifier.
        total_allowance (float): Original budget amount in EGP.
        start_date (date): First day of the cycle.
        end_date (date): Last day of the cycle.
        remaining_balance (float): Current unspent balance.
        created_at (date): Date the object was instantiated.
        is_active (bool): ``True`` while balance > 0 and today ≤ end_date.

    Example:
        >>> from datetime import date
        >>> cycle = BudgetCycle(1, 42, 3000, date(2025, 6, 1), date(2025, 6, 30))
        >>> cycle.deduct_expense(500)
        >>> cycle.remaining_balance
        2500.0
    """

    def __init__(
        self,
        cycle_id: int,
        user_id: int,
        total_allowance: float,
        start_date: date,
        end_date: date,
    ) -> None:
        """Create and immediately validate a new BudgetCycle.

        Args:
            cycle_id (int): Unique cycle identifier.
            user_id (int): Owner's user identifier.
            total_allowance (float): Total spending allowance in EGP.
            start_date (date): Cycle start date.
            end_date (date): Cycle end date (must be after start_date).

        Raises:
            TypeError: If ``start_date`` or ``end_date`` is not a
                :class:`datetime.date` instance.
        """
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise TypeError("Dates must be datetime.date")

        self.cycle_id = cycle_id
        self.user_id = user_id
        self.total_allowance = float(total_allowance)
        self.start_date = start_date
        self.end_date = end_date
        self.remaining_balance = float(total_allowance)
        self.created_at = date.today()
        self.is_active = True
        self.update_status()

    def initialize_cycle(self, amount: float, start_date: date, end_date: date) -> None:
        """Re-initialise the cycle with new parameters.

        Args:
            amount (float): New total allowance (must be > 0).
            start_date (date): New start date.
            end_date (date): New end date (must be after start_date).

        Raises:
            ValueError: If ``amount`` ≤ 0 or ``end_date`` ≤ ``start_date``.
        """
        if amount <= 0:
            raise ValueError("Allowance must be greater than 0")
        if end_date <= start_date:
            raise ValueError("End date must be after start date")

        self.total_allowance = float(amount)
        self.start_date = start_date
        self.end_date = end_date
        self.remaining_balance = float(amount)
        self.update_status()

    def get_remaining_days(self) -> int:
        """Return the number of days left in the cycle.

        Returns:
            int: Days remaining (minimum 0 — never negative).
        """
        return max((self.end_date - date.today()).days, 0)

    def reset_cycle(self) -> None:
        """Restore the remaining balance to the original allowance.

        The ``is_active`` flag is refreshed via :meth:`update_status`
        rather than being forced to ``True``.
        """
        self.remaining_balance = self.total_allowance
        self.update_status()

    def deduct_expense(self, amount: float) -> None:
        """Subtract an expense amount from the remaining balance.

        The balance is clamped to zero; it will never go negative.
        :meth:`update_status` is called after deduction.

        Args:
            amount (float): Positive expense value in EGP.

        Raises:
            ValueError: If ``amount`` ≤ 0.
        """
        if amount <= 0:
            raise ValueError("Expense must be greater than 0")
        self.remaining_balance = max(self.remaining_balance - amount, 0)
        self.update_status()

    def update_status(self) -> None:
        """Sync ``is_active`` with the current balance and date.

        Sets ``is_active`` to ``False`` if the remaining balance is zero
        or today's date is past ``end_date``; otherwise ``True``.
        """
        if self.remaining_balance <= 0 or date.today() > self.end_date:
            self.is_active = False
        else:
            self.is_active = True
