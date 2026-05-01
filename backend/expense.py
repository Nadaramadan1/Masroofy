"""
models/expense.py
Entities: Category + Expense
Both are kept in one file to match the project's flat models/ structure.
"""

from dataclasses import dataclass, field
from datetime import datetime


# ======================================================================= #
# Category Entity                                                          #
# ======================================================================= #

@dataclass
class Category:
    """
    Entity that classifies expenses into named groups (e.g. Food, Transport).

    Attributes:
        category_id: Unique identifier for this category.
        name:        Human-readable label (e.g. "Groceries").
        icon:        Icon identifier / emoji / path used in the UI.
    """

    category_id: int
    name: str
    icon: str = ""

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Category name must not be empty.")
        if self.category_id <= 0:
            raise ValueError("category_id must be a positive integer.")

    def __str__(self) -> str:
        return f"[{self.icon}] {self.name} (id={self.category_id})"

    def __repr__(self) -> str:
        return (
            f"Category(category_id={self.category_id!r}, "
            f"name={self.name!r}, icon={self.icon!r})"
        )


# ======================================================================= #
# Expense Entity                                                           #
# ======================================================================= #

@dataclass
class Expense:
    """
    Entity that records one spending transaction.

    Attributes:
        expense_id:  Unique identifier for this expense.
        user_id:     ID of the user who made the expense.
        cycle_id:    ID of the budget cycle this expense belongs to.
        amount:      Monetary value of the expense (must be > 0).
        category_id: ID of the category that classifies this expense.
        timestamp:   Date and time the expense was recorded.
                     Defaults to the current UTC time if not provided.
    """

    expense_id: int
    user_id: int
    cycle_id: int
    amount: float
    category_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.expense_id <= 0:
            raise ValueError("expense_id must be a positive integer.")
        if self.user_id <= 0:
            raise ValueError("user_id must be a positive integer.")
        if self.cycle_id <= 0:
            raise ValueError("cycle_id must be a positive integer.")
        if self.amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")
        if not self.category_id:
            raise ValueError("category_id must be provided.")

    def __str__(self) -> str:
        return (
            f"Expense #{self.expense_id} | "
            f"Amount: {self.amount:.2f} | "
            f"Category: {self.category_id} | "
            f"At: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def __repr__(self) -> str:
        return (
            f"Expense(expense_id={self.expense_id!r}, "
            f"user_id={self.user_id!r}, "
            f"cycle_id={self.cycle_id!r}, "
            f"amount={self.amount!r}, "
            f"category_id={self.category_id!r}, "
            f"timestamp={self.timestamp!r})"
        )