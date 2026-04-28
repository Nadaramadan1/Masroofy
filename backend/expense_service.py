"""
services/expense_service.py
Control Layer: ExpenseService
Observer Pattern implementation for expense tracking system
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from expense import Expense


# =========================================================
# Observer Interface
# =========================================================

class Observer(ABC):

    @abstractmethod
    def update(self, data) -> None:
        pass


# =========================================================
# Observers
# =========================================================

class ExpenseObserver(Observer):

    def update(self, data) -> None:
        expenses = data.get("expenses", [])
        total = sum(e.amount for e in expenses)

        print(
            f"[ExpenseObserver] Expense list updated — "
            f"{len(expenses)} record(s), total spent: {total:.2f}"
        )


class NotificationObserver(Observer):

    def update(self, data) -> None:
        expenses = data.get("expenses", [])
        cycle = data.get("cycle")

        total_spent = sum(e.amount for e in expenses)

        print(
            f"[NotificationObserver] Checking spend alert — total: {total_spent:.2f}"
        )

        if not cycle:
            return

        allowance = cycle.total_allowance

        if allowance <= 0:
            return

        if total_spent >= allowance:
            print("[NOTIFICATION] ALERT: Budget exceeded!")
        elif total_spent >= 0.8 * allowance:
            print("[NOTIFICATION] WARNING: You have spent over 80% of your budget!")


# =========================================================
# Expense Service
# =========================================================

class ExpenseService:

    def __init__(self):
        self._expenses: List[Expense] = []
        self._next_id = 1
        self._observers: List[Observer] = []
        self.budget_cycle = None

    # ---------------- Observers ----------------

    def register_observer(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        self._observers = [o for o in self._observers if o is not observer]

    def notify_observers(self):
        data = {
            "expenses": list(self._expenses),
            "cycle": self.budget_cycle
        }

        for observer in self._observers:
            observer.update(data)

    # ---------------- CRUD ----------------

    def add_expense(self, user_id: int, cycle_id: int, amount: float, category_id: int, timestamp=None):

        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

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

        #  UPDATE BUDGET CYCLE
        if self.budget_cycle:
            self.budget_cycle.deduct_expense(amount)

        self.notify_observers()

        return new_expense

    def update_expense(self, expense_id: int, amount: float):

        if amount <= 0:
            raise ValueError("Amount must be positive")

        exp = self._find_by_id(expense_id)
        exp.amount = amount

        self.notify_observers()

    def delete_expense(self, expense_id: int):

        exp = self._find_by_id(expense_id)
        self._expenses.remove(exp)

        self.notify_observers()

    # ---------------- Queries ----------------

    def get_expenses_by_cycle(self, cycle_id: int):
        return [e for e in self._expenses if e.cycle_id == cycle_id]

    # ---------------- Helper ----------------

    def _find_by_id(self, expense_id: int):
        for e in self._expenses:
            if e.expense_id == expense_id:
                return e
        raise LookupError("Expense not found")