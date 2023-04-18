"""A module that handles the client creation code"""
from __future__ import annotations
import socket
import threading
import json
import pickle
import base64
import sys
from dataclasses import dataclass
from functools import singledispatchmethod
from typing import Callable
from server.server_details import SERVER_HOST, SERVER_PORT, initial_digest_key
from shared_server_client_coms.authenticate_params import *
from shared_server_client_coms.commands import *
from shared_server_client_coms.transform_data import Digestable, validate_data, get_transfer_data


@dataclass
class UserDetails():
    """A dataclass to store user details and the authentication status"""
    username: str = ""
    password: str = ""
    authentication_status: AuthStatus = AuthStatus.PENDING


class EventCallbacks():
    """A callback-like class to allow users to override the desired methods
    acting like a callback
    """

    def __init__(self,
                 authenticate_user_response_callback: Callable[[
                     AuthStatus], None] = None,
                 successful_connection_callback: Callable[[], None] = None,
                 connection_error_callback: Callable[[], None] = None,
                 create_user_response_callback: Callable[[
                     CreateUserStatus], None] = None,
                 chat_recieved_callback: Callable[[str, str], None] = None,
                 users_connected_recieved: Callable[[list[str]], None] = None,
                 user_connected_recieved_callback: Callable[[
                     str], None] = None,
                 remove_user_callback: Callable[[str], None] = None) -> None:

        self._authenticate_user_response_callback = authenticate_user_response_callback
        self._successful_connection_callback = successful_connection_callback
        self._connection_error_callback = connection_error_callback
        self._create_user_response_callback = create_user_response_callback
        self._chat_recieved_callback = chat_recieved_callback
        self._users_connected_callback = users_connected_recieved
        self._user_connected_recieved_callback = user_connected_recieved_callback
        self._remove_user_callback = remove_user_callback

    def authenticate_user_response(self, status: AuthStatus) -> None:
        """Triggers when the server responds to the client after they have
        requested to authenticate a new user
        """
        if self._authenticate_user_response_callback is not None:
            self._authenticate_user_response_callback(status)

    def successful_connection(self) -> None:
        """Triggers when the client has succesfully communicated with the server"""
        if self._successful_connection_callback is not None:
            self._successful_connection_callback()

    def connection_error(self) -> None:
        """Triggers when the server recieves a chat message from another client"""
        if self._connection_error_callback is not None:
            self._connection_error_callback()

    def create_user_response(self, status: CreateUserStatus) -> None:
        """Triggers when the server responds to the client after they have
        requested to create a new user
        """
        if self._create_user_response_callback is not None:
            self._create_user_response_callback(status)

    def chat_recieved(self, username: str, message: str) -> None:
        """Triggers when the server recieves a chat message from another client"""
        if self._chat_recieved_callback is not None:
            self._chat_recieved_callback(username, message)

    def user_connected(self, username: str) -> None:
        """Triggers when the server gains a new users connected"""
        if self._user_connected_recieved_callback is not None:
            self._user_connected_recieved_callback(username)

    def users_connected(self, users: list[str]) -> None:
        """
        Triggers when after the user is authenticated,
        let the client know what users are online
        """
        if self._users_connected_callback is not None:
            self._users_connected_callback(users)

    def remove_user(self, user: str) -> None:
        """
        Triggers when another client disconnects from the server
        """
        if self._remove_user_callback is not None:
            self._remove_user_callback(user)


class ActiveClient():
    """A class that represents the client connection"""

    def __init__(self, callbacks: EventCallbacks = EventCallbacks()) -> None:
        self._callbacks = callbacks
        self._digest = Digestable(initial_digest_key())
        self._user_details: UserDetails = None

        try:
            self._communication_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self._communication_socket.connect((SERVER_HOST, SERVER_PORT))

            self._listen_thread = threading.Thread(target=self._listen,
                                                   args=(self._communication_socket,), daemon=True)
            self._listen_thread.start()

        except ConnectionRefusedError:
            self._callbacks.connection_error()

    def get_username(self) -> str:
        """returns the username of this client"""
        return self._user_details.username

    def send_command(self, command: Command) -> None:
        """Send a command to the server via a thread"""
        send_thread = threading.Thread(target=self.__send_command_sub,
                                       args=(self._communication_socket, command,
                                             self._digest), daemon=True)
        send_thread.start()

    def __send_command_sub(self, com_socket: socket.socket, command: Command,
                           my_digest: Digestable) -> None:
        data = get_transfer_data(command, my_digest)
        com_socket.send(data.encode("utf-8"))

    def register_event_callback(self, obj: EventCallbacks) -> None:
        """register a different event callback object to handle responses from the server"""
        self._callbacks = obj

    def authenticate_user(self, user: UserDetails) -> None:
        """Send a request to the server to authenticate the user via TCP"""
        self._user_details = user
        this_command = CommandAuthenticateUser(user.username, user.password)
        self.send_command(this_command)

    def create_user(self, user: UserDetails) -> None:
        """Send a request to the server to create the new user via TCP"""
        this_command = CommandCreateUser(user.username, user.password)
        self.send_command(this_command)

    def is_successful(self) -> bool:
        """Determine if the activation process is successful"""
        if self._user_details is None:
            return False

        return self._user_details.authentication_status == AuthStatus.SUCCESS

    def _listen(self, communication_socket: socket.socket) -> None:
        while True:
            try:
                new_message = communication_socket.recv(1024).decode("utf-8")
                data = json.loads(new_message)

                if validate_data(data, self._digest):
                    command = pickle.loads(base64.b64decode(data["data"]))
                    print(command)
                    return_command = self._handle(command)

                    if return_command is not None:
                        self.send_command(return_command)

            except (ConnectionAbortedError, ConnectionResetError, OSError):
                print("Socket closed")
                communication_socket.close()
                break

            sys.stdout.flush()

    @singledispatchmethod
    def _handle(self, server_request) -> Command:
        """Not implemented"""
        print("got a Command")

    @_handle.register
    def _(self, server_request: CommandAuthenticateUserResponse) -> Command:
        print("got a CommandAuthenticateUserResponse")

        self._user_details.authentication_status = server_request.status
        self._callbacks.authenticate_user_response(server_request.status)
        return None

    @_handle.register
    def _(self, server_request: CommandSuccessfulConnection) -> Command:
        print("got a CommandSuccessfulConnection")
        self._digest = Digestable(server_request.digest_key)

        self._callbacks.successful_connection()
        return None

    @_handle.register
    def _(self, server_request: CommandCreateUserResponse) -> Command:
        print("got a CommandCreateUserResponse")

        self._callbacks.create_user_response(server_request.status)
        return None

    @_handle.register
    def _(self, server_request: CommandSendChat) -> Command:
        print("got a CommandSendChat")
        print(f"{server_request.username}, {server_request.message}")
        self._callbacks.chat_recieved(
            server_request.username, server_request.message)

        return None

    @_handle.register
    def _(self, server_request: CommandConnectedUsers) -> Command:
        print("got a CommandConnectedUsers")
        print(f"{server_request.users}")
        self._callbacks.users_connected(server_request.users)

        return None

    @_handle.register
    def _(self, server_request: CommandUserConnected) -> Command:
        print("got a CommandUserConnected")
        print(f"{server_request.username}")
        self._callbacks.user_connected(server_request.username)

        return None

    @_handle.register
    def _(self, server_request: CommandRemoveUser) -> Command:
        print("got a CommandRemoveUser")
        print(f"{server_request.username}")
        self._callbacks.remove_user(server_request.username)

        return None
