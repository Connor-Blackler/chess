"""A module that handles the main loop for the client connection"""

import threading
from client.client import ActiveClient

def main() -> None:
    """Main loop where the client is constructed and polled"""
    print("what is your nickname?")
    my_client = ActiveClient(nickname=input(""))

    def write(my_client: ActiveClient):
        while True:
            new_message = input("")
            if new_message == "q" or new_message == "quit":
                my_client.communication_socket.close()
                del my_client
                break

            my_client.send_message(new_message)

    write_thread = threading.Thread(target=write, args=(my_client,))
    write_thread.start()

main()
