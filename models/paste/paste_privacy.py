from enum import Enum

class PastePrivacy(int, Enum):
    PUBLIC = 0
    UNLISTED = 1
    PRIVATE = 2
