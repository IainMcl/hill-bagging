class DatabaseServiceInterface:
    def connect(self):
        raise NotImplementedError("Subclasses must implement this method")

    def disconnect(self):
        raise NotImplementedError("Subclasses must implement this method")

    def execute_query(self, query):
        raise NotImplementedError("Subclasses must implement this method")

    def db_connection(self):
        """
        Context manager for database connection.
        """
        raise NotImplementedError("Subclasses must implement this method")
