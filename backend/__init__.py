"""
backend
=======
Masroofy backend package.

Exposes all service and entity classes used by the Flask application layer.

Modules
-------
user
    :class:`~user.User` entity.
budget_cycle
    :class:`~budget_cycle.BudgetCycle` entity.
expense
    :class:`~expense.Expense` and :class:`~expense.Category` data objects.
auth_service
    :class:`~auth_service.AuthorizationService` and :class:`~auth_service.UserRepository`.
budget_service
    :class:`~budget_service.BudgetService`.
expense_service
    :class:`~expense_service.ExpenseService`.
calculation_service
    :class:`~calculation_service.CalculationService`,
    :class:`~calculation_service.DailyLimitStrategy`,
    :class:`~calculation_service.RemainingBalanceStrategy`.
notification_service
    :class:`~notification_service.NotificationService`.
observer
    :class:`~observer.Observer` and :class:`~observer.Subject` (Observer pattern).
"""
