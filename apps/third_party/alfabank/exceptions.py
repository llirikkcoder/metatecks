class AlfaBankError(Exception):
    def __init__(self, message, code=None, raw_response=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.raw_response = raw_response
