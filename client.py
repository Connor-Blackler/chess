"""A module that handles the main loop for the client connection"""

from client.client import ActiveClient
from client.login import AuthenciateUser
from client.client_main_window import MainWindow

def _retrieve_authenticated_user() -> ActiveClient:
    ret = ActiveClient()
    auth_user_ui = AuthenciateUser(ret)

    return ret

def main() -> None:
    """Main loop where the client is constructed and polled"""
    my_client = _retrieve_authenticated_user()
    if my_client is None:
        quit()

    if my_client.is_successful():
        this_window = MainWindow(my_client)

main()
