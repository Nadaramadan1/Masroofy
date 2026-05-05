from observer import Observer


class NotificationService(Observer):

    def update(self, data):

        if not isinstance(data, dict):
            return

        cycle = data.get("cycle")
        if not cycle:
            return

        allowance = cycle.total_allowance

        if allowance <= 0:
            return

        spent_ratio = 1 - (cycle.remaining_balance / allowance)
        spent_ratio = max(0, spent_ratio)

        print(f"[Notification] Spent ratio: {spent_ratio:.2f}")

        # ALERT
        if spent_ratio >= 1:
            self._send_budget_exceeded()
            return

        # WARNING
        if spent_ratio >= 0.8:
            self._send_warning(spent_ratio)

    # ---------------- internal helpers ----------------

    def _send_warning(self, ratio):
        print(f"WARNING: You have used {ratio * 100:.0f}% of your budget")

    def _send_budget_exceeded(self):
        print("ALERT: Budget exceeded")

    def notifyCycleCreated(self):
        print("[Notification] New budget cycle created successfully.")