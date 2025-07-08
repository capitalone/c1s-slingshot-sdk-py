class ResourceNotFoundError(Exception):
    """Exception raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: str):
        """Initialize the exception with resource type and identifier."""
        super().__init__(f"{resource} with identifier '{identifier}' not found.")
        self.resource = resource
        self.identifier = identifier
