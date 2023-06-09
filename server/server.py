"""A module that handles the server creation code"""

import socket
import threading
import sys
import pickle
import uuid
import json
import base64
from functools import singledispatchmethod
from shared_python.shared_design_patterns.singleton_decorator import singleton
from shared_python.shared_hmac.hmac import Digestable
from shared_server_client_coms.authenticate_params import *
from shared_server_client_coms.commands import *
from shared_server_client_coms.transform_data import get_transfer_data, validate_data
from shared_python.shared_open_ai.chat import OpenAIChat
from .server_details import SERVER_HOST, SERVER_PORT, initial_digest_key
from .server_data import UserDatabase, DatabaseInsertState


class _ActiveClient:
    """A class that represents the client connection held by the server"""

    def __init__(self, communication_socket: socket.socket) -> None:
        self.__active = True
        self.__digestable_key = str(uuid.uuid4())
        self._communication_socket = communication_socket
        self.username = ""
        self.__chat_bot = OpenAIChat()

        listen_thread = threading.Thread(
            target=self._listen, args=(communication_socket,))
        listen_thread.start()

    def kill(self):
        """Disable the thread driving the TCP socket"""
        self.__active = False

    def send_command(self, command: Command) -> None:
        """Send a command to the server via a thread"""
        send_thread = threading.Thread(target=self.__send_command_sub,
                                       args=(self._communication_socket, command,
                                             Digestable(self.__digestable_key)), daemon=True)
        send_thread.start()

    def __send_command_sub(self, com_socket: socket.socket, command: Command,
                           my_digest: Digestable) -> None:
        data = get_transfer_data(command, my_digest)
        com_socket.send(data.encode("utf-8"))

    def _listen(self, my_socket: socket.socket):
        intial_digestable = Digestable(initial_digest_key())
        success_command = CommandSuccessfulConnection(self.__digestable_key)
        initial_data = get_transfer_data(success_command, intial_digestable)
        my_socket.send(initial_data.encode("utf-8"))

        my_digestable = Digestable(self.__digestable_key)

        while self.__active:
            try:
                data = my_socket.recv(1024)
                data = json.loads(data.decode("utf-8"))

                if validate_data(data, my_digestable):
                    command = pickle.loads(base64.b64decode(data["data"]))
                    print(command)
                    return_command = self._handle(command)

                    if return_command is not None:
                        self.send_command(return_command)

                else:
                    print("data is not valid")

                sys.stdout.flush()

            except (ConnectionAbortedError, ConnectionResetError, OSError):
                print("Socket closed")
                my_socket.close()
                ActiveServer().remove_client(self)
                sys.stdout.flush()
                break

    @singledispatchmethod
    def _handle(self, server_request) -> Command:
        """Not implemented"""
        print("got a Command")

    @_handle.register
    def _(self, server_request: CommandSuccessfulConnection) -> Command:
        print("got a CommandSuccessfulConnection")
        self.__digestable_key = Digestable(server_request.digest_key)

        return None

    @_handle.register
    def _(self, server_request: CommandAuthenticateUser) -> Command:
        print("got a CommandAuthenticateUser")

        self.username = server_request.username
        authentication_status = ActiveServer().authenticate_user(
            server_request.username, server_request.password)
        print(
            f"Authentication request: {server_request.username}:result: {str(authentication_status)}")
        if authentication_status == AuthStatus.SUCCESS:
            ActiveServer().announce(CommandUserConnected(server_request.username))
        return CommandAuthenticateUserResponse(authentication_status)

    @_handle.register
    def _(self, server_request: CommandCreateUser) -> Command:
        print("got a CommandCreateUser")
        authentication_status = ActiveServer().create_user(
            server_request.username, server_request.password)
        print(authentication_status)
        return CommandCreateUserResponse(authentication_status)

    @_handle.register
    def _(self, server_request: CommandSendChat) -> Command:
        print("got a CommandSendChat")
        ActiveServer().announce(server_request)

        return None

    @_handle.register
    def _(self, server_request: CommandRequestUsers) -> Command:
        print("got a CommandRequestUsers")

        return CommandConnectedUsers(ActiveServer().get_users())

    @_handle.register
    def _(self, server_request: CommandChatGPTRequest) -> Command:
        print("got a CommandChatGPTRequest")
        ActiveServer().announce(
            CommandSendChat(server_request.username, server_request.message))

        chat_response = self.__chat_bot.send_message(server_request.message)

        ActiveServer().announce(
            CommandSendChat("ChatGPT", chat_response))

        return None


@singleton
class ActiveServer():
    """A class that represents the server"""

    def __init__(self) -> None:
        self._clients: list[_ActiveClient] = []
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((SERVER_HOST, SERVER_PORT))
        self._server_socket.listen()
        self._users = UserDatabase()

    def start(self) -> None:
        """A method that polls the server, to handle new connections from a client"""
        while True:
            client_socket, address = self._server_socket.accept()
            self._clients.append(_ActiveClient(client_socket))

    def announce(self, command: Command) -> None:
        """Send a command to every active client currently connected"""
        for this_client in self._clients:
            this_client.send_command(command)

    def remove_client(self, client: _ActiveClient):
        """remove an active client from the list"""
        if client in self._clients:
            print(f"removing client {client}")
            self._clients.remove(client)
            self.announce(CommandSendChat(
                "Server", f"{client.username} has left the chat."))
            self.announce(CommandRemoveUser(client.username))

    def get_users(self) -> list[str]:
        """Returns a list of active users"""
        ret = ["ChatGPT"]
        for this_user in self._clients:
            ret.append(this_user.username)

        return ret

    def authenticate_user(self, username: str, password: str) -> AuthStatus:
        """Determine if the client's user name as password is correct"""
        return self._users.confirm_password(username, password)

    def create_user(self, username: str, password: str) -> CreateUserStatus:
        """Attempt to create a new user with the given username and password"""
        error = self._users.inser_user(username, password)
        if error == DatabaseInsertState.ALREADY_EXISTS:
            return CreateUserStatus.USERNAME_TAKEN

        elif error == DatabaseInsertState.SUCCESS:
            return CreateUserStatus.SUCCESS

        elif error == DatabaseInsertState.DATABASE_ERROR:
            return CreateUserStatus.NETWORK_ERROR
