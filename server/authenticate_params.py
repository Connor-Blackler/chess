"""All logic used to authenticate the users credentials"""

from enum import Enum,auto

class AuthStatus(Enum):
    """Different states that represent the userauthentication result"""
    SUCCESS = auto()
    NETWORK_ERROR = auto()
    INCORRECT_USER = auto()
    INCORRECT_PASSWORD = auto()
    PENDING = auto()
