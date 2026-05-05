from datetime import datetime
from typing import List
from collections import defaultdict

from  expense import Expense
from  observer import Observer


class ExpenseService:

    def __init__(self):
        self._expenses: List[Expense] = []
        self._next_id = 1
        self._observers: List[Observer] = []

        # 🔥 FIX: بدل single cycle → multi-user safe state
        self.active_cycles = {}  # user_id -> cycle

        self.load_expenses_from_json()

    # =====================================================
    # Observers
    # =====================================================

    def register_observer(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        self._observers = [o for o in self._observers if o is not observer]

    def notify_observers(self):
        data = {
            "expenses": list(self._expenses),
        }

        for observer in self._observers:
            observer.update(data)

    # =====================================================
    # ADD EXPENSE
    # =====================================================

    def add_expense(self, user_id: int, cycle_id: int, amount: float, category_id: int, timestamp=None):

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

        # =================================================
        # FIX: safe cycle handling (per user + cycle)
        # =================================================
        cycle = self.active_cycles.get(user_id)

        if cycle and cycle.cycle_id == cycle_id:
            cycle.deduct_expense(amount)

        self.save_expenses_to_json()

        # =================================================
        # CALCULATIONS (FIXED SCOPE)
        # =================================================
        from calculation_service import CalculationService, DailyLimitStrategy

        calc_service = CalculationService()
        calc_service.set_calculation_strategy(DailyLimitStrategy())

        if cycle:
            updated_limit = calc_service.recalculateDailyLimit(cycle)

            total_spent = calc_service.calculateTotalSpending(
                user_id,
                cycle_id
            )

            percentage = calc_service.calculatePercentage(total_spent, cycle)

            from notification_service import NotificationService
            notif_service = NotificationService()

            if percentage >= 100:
                notif_service.send("Budget Exhausted")
            elif percentage >= 80:
                notif_service.send("Warning: 80% used")

        self.notify_observers()
        return new_expense

    # =====================================================
    # QUERIES (FIXED FILTERING)
    # =====================================================

    def get_expenses_by_cycle(self, user_id: int, cycle_id: int):
        return [
            e for e in self._expenses
            if e.user_id == user_id and e.cycle_id == cycle_id
        ]

    def getTransactionsByCycleID(self, user_id: int, cycle_id: int):

        transactionsList = []

        for e in self._expenses:
            if e.user_id == user_id and e.cycle_id == cycle_id:
                transactionsList.append({
                    "amount": e.amount,
                    "category": e.category_id,
                    "date": str(e.timestamp)[:10] if e.timestamp else "",
                    "note": ""
                })

        return transactionsList

    # =====================================================
    # CATEGORY ANALYSIS
    # =====================================================

    def aggregateByCategory(self, transactions):

        category_totals = defaultdict(float)

        for e in transactions:
            if isinstance(e, dict):
                category_totals[e.get("category", "Unknown")] += e.get("amount", 0)
            else:
                category_totals[e.category_id] += e.amount

        return dict(category_totals)

    # =====================================================
    # DELETE SAFE
    # =====================================================

    def delete_expense(self, expense_id: int):

        exp = self._find_by_id(expense_id)

        # revert cycle balance safely
        cycle = self.active_cycles.get(exp.user_id)

        if cycle and cycle.cycle_id == exp.cycle_id:
            cycle.remaining_balance += exp.amount

        self._expenses.remove(exp)

        self.save_expenses_to_json()
        self.notify_observers()

    # =====================================================
    # HELPER
    # =====================================================

    def _find_by_id(self, expense_id: int):
        for e in self._expenses:
            if e.expense_id == expense_id:
                return e
        raise LookupError("Expense not found")

    # =====================================================
    # JSON LOAD
    # =====================================================

    def load_expenses_from_json(self):
        import json, os

        DATA_FILE = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "expenses.json"
        )

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._expenses = []

            for exp in data:
                self._expenses.append(Expense(
                    expense_id=exp.get("expense_id", 0),
                    user_id=exp.get("user_id", 0),
                    cycle_id=exp.get("cycle_id", 0),
                    amount=exp["amount"],
                    category_id=exp.get("category"),
                    timestamp=exp.get("date", datetime.utcnow())
                ))

            self._next_id = (
                max(e.expense_id for e in self._expenses) + 1
                if self._expenses else 1
            )

        except:
            self._expenses = []
            self._next_id = 1

    # =====================================================
    # JSON SAVE
    # =====================================================

    def save_expenses_to_json(self):
        import json, os

        DATA_FILE = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "expenses.json"
        )

        data = [
            {
                "expense_id": e.expense_id,
                "user_id": e.user_id,
                "cycle_id": e.cycle_id,
                "amount": e.amount,
                "category": e.category_id,
                "date": str(e.timestamp)
            }
            for e in self._expenses
        ]

        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def sortByDateDescending(self, transactionsList):
    return sorted(
        transactionsList,
        key=lambda x: x.get("date", ""),
        reverse=True
    )