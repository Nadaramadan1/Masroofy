from .observer import Observer

class NotificationService(Observer):
    def __init__(self):
        super().__init__()

    def update(self, subject):
        """
        Called when ExpenseService (the subject) notifies its observers.
        """
        # Assuming subject is ExpenseService and has access to BudgetService/Active Cycle
        # or directly provides current spending info.
        if hasattr(subject, 'budget_service'):
            # This is a bit of a reach but follows the pattern
            # In a real system, we'd pass the data in the update or have a better link
            pass

    def check_threshold_total_spent(self, total_spent, allowance):
        """Checks if the spent amount exceeds a threshold (e.g., 80%)."""
        if allowance <= 0:
            return False
        return (total_spent / allowance) >= 0.8

    def send_warning_notification(self):
        print("[NOTIFICATION] WARNING: You have spent over 80% of your budget!")

    def send_budget_exceeded_notification(self):
        print("[NOTIFICATION] ALERT: Budget exceeded!")

    def process_notification_logic(self, cycle):
        """Logic to evaluate and send notifications for a specific cycle."""
        if not cycle:
            return
            
        total_spent = cycle.total_allowance - cycle.remaining_balance
        if cycle.remaining_balance <= 0:
            self.send_budget_exceeded_notification()
        elif self.check_threshold_total_spent(total_spent, cycle.total_allowance):
            self.send_warning_notification()
