from .authenticate_params import AuthStatus

class Command():
    """Abstract base class for a client <-> server command"""

class CommandAuthenticateUser(Command):
    """A command that represents user authentication"""
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

class CommandAuthenticateUserResponse(Command):
    """A command that represents user authentication"""
    def __init__(self, status: AuthStatus) -> None:
        self.status = status

class CommandSuccessfulConnection(Command):
    """A command that represents user authentication"""
    def __init__(self, digest_key: str) -> None:
        self.digest_key = digest_key
