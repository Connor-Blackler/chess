"""A module that handles the client creation code"""
from __future__ import annotations
import socket
import threading
import json
import pickle
import base64
from functools import singledispatchmethod
from typing import Callable
from server.server_details import SERVER_HOST,SERVER_PORT,initial_digest_key
from shared_server_client_coms.authenticate_params import AuthStatus
from shared_server_client_coms.commands import *
from shared_server_client_coms.transform_data import Digestable,validate_data,get_transfer_data

AuthClientCallback = Callable[[AuthStatus], None]

class AuthClient():
    """A class that represents the client's name and password"""
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self._status = AuthStatus.PENDING

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, new_status: AuthStatus) -> None:
        self._status = new_status

class AuthClientEventWrapper(AuthClient):
    """A Authclient with additional callback functionality"""
    def __init__(self, username: str, password: str, callback: AuthClientCallback) -> None:
        super().__init__(username, password)

        self.event_callback = callback

    @AuthClient.status.setter
    def status(self, new_status: AuthStatus) -> None:
        self._status = new_status
        if self.event_callback is not None:
            self.event_callback(new_status)

class ActiveClient():
    """A class that represents the client connection"""
    def __init__(self, user_details: AuthClient) -> None:
        self._user_details = user_details
        self._digest = Digestable(initial_digest_key())

        try:
            self._communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._communication_socket.connect((SERVER_HOST,SERVER_PORT))

            self._listen_thread = threading.Thread(target=self._listen, args=(self._communication_socket,), daemon=True)
            self._listen_thread.start()

        except ConnectionRefusedError:
            self._user_details.status = AuthStatus.NETWORK_ERROR

    def authenticate_user(self, user_details: AuthClient) -> None:
        """Authenciate the user details via a thread to communicate with the server via TCP"""
        self._user_details = user_details
        this_command = CommandAuthenticateUser(user_details.username, user_details.password)
        self.send_command(this_command)

    def send_command(self, command: Command) -> None:
        """Send a command to the server via a thread"""
        send_thread = threading.Thread(target=self.__send_command_sub,
                                       args=(self._communication_socket, command, self._digest), daemon=True)
        send_thread.start()

    def __send_command_sub(self, com_socket: socket.socket, command: Command, my_digest: Digestable) -> None:
        data = get_transfer_data(command, my_digest)
        com_socket.send(data.encode("utf-8"))

    def is_successful(self) -> bool:
        """Determine if the activation process is successful"""
        return self._user_details.status == AuthStatus.SUCCESS

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

    @singledispatchmethod
    def _handle(self, server_request) -> Command:
        """Not implemented"""
        print("got a Command")

    @_handle.register
    def _(self, server_request: CommandAuthenticateUserResponse) -> Command:
        print("got a CommandAuthenticateUserResponse")

        self._user_details.status = server_request.status
        return None

    @_handle.register
    def _(self, server_request: CommandSuccessfulConnection) -> Command:
        print("got a CommandSuccessfulConnection")
        self._digest = Digestable(server_request.digest_key)

        return None
