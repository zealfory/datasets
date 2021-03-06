class DownloadHandler:
    """
    Base class for all download handlers
    """
    def __init__(self, repository, definition):
        self.context = repository.context
        self.repository = repository
        self.definition = definition

    @staticmethod
    def find(repository, definition):
        return repository.findhandler("download", definition["handler"])(repository, definition)