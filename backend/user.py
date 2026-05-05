# class User <<entity>> {
#  -userName: string
#  -userId: int
#  -passwordHash: string
#  -email: string
# }

"""
user.py
=======
Defines the :class:`User` entity for the Masroofy budget-tracking application.

This module is part of the **backend** package and maps directly to the
``User`` entity described in the system's class diagram.
"""


class User:
    """Represents an authenticated user of the Masroofy application.

    The ``User`` class is an entity that stores identity and credential
    information.  All fields are validated on construction; invalid values
    raise :exc:`ValueError`.

    Attributes:
        user_id (int): Unique positive integer that identifies the user.
        user_name (str): Display name of the user (non-empty).
        email (str): Valid e-mail address used for login.
        password_hash (str): Bcrypt/Werkzeug hash of the user's password.

    Example:
        >>> u = User(1, "Alice", "alice@example.com", "hashed_pw")
        >>> print(u)
        User: Alice | alice@example.com
    """

    def __init__(self, user_id: int, user_name: str, email: str, password_hash: str) -> None:
        """Initialise a User instance with validated fields.

        Args:
            user_id (int): Positive integer identifier.
            user_name (str): Non-empty display name.
            email (str): String that contains ``@``.
            password_hash (str): Non-empty password hash.

        Raises:
            ValueError: If ``user_id`` is not positive, ``user_name`` is
                blank, ``email`` is invalid, or ``password_hash`` is empty.
        """
        if user_id <= 0:
            raise ValueError("user_id must be positive")
        if not user_name or not user_name.strip():
            raise ValueError("user_name is required")
        if not email or "@" not in email:
            raise ValueError("invalid email")
        if not password_hash:
            raise ValueError("password_hash is required")

        self.user_id = user_id
        self.user_name = user_name
        self.email = email
        self.password_hash = password_hash

    def __str__(self) -> str:
        """Return a human-readable string representation.

        Returns:
            str: ``"User: <user_name> | <email>"``
        """
        return f"User: {self.user_name} | {self.email}"

    def __repr__(self) -> str:
        """Return an unambiguous developer representation.

        Returns:
            str: Constructor-style representation including all key fields.
        """
        return (
            f"User(user_id={self.user_id}, "
            f"user_name={self.user_name!r}, "
            f"email={self.email!r})"
        )
