from abc import ABC, abstractmethod
from datetime import date

class CalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, budget_cycle):
        pass


class DailyLimitStrategy(CalculationStrategy):
    def calculate(self, budget_cycle):

        if not budget_cycle or not budget_cycle.is_active:
            return 0.0

        remaining_days = (budget_cycle.end_date - date.today()).days

        if remaining_days <= 0:
            return budget_cycle.remaining_balance

        return budget_cycle.remaining_balance / remaining_days


class RemainingBalanceStrategy(CalculationStrategy):
    def calculate(self, budget_cycle):
        if not budget_cycle:
            return 0.0
        return budget_cycle.remaining_balance


class CalculationService:
    def __init__(self):
        self.strategy = None

    def set_calculation_strategy(self, strategy: CalculationStrategy):
        self.strategy = strategy

    def execute_calculation(self, budget_cycle):
        if self.strategy is None:
            raise ValueError("Strategy not set")

        return self.strategy.calculate(budget_cycle)

    def recalculateDailyLimit(self, budget_cycle):
        return self.execute_calculation(budget_cycle)

    def calculatePercentages(self, category_totals):
        total_spent = sum(category_totals.values())
        if total_spent == 0: 
            return {}
        return {cat: round((val / total_spent) * 100, 2) for cat, val in category_totals.items()}

    def calculateTotalSpending(self, user_id):
        import os, json
        # Mimic DB SELECT expenses
        DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "expenses.json")
        try:
            with open(DATA_FILE, "r") as f:
                expenses = json.load(f)
                return sum(e["amount"] for e in expenses if e["user_id"] == user_id)
        except:
            return 0.0

    def calculatePercentage(self, total_spent, budget_cycle):
        if not budget_cycle or budget_cycle.total_allowance == 0:
            return 0.0
        return (total_spent / budget_cycle.total_allowance) * 100