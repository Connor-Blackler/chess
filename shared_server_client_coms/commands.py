from .authenticate_params import *

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

class CommandCreateUser(Command):
    """A command that represents user authentication"""
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

class CommandCreateUserResponse(Command):
    """A command that represents user authentication"""
    def __init__(self, status: CreateUserStatus) -> None:
        self.status = status

class CommandSendChat(Command):
    """A command that represents user chatting"""
    def __init__(self, username: str, message: str) -> None:
        self.username = username
        self.message = message
