"""A module that handles the main loop for the server creation"""

import threading
from server.server import ActiveServer


def _start_server() -> None:
    server = ActiveServer()
    server.start()


def main() -> None:
    """The main loop that creates a server, and polls it"""
    thread = threading.Thread(target=_start_server)
    thread.start()


main()
