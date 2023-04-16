"""Code to show the main window UI"""
from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5 import uic
from shared_server_client_coms.commands import CommandSendChat,CommandRequestUsers
from .client import ActiveClient,EventCallbacks

class _MyMainWindowQT(QMainWindow):
    def __init__(self):
        super(_MyMainWindowQT, self).__init__()
        uic.loadUi("client/main_window_qt_file.ui", self)
        self.show()

class MainWindow:
    def __init__(self, client: ActiveClient) -> None:
        self.client = client

        self._app = QApplication([])
        self._window = _MyMainWindowQT()

        self._window.send_message_btn.clicked.connect(self._message_btn_clicked)

        callbacks = EventCallbacks(
            None,
            None,
            self._connection_error_callback,
            None,
            self._message_recieved_callback,
            self._users_connected_callback,
            self._user_connected_callback,
            self._remove_user_callback)

        client.register_event_callback(callbacks)
        client.send_command(CommandRequestUsers())

        self._app.exec_()

    def _message_btn_clicked(self) -> None:
        self.client.send_command(CommandSendChat(self.client.get_username(),
                                                 self._window.send_message_box.toPlainText()))
        self._window.send_message_box.setPlainText("")

    def _message_recieved_callback(self, username: str, message: str) -> None:
        my_list = [f"{username}: {message}"]
        self._window.chat_list.addItems(my_list)

    def _connection_error_callback(self) -> None:
        ...

    def _append_user(self, user: str) -> None:
        self._window.connected_users.addItem(user)

    def _remove_user(self, user: str) -> None:
        ...

    def _user_connected_callback(self, username: str) -> None:
        self._append_user(username)

    def _users_connected_callback(self, users: list[str]) -> None:
        for item in users:
            self._append_user(item)

    def _remove_user_callback(self, user: str) -> None:
        self._remove_user(user)
