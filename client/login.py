"""A module to handle client login UI"""
from mttkinter import mtTkinter as tk
from shared_server_client_coms.authenticate_params import *
from .client import ActiveClient,EventCallbacks,UserDetails
from shared_server_client_coms.authenticate_params import CreateUserStatus

class AuthenciateUser():
    """An object that handles all the ui to retrieve authenticated user details from the user"""
    def __init__(self, active_client: ActiveClient) -> None:
        self._active_client = active_client

        self.main_window = tk.Tk()
        self.main_window.title("A cool chess game...")
        self.main_window.bind("<<close_the_window>>", self._close_window)

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

        self._active_client.register_event_callback(EventCallbacks(
            self._auth_response_callback,
            self._succesful_connection_callback,
            self._connection_error_callback,
            self._create_user_response_callback))

        self.main_window.mainloop()

    def _close_window(self, event) -> None:
        self.main_window.destroy()

    def _handle_signup_button_click(self) -> None:
        self.my_password_entry["state"] = "disable"
        self.my_user_name_entry["state"] = "disable"
        self.server_status_label["text"] = ""

        self._active_client.create_user(UserDetails(
            self.my_user_name_entry.get(),self.my_password_entry.get()))

    def _handle_login_button_click(self) -> None:
        self.my_password_entry["state"] = "disable"
        self.my_user_name_entry["state"] = "disable"
        self.server_status_label["text"] = ""

        self._active_client.authenticate_user(UserDetails(
            self.my_user_name_entry.get(),self.my_password_entry.get()))

    def _succesful_connection_callback(self) -> None:
        self.server_status_label["text"] = "server_contact_success"

    def _connection_error_callback(self) -> None:
        self.server_status_label["text"] = "server_contact_failed"

    def _auth_response_callback(self, status: AuthStatus) -> None:
        if status == AuthStatus.SUCCESS:
            self.main_window.event_generate("<<close_the_window>>")

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

    def _create_user_response_callback(self, status: CreateUserStatus) -> None:
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
