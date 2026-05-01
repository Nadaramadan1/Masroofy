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
    """Handles all direct interactions with the user database (JSON file)."""
    def __init__(self, data_path):
        self.data_path = data_path

    def load_all(self):
        if not os.path.exists(self.data_path):
            return []
        with open(self.data_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save(self, user_data):
        """Equivalent to INSERT User in the sequence diagram."""
        users = self.load_all()
        # Generate new ID
        new_id = 1 if not users else max(u["user_id"] for u in users) + 1
        user_data["user_id"] = new_id
        
        users.append(user_data)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
        return user_data

class AuthorizationService:
    def __init__(self):
        self.repository = UserRepository(DATA_FILE)
        self.logged_in_users = []

    def register(self, user_name, email, password):
        """Implementation of the Register Sequence Diagram."""
        # 1. hashPassword()
        hashed_password = self.hashPassword(password)
        
        # 2. generateToken()
        token = self.generateToken()
        
        # Prepare user data
        user_data = {
            "user_name": user_name,
            "email": email,
            "password_hash": hashed_password,
            "created_token": token # Optional: save token or handle separately
        }
        
        # 3. User Repository: save(user)
        saved_user = self.repository.save(user_data)
        
        # Return success (returning the User object as shown in diagram)
        return User(
            saved_user["user_id"], 
            saved_user["user_name"], 
            saved_user["email"], 
            saved_user["password_hash"]
        )

    def login(self, email, password):
        users_data = self.repository.load_all()
        for u_data in users_data:
            if u_data.get("email") == email:
                user = User(u_data["user_id"], u_data["user_name"], u_data["email"], u_data["password_hash"])
                if self.verifyPassword(password, user.password_hash):
                    if user.user_id not in self.logged_in_users:
                        self.logged_in_users.append(user.user_id)
                    return True, self.generateToken(), user
        return False, None, None

    def logout(self, userId):
        if userId in self.logged_in_users:
            self.logged_in_users.remove(userId)

    def verifyPassword(self, password, hashed):
        return check_password_hash(hashed, password)

    def verifyPin(self, pin):
        return len(pin) == 4 and pin.isdigit()

    def generateToken(self):
        return secrets.token_hex(16)

    def hashPassword(self, password):
        return generate_password_hash(password)

    def isAuthenticated(self, userId):
        return userId in self.logged_in_users
