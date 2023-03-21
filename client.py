"""A module that handles the main loop for the client connection"""

from client.client import ActiveClient
from client.login import AuthenciateUser
from client.client_main_window import main_window

def _retrieve_authenticated_user() -> ActiveClient:
    auth_user_ui = AuthenciateUser()
    my_client = auth_user_ui.retrieve_client()

    return my_client

def main() -> None:
    """Main loop where the client is constructed and polled"""
    my_client = _retrieve_authenticated_user()
    if my_client.is_successful():
        main = main_window(my_client)

main()
