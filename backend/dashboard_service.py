# class Dashboard <<boundary>> {
#  -userId: int
#  -cycleId: int
#
#  +displayDailyLimit(): void
#  +displayRemainingBalance(): void
#  +loadDashboardData(): void
#  +showAlerts(): void
# }

class Dashboard:
    def __init__(self, user_id, cycle_id, budget_service, calculation_service):
        self.user_id = user_id
        self.cycle_id = cycle_id
        self.budget_service = budget_service
        self.calculation_service = calculation_service

    def loadDashboardData(self):
        cycle = self.budget_service.get_active_cycle(self.user_id)

        if not cycle:
            self.showAlerts("No active budget cycle found")
            return

        self.displayRemainingBalance(cycle.remaining_balance)

        # Daily limit calculation
        from calculation_service import DailyLimitStrategy

        self.calculation_service.set_calculation_strategy(DailyLimitStrategy())
        daily_limit = self.calculation_service.execute_calculation(cycle)

        self.displayDailyLimit(daily_limit)

        # Alerts
        if cycle.remaining_balance <= 0:
            self.showAlerts("You exceeded your budget!")

        elif daily_limit < 100:  # example threshold
            self.showAlerts("Low daily budget warning!")

    def displayDailyLimit(self, daily_limit):
        print(f"Daily Limit: {daily_limit:.2f}")

    def displayRemainingBalance(self, remaining_balance):
        print(f"Remaining Balance: {remaining_balance:.2f}")

    def showAlerts(self, message):
        print(f"Alert: {message}")