"""Code to show the main window UI"""
import tkinter as tk
from .client import ActiveClient

class main_window():
    def __init__(self, client: ActiveClient) -> None:
        self.client = client
        self.client.send_message("Hello server!")

        self.main_window = tk.Tk()

        label = tk.Label(self.main_window, text=f"Welcome {client.user_details.username}!",
                         font=("Arial", 26))
        label.pack()

        self.message = tk.Entry(self.main_window)
        self.message.pack()

        btn = tk.Button(self.main_window, text="send message", command=self._btn_clicked)
        btn.pack()

        self.main_window.mainloop()

    def _btn_clicked(self) -> None:
        self.client.send_message(self.message.get())
