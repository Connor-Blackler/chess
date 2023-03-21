"""A module that handles the client creation code"""

import socket
import threading
from typing import Callable
from server.server_details import SERVER_HOST,SERVER_PORT
from server.authenticate_params import AuthStatus

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

AuthClientCallback = Callable[[AuthStatus], None]

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
    def __init__(self, user_details: AuthClient, communication_socket: socket.socket = None, auth_callback: AuthClientEventWrapper = None) -> None:
        self.user_details = user_details
        self.auth_callback = auth_callback
        self._active = True

        if communication_socket is None:
            self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.communication_socket.connect((SERVER_HOST,SERVER_PORT))

            self._listening_thread = threading.Thread(target=self._message_recieve, daemon=True)
            self._listening_thread.start()
        else:
            self.communication_socket = communication_socket

    def _message_recieve(self):
        self.communication_socket.settimeout(1)
        while self._active:
            try:
                new_message = self.communication_socket.recv(1024).decode("utf-8")
                if new_message == "COMMAND:user_details":
                    self.communication_socket.send(str({"password":self.user_details.password,"username":self.user_details.username}).encode("utf-8"))
                elif new_message == "COMMAND:user_valid":
                    self.user_details.status = AuthStatus.SUCCESS
                elif new_message == "COMMAND:user_invalid_password":
                    self.user_details.status = AuthStatus.INCORRECT_PASSWORD
                    break
                elif new_message == "COMMAND:user_invalid_user":
                    self.user_details.status = AuthStatus.INCORRECT_USER
                    break
                else:
                    print(f"The server has sent us a message {new_message}")

            except TimeoutError:
                pass
            except (ConnectionAbortedError, ConnectionResetError, OSError):
                print("Socket closed")
                self.communication_socket.close()
                break

    def send_message(self, message: str):
        """Send a message to the server"""
        self.communication_socket.send(message.encode("utf-8"))
