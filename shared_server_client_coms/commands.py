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


class CommandUserConnected(Command):
    """A command that represents when a new user connects"""

    def __init__(self, username: str) -> None:
        self.username = username


class CommandConnectedUsers(Command):
    """A command that holds a list of all connected users"""

    def __init__(self, users: list[str]) -> None:
        self.users = users


class CommandRemoveUser(Command):
    """A command that triggers when a user disconnects"""

    def __init__(self, username: str) -> None:
        self.username = username


class CommandRequestUsers(Command):
    """A command that will ask the server the list of connected clients"""


class CommandChatGPTRequest(Command):
    """A command that will request information from ChatGPT"""

    def __init__(self, username: str, message: str) -> None:
        self.username = username
        self.message = message
