# class AuthorizationService <<control>> {
#  +login(email: string, password: string): boolean
#  +logout(userId: int): void
#  +register(userName: string, email: string, password: string): User
#  +verifyPassword(password: string): boolean
#  +verifyPin(pin: string): boolean
#  +generateToken(): string
#  +hashPassword(password: string): string
#  +isAuthenticated(userId: int): boolean
# }

"""
auth_service.py
===============
Authentication and user-management services for the Masroofy application.

Exports
-------
:class:`UserRepository`
    Low-level JSON persistence for user records.
:class:`AuthorizationService`
    High-level service implementing the Register / Login sequence diagrams.
"""

import json
import os
import secrets

from werkzeug.security import generate_password_hash, check_password_hash

try:
    from user import User
except ImportError:
    from .user import User

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "users.json")


class UserRepository:
    """Handles direct read/write access to the ``users.json`` store.

    This class is the single point of contact between the
    :class:`AuthorizationService` and the file-system user database.

    Attributes:
        data_path (str): Absolute path to the ``users.json`` file.
    """

    def __init__(self, data_path: str) -> None:
        """Initialise the repository with a path to the JSON data file.

        Args:
            data_path (str): Absolute path to ``users.json``.
        """
        self.data_path = data_path

    def load_all(self) -> list:
        """Load and return all user records from disk.

        Returns:
            list[dict]: List of user dictionaries.  Returns ``[]`` if the
                file does not exist or contains invalid JSON.
        """
        if not os.path.exists(self.data_path):
            return []
        with open(self.data_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save(self, user_data: dict) -> dict:
        """Persist a new user record (INSERT equivalent).

        Assigns an auto-incremented ``user_id`` to ``user_data`` before
        appending it to the JSON store.

        Args:
            user_data (dict): User fields without ``user_id``
                (e.g., ``user_name``, ``email``, ``password_hash``).

        Returns:
            dict: The saved record including its generated ``user_id``.
        """
        users = self.load_all()
        new_id = 1 if not users else max(u["user_id"] for u in users) + 1
        user_data["user_id"] = new_id
        users.append(user_data)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
        return user_data


class AuthorizationService:
    """Control class that implements authentication use-cases.

    Implements the **Register** and **Login** sequence diagrams from the
    Masroofy design model.

    Attributes:
        repository (UserRepository): Provides persistence for user records.
        logged_in_users (list[int]): In-memory list of authenticated user IDs.
    """

    def __init__(self) -> None:
        """Initialise the service with a repository and empty session list."""
        self.repository = UserRepository(DATA_FILE)
        self.logged_in_users: list = []

    def register(self, user_name: str, email: str, password: str) -> User:
        """Create and persist a new user account.

        Follows the **Register Sequence Diagram**:

        1. Hash the plain-text password.
        2. Generate a random session token.
        3. Persist the user via :class:`UserRepository`.
        4. Return a :class:`~user.User` entity.

        Args:
            user_name (str): Display name for the new account.
            email (str): E-mail address used as the login identifier.
            password (str): Plain-text password (hashed before storage).

        Returns:
            User: The newly created :class:`~user.User` instance.
        """
        hashed_password = self.hashPassword(password)
        token = self.generateToken()

        user_data = {
            "user_name": user_name,
            "email": email,
            "password_hash": hashed_password,
            "created_token": token,
        }

        saved_user = self.repository.save(user_data)
        return User(
            saved_user["user_id"],
            saved_user["user_name"],
            saved_user["email"],
            saved_user["password_hash"],
        )

    def login(self, email: str, password: str):
        """Authenticate a user by e-mail and password.

        Args:
            email (str): Registered e-mail address.
            password (str): Plain-text password to verify.

        Returns:
            tuple: ``(True, token, User)`` on success,
                ``(False, None, None)`` on failure.
        """
        for u_data in self.repository.load_all():
            if u_data.get("email") == email:
                user = User(
                    u_data["user_id"],
                    u_data["user_name"],
                    u_data["email"],
                    u_data["password_hash"],
                )
                if self.verifyPassword(password, user.password_hash):
                    if user.user_id not in self.logged_in_users:
                        self.logged_in_users.append(user.user_id)
                    return True, self.generateToken(), user
        return False, None, None

    def logout(self, userId: int) -> None:
        """Remove a user from the active-session list.

        Args:
            userId (int): The user identifier to invalidate.
        """
        if userId in self.logged_in_users:
            self.logged_in_users.remove(userId)

    def verifyPassword(self, password: str, hashed: str) -> bool:
        """Check a plain-text password against its stored hash.

        Args:
            password (str): The plain-text candidate.
            hashed (str): The Werkzeug/bcrypt hash from the database.

        Returns:
            bool: ``True`` if the password matches.
        """
        return check_password_hash(hashed, password)

    def verifyPin(self, pin: str) -> bool:
        """Validate that a PIN is exactly 4 numeric digits.

        Args:
            pin (str): Candidate PIN string.

        Returns:
            bool: ``True`` only when the PIN is a 4-digit numeric string.
        """
        return len(pin) == 4 and pin.isdigit()

    def generateToken(self) -> str:
        """Generate a cryptographically secure random hex token.

        Returns:
            str: 32-character hex string (16 bytes of entropy).
        """
        return secrets.token_hex(16)

    def hashPassword(self, password: str) -> str:
        """Hash a plain-text password using Werkzeug's PBKDF2/bcrypt.

        Args:
            password (str): The plain-text password.

        Returns:
            str: The resulting password hash suitable for database storage.
        """
        return generate_password_hash(password)

    def isAuthenticated(self, userId: int) -> bool:
        """Check whether a user currently has an active session.

        Args:
            userId (int): The user identifier to check.

        Returns:
            bool: ``True`` if the user is in the active-sessions list.
        """
        return userId in self.logged_in_users
