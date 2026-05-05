from dataclasses import dataclass, field
from datetime import datetime, timezone


# =======================================================
# Category
# =======================================================
@dataclass
class Category:

    category_id: str
    name: str
    icon: str = ""

    def __post_init__(self) -> None:
        if not self.category_id or not self.category_id.strip():
            raise ValueError("category_id must not be empty.")

        if not self.name or not self.name.strip():
            raise ValueError("Category name must not be empty.")

    def __str__(self) -> str:
        return f"[{self.icon}] {self.name} (id={self.category_id})"

# =======================================================
# Expense
# =======================================================

@dataclass
class Expense:

    expense_id: int
    user_id: int
    cycle_id: int
    amount: float
    category_id: str   # مهم جدًا يفضل str

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:

        if self.expense_id <= 0:
            raise ValueError("expense_id must be positive.")

        if self.user_id <= 0:
            raise ValueError("user_id must be positive.")

        if self.cycle_id <= 0:
            raise ValueError("cycle_id must be positive.")

        if self.amount <= 0:
            raise ValueError("amount must be > 0")

        if not self.category_id or not str(self.category_id).strip():
            raise ValueError("category_id must not be empty.")