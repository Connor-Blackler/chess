"""A module to handle client login UI"""
import tkinter as tk
from shared_server_client_coms.authenticate_params import *
from .client import SubmitClientEventWrapper,ActiveClient
from shared_server_client_coms.authenticate_params import CreateUserStatus

class AuthenciateUser():
    """An object that handles all the ui to retrieve authenticated user details from the user"""
    def __init__(self) -> None:
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

        login_signup_frame = tk.Frame()
        my_sign_up_button = tk.Button(login_signup_frame, text="Sign up",
                                      command=self._handle_signup_button_click)
        my_sign_up_button.grid(row=2,column=0,padx=24)

        my_login_button = tk.Button(login_signup_frame, text="Login",
                                    command=self._handle_login_button_click)
        my_login_button.grid(row=2,column=1,padx=24)
        login_signup_frame.pack(padx=20, pady=10)

        self.server_status_label = tk.Label(self.main_window, text="", font=('Arial', 9))
        self.server_status_label.pack(padx=20, pady=10)

        self._active_client = ActiveClient(SubmitClientEventWrapper(
            "","",self._auth_response))
        
        self.main_window.mainloop()

    def _handle_signup_button_click(self) -> None:
        self.my_password_entry["state"] = "disable"
        self.my_user_name_entry["state"] = "disable"
        self.server_status_label["text"] = ""

        self._active_client.create_user(SubmitClientEventWrapper(
            self.my_user_name_entry.get(),self.my_password_entry.get(),self._create_user_response))

    def _handle_login_button_click(self) -> None:
        self.my_password_entry["state"] = "disable"
        self.my_user_name_entry["state"] = "disable"
        self.server_status_label["text"] = ""

        self._active_client.authenticate_user(SubmitClientEventWrapper(
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

    def _create_user_response(self, status: CreateUserStatus) -> None:
        if status == CreateUserStatus.SUCCESS:
            self.server_status_label["text"] = "user_creation_successful"
            self.my_password_entry["state"] = "normal"
            self.my_user_name_entry["state"] = "normal"

        elif status == CreateUserStatus.USERNAME_TAKEN:
            self.server_status_label["text"] = "user_creation_username_taken"
            self.my_password_entry["state"] = "normal"
            self.my_user_name_entry["state"] = "normal"

        elif status == CreateUserStatus.NETWORK_ERROR:
            self.server_status_label["text"] = "network_error"
            self.my_password_entry["state"] = "normal"
            self.my_user_name_entry["state"] = "normal"

    def retrieve_client(self) -> ActiveClient:
        """Retrieve the Authclient populated by the user"""
        return self._active_client
