class NoSuchTickerError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

class InsufficientSharesError(Exception):
    pass

class VolumeLessThanZeroError(Exception):
    pass