"""A module that handles the server creation code"""

import socket
import threading
import ast
import sys
from client.client import ActiveClient,AuthClient
from .authenticate_params import AuthStatus
from .server_details import SERVER_HOST,SERVER_PORT

class ActiveServer():
    """A class that represents the server"""
    def __init__(self) -> None:
        self._clients: list[ActiveClient] = []
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((SERVER_HOST,SERVER_PORT))
        self._server_socket.listen()

    def _authenticate_user(self, client: AuthClient) -> AuthStatus:
        if client.username == "bob" and client.password == "bob2":
            return AuthStatus.SUCCESS

        elif client.username == "bob" and client.password != "bob2":
            return AuthStatus.INCORRECT_PASSWORD

        else:
            return AuthStatus.INCORRECT_USER

    def start(self) -> None:
        """A method that polls the server, to handle new connections from a client"""
        while True:
            self._server_socket.settimeout(1)
            try:
                client_socket, address = self._server_socket.accept()
            except socket.timeout:
                pass
            else:
                print(f"connected: {str(address)}")

                client_socket.settimeout(None)
                client_socket.send("COMMAND:user_details".encode("utf-8"))
                user_details = client_socket.recv(1024)
                user_details = ast.literal_eval(user_details.decode("utf-8"))

                client_details = AuthClient(user_details["username"], user_details["password"])
                status = self._authenticate_user(client_details)
                print(f"Authentication request: {client_details.username}: result: {str(status)}")

                if status == AuthStatus.INCORRECT_PASSWORD:
                    client_socket.send("COMMAND:user_invalid_password".encode("utf-8"))

                elif status == AuthStatus.INCORRECT_USER:
                    client_socket.send("COMMAND:user_invalid_user".encode("utf-8"))

                elif status == AuthStatus.SUCCESS:
                    client_socket.send("COMMAND:user_valid".encode("utf-8"))
                    new_client = ActiveClient(client_details,communication_socket=client_socket)

                    self._clients.append(new_client)
                    print(f"{new_client.user_details.username} has joined the chat")
                    self._announce(f"{new_client.user_details.username} has joined the chat")

                    thread = threading.Thread(target=self._message_recieved, args=(new_client,))
                    thread.start()

            sys.stdout.flush()

    def _announce(self, message: str) -> None:
        for this_client in self._clients:
            this_client.communication_socket.send(message.encode("utf-8"))

    def _message_recieved(self, client: ActiveClient) -> None:
        while True:
            client.communication_socket.settimeout(1)
            try:
                new_message = client.communication_socket.recv(1024).decode("utf-8")
                print(f"new message received from {client.user_details.username}: {new_message}")
                self._announce(f"new message: {client.user_details.username}: {new_message}")
            except socket.timeout:
                pass
            except (ConnectionAbortedError, ConnectionResetError):
                client.communication_socket.close()
                self._clients.remove(client)
                self._announce(f"{client.user_details.username} has left the chat")
                print(f"{client.user_details.username} has left the chat")
                break
