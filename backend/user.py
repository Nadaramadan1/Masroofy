# class User <<entity>> {
#  -userName: string
#  -userId: int
#  -passwordHash: string
#  -email: string
# }

class User:
    def __init__(self, user_id, user_name, email, password_hash):
        self.user_id = user_id
        self.user_name = user_name
        self.email = email
        self.password_hash = password_hash

    def __str__(self):
        return f"User: {self.user_name} | {self.email}"

    def __repr__(self):
        return self.__str__()