class Category:
    """
    Represents an expense category in the system.
    
    Each category has a name, optional icon, and unique ID.
    """

    def __init__(self, category_id: int, name: str, icon: str = None):
        """
        Initialize a new Category.

        Args:
            category_id (int): Unique identifier for the category.
            name (str): Category name.
            icon (str, optional): Icon representing the category.
        """
        self.category_id = category_id
        self.name = name
        self.icon = icon

    def __str__(self):
        """
        Return the category name as string representation.
        """
        return self.name