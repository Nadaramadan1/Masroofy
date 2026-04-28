"""
services/expense_service.py
Control Layer: ExpenseService
Manages expense CRUD operations and notifies registered observers
whenever the expense list changes (Observer Pattern).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional

from models.expense import Category, Expense          # ✅ fixed import


# ======================================================================= #
# Observer Pattern Interface                                               #
# ======================================================================= #

class Observer(ABC):
    """Abstract base for all observers that listen to ExpenseService events."""

    @abstractmethod
    def update(self, expenses: List[Expense]) -> None:
        """
        Called whenever the expense list changes.

        Args:
            expenses: The current full list of expenses held by the service.
        """


class ExpenseObserver(Observer):
    """
    Concrete observer that reacts to expense changes
    (e.g. refreshing a local cache or a UI widget).
    """

    def update(self, expenses: List[Expense]) -> None:
        total = sum(e.amount for e in expenses)
        print(
            f"[ExpenseObserver] Expense list updated — "
            f"{len(expenses)} record(s), total spent: {total:.2f}"
        )


class NotificationObserver(Observer):
    """
    Concrete observer that forwards the updated expense list
    to the NotificationService for threshold checking.
    Replace the body with a real NotificationService call as needed.
    """

    def update(self, expenses: List[Expense]) -> None:
        total = sum(e.amount for e in expenses)
        print(
            f"[NotificationObserver] Checking spend alert — "
            f"total: {total:.2f}"
        )


# ======================================================================= #
# ExpenseService                                                           #
# ======================================================================= #

class ExpenseService:
    """
    Control class responsible for all expense operations.

    Responsibilities
    ----------------
    * Add, update, and delete expenses.
    * Query expenses by cycle or filtered by category / date range.
    * Notify registered observers after every mutating operation.

    Follows the Observer Pattern: call ``register_observer`` to subscribe
    any object that implements ``Observer``.
    """

    def __init__(self) -> None:
        # In-memory store — replace with a repository / DB session as needed.
        self._expenses: List[Expense] = []
        self._next_id: int = 1
        self._observers: List[Observer] = []

    # ------------------------------------------------------------------ #
    # Observer management                                                  #
    # ------------------------------------------------------------------ #

    def register_observer(self, observer: Observer) -> None:
        """Subscribe an observer to expense-change events."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        """Unsubscribe an observer."""
        self._observers = [o for o in self._observers if o is not observer]

    def notify_observers(self) -> None:
        """Broadcast the current expense list to all registered observers."""
        for observer in self._observers:
            observer.update(list(self._expenses))

    # ------------------------------------------------------------------ #
    # CRUD operations                                                      #
    # ------------------------------------------------------------------ #

    def add_expense(
        self,
        user_id: int,
        cycle_id: int,
        amount: float,
        category_id: int,
        timestamp: Optional[datetime] = None,
    ) -> Expense:
        """
        Create and store a new expense.

        Args:
            user_id:     Owner of the expense.
            cycle_id:    Budget cycle the expense belongs to.
            amount:      Positive monetary value.
            category_id: Category that classifies this expense.
            timestamp:   Defaults to current UTC time when omitted.

        Returns:
            The newly created Expense instance.
        """
        expense = Expense(
            expense_id=self._next_id,
            user_id=user_id,
            cycle_id=cycle_id,
            amount=amount,
            category_id=category_id,
            timestamp=timestamp or datetime.utcnow(),
        )
        self._expenses.append(expense)
        self._next_id += 1
        self.notify_observers()
        return expense

    def update_expense(self, expense_id: int, amount: float) -> None:
        """
        Update the amount of an existing expense.

        Args:
            expense_id: ID of the expense to update.
            amount:     New positive monetary value.

        Raises:
            ValueError:  If amount is not positive.
            LookupError: If no expense with the given ID exists.
        """
        if amount <= 0:
            raise ValueError("Updated amount must be greater than zero.")

        expense = self._find_by_id(expense_id)
        expense.amount = amount
        self.notify_observers()

    def delete_expense(self, expense_id: int) -> None:
        """
        Remove an expense from the store.

        Args:
            expense_id: ID of the expense to remove.

        Raises:
            LookupError: If no expense with the given ID exists.
        """
        expense = self._find_by_id(expense_id)
        self._expenses.remove(expense)
        self.notify_observers()

    # ------------------------------------------------------------------ #
    # Query operations                                                     #
    # ------------------------------------------------------------------ #

    def get_expenses_by_cycle(self, cycle_id: int) -> List[Expense]:
        """
        Return all expenses that belong to the given budget cycle.

        Args:
            cycle_id: The target budget cycle ID.

        Returns:
            List of matching Expense objects (may be empty).
        """
        return [e for e in self._expenses if e.cycle_id == cycle_id]

    def filter_expenses(
        self,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Expense]:
        """
        Return expenses filtered by optional category and/or date range.

        Args:
            category_id: When provided, only expenses in this category
                         are returned.
            start_date:  When provided, only expenses on or after this
                         date are returned.
            end_date:    When provided, only expenses on or before this
                         date are returned.

        Returns:
            Filtered list of Expense objects.
        """
        results = list(self._expenses)

        if category_id is not None:
            results = [e for e in results if e.category_id == category_id]

        if start_date is not None:
            results = [e for e in results if e.timestamp.date() >= start_date]

        if end_date is not None:
            results = [e for e in results if e.timestamp.date() <= end_date]

        return results

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _find_by_id(self, expense_id: int) -> Expense:
        """
        Locate an expense by its ID.

        Raises:
            LookupError: If no expense with the given ID is found.
        """
        for expense in self._expenses:
            if expense.expense_id == expense_id:
                return expense
        raise LookupError(f"No expense found with id={expense_id}.")