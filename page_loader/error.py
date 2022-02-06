class FileError(OSError):
    def __init__(self, info, path):
        self.path = path
        self.info = info
        super().__init__(
            f"FileError: {info} {path}"
        )
