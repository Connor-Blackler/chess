"""All logic used to authenticate the users credentials"""

from enum import Enum,auto
from client.client import AuthClient

class AuthStatus(Enum):
    """Different states that represent the userauthentication result"""
    SUCESS: auto()
    NETWORK_ERROR: auto()
    INCORRECT_USER: auto()
    INCORRECT_PASSWORD: auto()

def authenticate_user(client_details: AuthClient) -> AuthStatus:
    """Public function to authenticate a users credentials"""
    return AuthStatus.SUCESS
