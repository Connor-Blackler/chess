"""Unit tests for client.py"""
from client.client import UserDetails
from shared_server_client_coms.authenticate_params import AuthStatus


def test_userdetails_defaults() -> None:
    my_user = UserDetails()

    assert my_user.password == ""
    assert my_user.username == ""
    assert my_user.authentication_status == AuthStatus.PENDING
