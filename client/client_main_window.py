"""Code to show the main window UI"""
from mttkinter import mtTkinter as tk
from .client import ActiveClient,EventCallbacks
from shared_server_client_coms.commands import CommandSendChat

class main_window():
    def __init__(self, client: ActiveClient) -> None:
        self.client = client

        callbacks = EventCallbacks(
            None,
            None,
            self._connection_error_callback,
            None,
            self._message_recieved_callback)

        client.register_event_callback(callbacks)

        self.main_window = tk.Tk()

        #Left portion of the window
        main_frame = tk.Frame(self.main_window)
        label = tk.Label(main_frame, text=f"Welcome {client.get_username()}!",
                         font=("Arial", 26))
        label.pack()
        main_frame.grid(row=0,column=0,sticky="nws")
        self.main_window.columnconfigure(0,weight=8)
        self.main_window.columnconfigure(1,weight=2)

        #Chat frame
        self.chat_frame = tk.Frame(self.main_window)
        self.message = tk.Entry(self.chat_frame)
        self.message.grid(row=0, column=0)
        self.message.bind("<Return>", self._btn_clicked)

        self.chat_field = tk.Listbox(self.chat_frame,width=15)
        self.chat_field.grid(row=1, column=0)
        
        scrollbar = tk.Scrollbar(self.chat_field)
        scrollbar.place(relheight=1, relx=0.88)

        btn = tk.Button(self.chat_frame, text="send message", command=self.__btn_clicked)
        btn.grid(row=2, column=0)

        self.chat_frame.rowconfigure(0,weight=1)
        self.chat_frame.rowconfigure(1,weight=8)
        self.chat_frame.rowconfigure(2,weight=1)
        self.chat_frame.grid(row=0,column=1,sticky="nes")

        self.main_window.mainloop()

    def __btn_clicked(self) -> None:
        self.client.send_command(CommandSendChat(self.client.get_username(), self.message.get()))

    def _btn_clicked(self, event) -> None:
        self.__btn_clicked()

    def _message_recieved_callback(self, username: str, message: str) -> None:
        self.chat_field.insert(tk.END, f"{username}: {message}")

    def _connection_error_callback(self) -> None:
        ...
