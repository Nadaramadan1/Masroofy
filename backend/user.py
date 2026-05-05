# class User <<entity>> {
#  -userName: string
#  -userId: int
#  -passwordHash: string
#  -email: string
# }

class User:

    def __init__(self, user_id, user_name, email, password_hash):

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

    def __str__(self):
        return f"User: {self.user_name} | {self.email}"

    def __repr__(self):
        return (
            f"User(user_id={self.user_id}, "
            f"user_name={self.user_name!r}, "
            f"email={self.email!r})"
        )