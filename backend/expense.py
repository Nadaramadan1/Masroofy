"""
expense.py
==========
Defines the :class:`Category` and :class:`Expense` data-transfer objects
used throughout the Masroofy backend.

Both classes are implemented as frozen-style dataclasses with
``__post_init__`` validation so invalid objects can never be constructed.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Category:
    """Represents a spending category (e.g., Food, Transport).

    Attributes:
        category_id (str): Non-empty unique identifier string.
        name (str): Human-readable category label.
        icon (str): Emoji or icon string displayed in the UI (optional).

    Example:
        >>> cat = Category("food", "Food", "🍔")
        >>> str(cat)
        '[🍔] Food (id=food)'
    """

    category_id: str
    name: str
    icon: str = ""

    def __post_init__(self) -> None:
        """Validate that ``category_id`` and ``name`` are non-empty.

        Raises:
            ValueError: If ``category_id`` or ``name`` is blank.
        """
        if not self.category_id or not self.category_id.strip():
            raise ValueError("category_id must not be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("Category name must not be empty.")

    def __str__(self) -> str:
        """Return a display-friendly string.

        Returns:
            str: ``"[<icon>] <name> (id=<category_id>)"``
        """
        return f"[{self.icon}] {self.name} (id={self.category_id})"


@dataclass
class Expense:
    """Represents a single recorded expense transaction.

    Attributes:
        expense_id (int): Positive unique identifier.
        user_id (int): Positive identifier of the owning user.
        cycle_id (int): Positive identifier of the associated budget cycle.
        amount (float): Positive transaction amount in EGP.
        category_id (str): Non-empty category identifier string.
        timestamp (datetime): UTC timestamp; defaults to ``datetime.now(UTC)``.

    Example:
        >>> exp = Expense(1, 42, 3, 150.0, "food")
        >>> exp.amount
        150.0
    """

    expense_id: int
    user_id: int
    cycle_id: int
    amount: float
    category_id: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        """Validate all required fields.

        Raises:
            ValueError: If any identifier is non-positive, ``amount`` ≤ 0,
                or ``category_id`` is blank.
        """
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
