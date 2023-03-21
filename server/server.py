"""A module that handles the server creation code"""

import socket
import threading
from dataclasses import dataclass,field
from client.client import ActiveClient
from .server_details import SERVER_HOST,SERVER_PORT

@dataclass
class ActiveServer():
    """A class that represents the server"""
    _clients: list[ActiveClient] = field(default_factory=list)
    _server_socket: socket = field(init=False)

    def __post_init__(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((SERVER_HOST,SERVER_PORT))
        self._server_socket.listen()

    def start(self) -> None:
        """A method that polls the server, to handle new connections from a client"""
        while True:
            client_socket, address = self._server_socket.accept()
            print(f"connected: {str(address)}")

            client_socket.send("COMMAND:user_details".encode("utf-8"))
            user_details = client_socket.recv(1024).decode("utf-8")

            new_client = ActiveClient(nickname=user_details, communication_socket=client_socket)
            self._clients.append(new_client)
            print(f"{new_client.nickname} has joined the chat")
            self._announce(f"{new_client.nickname} has joined the chat")

            thread = threading.Thread(target=self._message_recieved, args=(new_client,))
            thread.start()

    def _announce(self, message: str) -> None:
        for this_client in self._clients:
            this_client.communication_socket.send(message.encode("utf-8"))

    def _message_recieved(self, client: ActiveClient) -> None:
        while True:
            try:
                new_message = client.communication_socket.recv(1024).decode("utf-8")
                self._announce(new_message)
            except ConnectionAbortedError:
                client.communication_socket.close()
                self._clients.remove(client)
                self._announce(f"{client.nickname} has left the chat")
                print(f"{client.nickname} has left the chat")
                break
