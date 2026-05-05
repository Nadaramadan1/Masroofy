"""
notification_service.py
=======================
Provides the :class:`NotificationService` — a concrete :class:`~observer.Observer`
that sends budget alerts when spending thresholds are crossed.
"""

from observer import Observer


class NotificationService(Observer):
    """Concrete observer that monitors spending and emits budget alerts.

    :class:`NotificationService` implements the :class:`~observer.Observer`
    interface.  When attached to an :class:`~observer.Subject`, it receives
    ``data`` payloads and checks spending ratios to decide whether to
    issue warnings or exceeded-budget alerts.

    Example:
        >>> svc = NotificationService()
        >>> svc.notifyCycleCreated()
        [Notification] New budget cycle created successfully.
    """

    def update(self, data: dict) -> None:
        """Handle a spending-update notification from a Subject.

        Calculates the ratio of spent-to-allowance and delegates to
        :meth:`_send_warning` or :meth:`_send_budget_exceeded` as
        appropriate.

        Args:
            data (dict): Expected to contain a ``"cycle"`` key whose value
                is a :class:`~budget_cycle.BudgetCycle` instance.  No-op
                if the key is absent or the cycle is invalid.
        """
        if not isinstance(data, dict):
            return

        cycle = data.get("cycle")
        if not cycle:
            return

        allowance = cycle.total_allowance
        if allowance <= 0:
            return

        spent_ratio = max(0, 1 - (cycle.remaining_balance / allowance))

        if spent_ratio >= 1:
            self._send_budget_exceeded()
            return

        if spent_ratio >= 0.8:
            self._send_warning(spent_ratio)

    def _send_warning(self, ratio: float) -> None:
        """Emit an 80 % threshold warning.

        Args:
            ratio (float): Current spent-to-allowance ratio (0–1).
        """
        print(f"WARNING: You have used {ratio * 100:.0f}% of your budget")

    def _send_budget_exceeded(self) -> None:
        """Emit a budget-exceeded alert."""
        print("ALERT: Budget exceeded")

    def notifyCycleCreated(self) -> None:
        """Log a confirmation that a new budget cycle was created."""
        print("[Notification] New budget cycle created successfully.")
