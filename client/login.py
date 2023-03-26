"""A module to handle client login UI"""
import tkinter as tk
from shared_server_client_coms.authenticate_params import AuthStatus
from .client import AuthClientEventWrapper,ActiveClient

class AuthenciateUser():
    """An object that handles all the ui to retrieve authenticated user details from the user"""
    def __init__(self) -> None:
        self._active_client = ActiveClient(AuthClientEventWrapper(
            "","",self._auth_response))

        self.main_window = tk.Tk()
        self.main_window.title("A cool chess game...")

        my_label = tk.Label(self.main_window, text="Welcome to a cool Chess game!",
                            font=('Arial', 18))
        my_label.pack(padx=20, pady=14)

        my_label = tk.Label(self.main_window, text="Please enter your username and password below",
                            font=('Arial', 14))
        my_label.pack(padx=20, pady=10)

        user_details_frame = tk.Frame()

        my_label = tk.Label(user_details_frame, text="Username:", font=('Arial', 9))
        my_label.grid(row=0,column=0)

        my_label = tk.Label(user_details_frame, text="Password:", font=('Arial', 9))
        my_label.grid(row=1,column=0)

        self.my_user_name_entry = tk.Entry(user_details_frame)
        self.my_user_name_entry.grid(row=0,column=1)

        self.my_password_entry = tk.Entry(user_details_frame, show="*")
        self.my_password_entry.grid(row=1,column=1)

        user_details_frame.pack(padx=20, pady=10)

        my_login_button = tk.Button(self.main_window, text="Login",
                                    command=self._handle_login_button_click)
        my_login_button.pack(padx=20, pady=10)

        self.server_status_label = tk.Label(self.main_window, text="", font=('Arial', 9))
        self.server_status_label.pack(padx=20, pady=10)

        self.main_window.mainloop()

    def _handle_login_button_click(self) -> None:
        self.my_password_entry["state"] = "disable"
        self.my_user_name_entry["state"] = "disable"
        self.server_status_label["text"] = ""

        self._active_client.authenticate_user(AuthClientEventWrapper(
            self.my_user_name_entry.get(),self.my_password_entry.get(),self._auth_response))

    def _auth_response(self, status: AuthStatus) -> None:
        if status == AuthStatus.SUCCESS:
            self.main_window.destroy()

        elif status == AuthStatus.INCORRECT_PASSWORD:
            self.server_status_label["text"] = "incorrect_password"
            self.my_password_entry["state"] = "normal"
            self.my_user_name_entry["state"] = "normal"

        elif status == AuthStatus.INCORRECT_USER:
            self.server_status_label["text"] = "incorrect_user"
            self.my_password_entry["state"] = "normal"
            self.my_user_name_entry["state"] = "normal"

        elif status == AuthStatus.NETWORK_ERROR:
            self.server_status_label["text"] = "network_error"
            self.my_password_entry["state"] = "normal"
            self.my_user_name_entry["state"] = "normal"

    def retrieve_client(self) -> ActiveClient:
        """Retrieve the Authclient populated by the user"""
        return self._active_client
