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
    """
    Boundary class responsible for displaying budget dashboard data
    for the user, including balance, daily limit, and alerts.
    """

    def __init__(self, user_id: int, cycle_id: int, budget_service, calculation_service):
        """
        Initialize Dashboard with required services.

        Args:
            user_id (int): ID of the user.
            cycle_id (int): Active budget cycle ID.
            budget_service: Service responsible for budget data.
            calculation_service: Service responsible for calculations.
        """
        self.user_id = user_id
        self.cycle_id = cycle_id
        self.budget_service = budget_service
        self.calculation_service = calculation_service

    def load_dashboard_data(self) -> None:
        """
        Load and display all dashboard information:
        - Remaining balance
        - Daily budget limit
        - Alerts if needed
        """
        cycle = self.budget_service.get_active_cycle(self.user_id)

        if not cycle:
            self.show_alerts("No active budget cycle found")
            return

        self.display_remaining_balance(cycle.remaining_balance)

        from calculation_service import DailyLimitStrategy
        self.calculation_service.set_calculation_strategy(DailyLimitStrategy())

        daily_limit = self.calculation_service.execute_calculation(cycle)

        self.display_daily_limit(daily_limit)

        if cycle.remaining_balance <= 0:
            self.show_alerts("You exceeded your budget!")
        elif daily_limit < 100:
            self.show_alerts("Low daily budget warning!")

    def display_daily_limit(self, daily_limit: float) -> None:
        """Display calculated daily limit."""
        print(f"Daily Limit: {daily_limit:.2f}")

    def display_remaining_balance(self, remaining_balance: float) -> None:
        """Display current remaining budget balance."""
        print(f"Remaining Balance: {remaining_balance:.2f}")

    def show_alerts(self, message: str) -> None:
        """Display alert messages to the user."""
        print(f"Alert: {message}")