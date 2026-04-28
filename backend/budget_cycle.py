from datetime import date


class BudgetCycle:

    def __init__(self, cycle_id, user_id, total_allowance, start_date, end_date):

        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise TypeError("Dates must be datetime.date")

        self.cycle_id = cycle_id
        self.user_id = user_id
        self.total_allowance = float(total_allowance)
        self.start_date = start_date
        self.end_date = end_date

        self.remaining_balance = float(total_allowance)
        self.created_at = date.today()
        self.is_active = True

    def initialize_cycle(self, amount, start_date, end_date):
        if amount <= 0:
            raise ValueError("Allowance must be greater than 0")

        if end_date < start_date:
            raise ValueError("End date must be after start date")

        self.total_allowance = float(amount)
        self.start_date = start_date
        self.end_date = end_date
        self.remaining_balance = float(amount)

        self.update_status()

    def get_remaining_days(self):
        return max((self.end_date - date.today()).days, 0)

    def reset_cycle(self):
        self.remaining_balance = self.total_allowance
        self.is_active = True

    def deduct_expense(self, amount):
        if amount <= 0:
            raise ValueError("Expense must be greater than 0")

        self.remaining_balance -= amount

        if self.remaining_balance <= 0:
            self.remaining_balance = 0

        self.update_status()

    def update_status(self):
        if self.remaining_balance <= 0 or date.today() > self.end_date:
            self.is_active = False
        else:
            self.is_active = True