class ValidationFailedError(Exception):
    def __init__(self, errors: list[dict]):
        self.errors = errors

class SemesterNotFoundError(Exception):
    pass
