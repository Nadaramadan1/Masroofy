from observer import Observer


class NotificationService(Observer):

    def update(self, data):

        if not isinstance(data, dict):
            return

        cycle = data.get("cycle")
        if cycle is None:
            return

        allowance = cycle.total_allowance

        if allowance <= 0:
            return

        spent_ratio = (allowance - cycle.remaining_balance) / allowance

        print(f"[Notification] Spent ratio: {spent_ratio:.2f}")

        # ALERT
        if spent_ratio >= 1:
            self.send_budget_exceeded_notification()
            return

        # WARNING
        if spent_ratio >= 0.8:
            self.send_warning_notification(spent_ratio)

    def send_warning_notification(self, ratio):
        print(f"WARNING: You have used {ratio * 100:.0f}% of your budget")

    def send_budget_exceeded_notification(self):
        print("ALERT: Budget exceeded")