from enum import Enum

class PasteExpiration(str, Enum):
    NEVER = "N"
    TEN_MINUTES = "10M"
    ONE_HOUR = "1H"
    ONE_DAY = "1D"