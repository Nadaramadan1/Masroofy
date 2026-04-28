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