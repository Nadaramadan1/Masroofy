# class BudgetCycle <<entity>> {
#  -cycleId: int
#  -userId: int
#  -totalAllowance: double
#  -startDate: Date
#  -endDate: Date
#  -remainingBalance: double
#  -createdAt: DateTime
#  -isActive: boolean

#  +initializeCycle(amount: double, startDate: Date, endDate: Date): void
#  +getRemainingDays(): int
#  +resetCycle(): void
#  +checkActiveStatus(): boolean
# }
from datetime import date

class BudgetCycle:
    def __init__(self, cycle_id, user_id, total_allowance, start_date, end_date):
        self.cycle_id = cycle_id
        self.user_id = user_id
        self.total_allowance = total_allowance
        self.start_date = start_date
        self.end_date = end_date

        self.remaining_balance = total_allowance
        self.created_at = date.today()
        self.is_active = True

    
    def initialize_cycle(self):
        self.remaining_balance = self.total_allowance
        self.is_active = True

    
    def get_remaining_days(self):
        today = date.today()
        return (self.end_date - today).days

   
    def reset_cycle(self):
        self.remaining_balance = self.total_allowance
        self.is_active = True

  
    def check_active_status(self):
        return self.is_active and self.remaining_balance > 0