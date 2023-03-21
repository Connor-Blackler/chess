"""A module that handles the client creation code"""

import socket
import threading
from dataclasses import dataclass,field
from server.server_details import SERVER_HOST,SERVER_PORT

@dataclass
class AuthClient():
    """A class that represents the client's name and password"""
    nickname: str
    password: str

@dataclass
class ActiveClient():
    """A class that represents the client connection"""
    nickname: str
    communication_socket: socket.socket = None
    _listening_thread: threading.Thread = field(init=False)

    def __post_init__(self) -> None:
        if self.communication_socket is None:
            self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.communication_socket.connect((SERVER_HOST,SERVER_PORT))

            self._listening_thread = threading.Thread(target=self._message_recieve)
            self._listening_thread.start()

    def _message_recieve(self):
        while True:
            try:
                new_message = self.communication_socket.recv(1024).decode("utf-8")
                if new_message == "COMMAND:user_details":
                    self.communication_socket.send(self.nickname.encode("utf-8"))
                else:
                    print(new_message)

            except ConnectionAbortedError:
                print("Socket closed")
                self.communication_socket.close()
                break

    def send_message(self, message: str):
        """Send a message to the server"""
        self.communication_socket.send(message.encode("utf-8"))
