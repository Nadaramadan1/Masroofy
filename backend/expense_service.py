"""
expense_service.py
==================
Service layer for managing :class:`~expense.Expense` records in Masroofy.

:class:`ExpenseService` loads expenses from disk on start-up, validates
and records new expenses, and notifies registered :class:`~observer.Observer`
instances after each mutation.
"""

from datetime import datetime
from typing import List
from collections import defaultdict

from expense import Expense
from observer import Observer


class ExpenseService:
    """Manages expense creation, querying, aggregation, and persistence.

    Implements the **Observer** role of a Subject: observers can register
    via :meth:`register_observer` and will be notified after each
    :meth:`add_expense` or :meth:`delete_expense` call.

    Attributes:
        _expenses (list[Expense]): In-memory collection of all expenses.
        _next_id (int): Auto-incremented ID counter for new expenses.
        _observers (list[Observer]): Registered notification observers.
        active_cycles (dict[int, BudgetCycle]): Per-user active cycle map.
    """

    def __init__(self) -> None:
        """Initialise the service and load existing expenses from disk."""
        self._expenses: List[Expense] = []
        self._next_id = 1
        self._observers: List[Observer] = []
        self.active_cycles: dict = {}
        self.load_expenses_from_json()

    # ------------------------------------------------------------------
    # Observer management
    # ------------------------------------------------------------------

    def register_observer(self, observer: Observer) -> None:
        """Register an observer (idempotent).

        Args:
            observer (Observer): Observer to add.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        """Unregister a previously registered observer.

        Args:
            observer (Observer): Observer to remove.
        """
        self._observers = [o for o in self._observers if o is not observer]

    def notify_observers(self) -> None:
        """Broadcast the current expense list to all registered observers."""
        data = {"expenses": list(self._expenses)}
        for observer in self._observers:
            observer.update(data)

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def add_expense(
        self,
        user_id: int,
        cycle_id: int,
        amount: float,
        category_id: str,
        timestamp=None,
    ) -> Expense:
        """Record a new expense, update the cycle balance, and persist.

        Args:
            user_id (int): Owning user's identifier.
            cycle_id (int): Associated budget cycle identifier.
            amount (float): Positive expense amount in EGP.
            category_id (str): Category identifier string.
            timestamp (str | datetime, optional): Transaction timestamp.
                Defaults to ``datetime.utcnow()``.

        Returns:
            Expense: The newly created :class:`~expense.Expense` object.

        Raises:
            ValueError: If ``amount`` ≤ 0.
        """
        if amount <= 0:
            raise ValueError("Invalid amount")

        new_expense = Expense(
            expense_id=self._next_id,
            user_id=user_id,
            cycle_id=cycle_id,
            amount=amount,
            category_id=category_id,
            timestamp=timestamp or datetime.utcnow(),
        )

        self._expenses.append(new_expense)
        self._next_id += 1

        cycle = self.active_cycles.get(user_id)
        if cycle and cycle.cycle_id == cycle_id:
            cycle.deduct_expense(amount)

        self.save_expenses_to_json()
        self.notify_observers()
        return new_expense

    def delete_expense(self, expense_id: int) -> None:
        """Remove an expense by ID and restore the cycle balance.

        Args:
            expense_id (int): Identifier of the expense to delete.

        Raises:
            LookupError: If no expense with ``expense_id`` exists.
        """
        exp = self._find_by_id(expense_id)
        cycle = self.active_cycles.get(exp.user_id)
        if cycle and cycle.cycle_id == exp.cycle_id:
            cycle.remaining_balance += exp.amount

        self._expenses.remove(exp)
        self.save_expenses_to_json()
        self.notify_observers()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_expenses_by_cycle(self, user_id: int, cycle_id: int) -> List[Expense]:
        """Return all expenses for a specific user and cycle.

        Args:
            user_id (int): User to filter by.
            cycle_id (int): Cycle to filter by.

        Returns:
            list[Expense]: Matching expense objects.
        """
        return [
            e for e in self._expenses
            if e.user_id == user_id and e.cycle_id == cycle_id
        ]

    def getTransactionsByCycleID(self, user_id: int, cycle_id: int) -> list:
        """Return serialisable transaction dicts for a user's cycle.

        Args:
            user_id (int): User to filter by.
            cycle_id (int): Cycle to filter by.

        Returns:
            list[dict]: Each dict has keys ``amount``, ``category``,
                ``date``, and ``note``.
        """
        return [
            {
                "amount": e.amount,
                "category": e.category_id,
                "date": str(e.timestamp)[:10] if e.timestamp else "",
                "note": "",
            }
            for e in self._expenses
            if e.user_id == user_id and e.cycle_id == cycle_id
        ]

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def aggregateByCategory(self, transactions: list) -> dict:
        """Sum transaction amounts grouped by category.

        Accepts both :class:`~expense.Expense` objects and plain dicts
        (as returned by :meth:`getTransactionsByCycleID`).

        Args:
            transactions (list): Expenses as objects or dicts.

        Returns:
            dict[str, float]: Mapping of category name/id to total amount.
        """
        category_totals: dict = defaultdict(float)
        for e in transactions:
            if isinstance(e, dict):
                category_totals[e.get("category", "Unknown")] += e.get("amount", 0)
            else:
                category_totals[e.category_id] += e.amount
        return dict(category_totals)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load_expenses_from_json(self) -> None:
        """Populate ``_expenses`` from ``data/expenses.json``.

        Silently resets to an empty list if the file is absent or corrupt.
        """
        import json
        import os

        DATA_FILE = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "expenses.json",
        )
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._expenses = [
                Expense(
                    expense_id=exp.get("expense_id", 0),
                    user_id=exp.get("user_id", 0),
                    cycle_id=exp.get("cycle_id", 0),
                    amount=exp["amount"],
                    category_id=exp.get("category"),
                    timestamp=exp.get("date", datetime.utcnow()),
                )
                for exp in data
            ]
            self._next_id = (
                max(e.expense_id for e in self._expenses) + 1
                if self._expenses else 1
            )
        except Exception:
            self._expenses = []
            self._next_id = 1

    def save_expenses_to_json(self) -> None:
        """Serialise all in-memory expenses to ``data/expenses.json``."""
        import json
        import os

        DATA_FILE = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "expenses.json",
        )
        data = [
            {
                "expense_id": e.expense_id,
                "user_id": e.user_id,
                "cycle_id": e.cycle_id,
                "amount": e.amount,
                "category": e.category_id,
                "date": str(e.timestamp),
            }
            for e in self._expenses
        ]
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_by_id(self, expense_id: int) -> Expense:
        """Locate an expense by its ID.

        Args:
            expense_id (int): The identifier to search for.

        Returns:
            Expense: The matching expense object.

        Raises:
            LookupError: If no expense with the given ID exists.
        """
        for e in self._expenses:
            if e.expense_id == expense_id:
                return e
        raise LookupError("Expense not found")

    def sortByDateDescending(self, transactionsList: list) -> list:
        """Sort a list of transaction dicts by date, newest first.

        Args:
            transactionsList (list[dict]): Transactions with a ``"date"`` key.

        Returns:
            list[dict]: Sorted copy of the list (descending by date string).
        """
        return sorted(transactionsList, key=lambda x: x.get("date", ""), reverse=True)
