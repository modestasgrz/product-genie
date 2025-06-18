class ShotCompositionException(Exception):
    def __init__(self, message):
        super().__init__(message)


class JSONDecodeRetranslateError(Exception):
    def __init__(self, message):
        super().__init__(message)
