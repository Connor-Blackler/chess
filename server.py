"""A module that handles the main loop for the server creation"""

from server.server import ActiveServer

def main() -> None:
    """The main loop that creates a server, and polls it"""
    server = ActiveServer()
    server.start()

main()