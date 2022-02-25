

class CreateTransactionError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class FindTransactionError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ValidateTransactionError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)