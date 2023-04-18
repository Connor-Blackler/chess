"""A module to unit test commands"""
from shared_server_client_coms.authenticate_params import *
from shared_server_client_coms.commands import *


def test_auth_user() -> None:
    my_username = "bob"
    my_password = "name"

    auth_user = CommandAuthenticateUser(my_username, my_password)

    assert auth_user.username == my_username
    assert auth_user.password == my_password


def test_authenticate_user_response() -> None:
    status_arr = (AuthStatus.INCORRECT_PASSWORD, AuthStatus.INCORRECT_USER,
                  AuthStatus.NETWORK_ERROR, AuthStatus.PENDING, AuthStatus.SUCCESS)

    for status in status_arr:
        my_authenticate_user_response = CommandAuthenticateUserResponse(status)

        assert my_authenticate_user_response.status == status


def test_command_successful_connection() -> None:
    test_key = "awdawdawdawd"

    my_success_connection = CommandSuccessfulConnection(test_key)

    assert my_success_connection.digest_key == test_key


def test_create_user() -> None:
    my_username = "bob"
    my_password = "name"

    create_user = CommandCreateUser(my_username, my_password)

    assert create_user.username == my_username
    assert create_user.password == my_password


def test_create_user_response() -> None:
    status_arr = (CreateUserStatus.NETWORK_ERROR, CreateUserStatus.SUCCESS,
                  CreateUserStatus.USERNAME_TAKEN, CreateUserStatus.PENDING)

    for status in status_arr:
        my_create_user_response = CommandCreateUserResponse(status)

        assert my_create_user_response.status == status


def test_command_send_chat() -> None:
    username = "bob"
    message = "this is a message"

    send_chat = CommandSendChat(username, message)

    assert send_chat.username == username
    assert send_chat.message == message


def test_command_user_connected() -> None:
    username = "bob"

    my_command = CommandUserConnected(username)

    assert my_command.username == username


def test_command_connected_users() -> None:
    users = ["bob", "bill"]

    my_command = CommandConnectedUsers(users)

    assert len(my_command.users) == 2
    assert my_command.users[0] == users[0]
    assert my_command.users[1] == users[1]


def test_command_remove_user() -> None:
    user = "bob"

    my_command = CommandRemoveUser(user)

    assert my_command.username == user


def test_command_chat_gpt_request() -> None:
    user = "bob"
    message = "testing"

    my_command = CommandChatGPTRequest(user, message)

    assert my_command.username == user
    assert my_command.message == message
