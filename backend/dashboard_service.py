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
    def __init__(self, user_id, cycle_id):
        self.user_id = user_id
        self.cycle_id = cycle_id

    def loadDashboardData(self):
        print("Loading dashboard data...")

    def displayDailyLimit(self, daily_limit):
        print(f"Daily Limit: {daily_limit}")

    def displayRemainingBalance(self, remaining_balance):
        print(f"Remaining Balance: {remaining_balance}")

    def showAlerts(self, message):
        print(f"Alert: {message}")
