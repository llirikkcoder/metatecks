class Bitrix24Error(Exception):
    def __init__(self, message, raw_response=None):
        super().__init__(message)
        self.message = message
        self.raw_response = raw_response
