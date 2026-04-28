class Category:

    def __init__(self, category_id: int, name: str, icon: str = None):
        self.category_id = category_id
        self.name = name
        self.icon = icon

    def __str__(self):
        return self.name