import socket
import colorama
import threading


class server_thread(threading.Thread):
    def __init__(self, 
                 tmp_dir: str,
                 thread_number: int, 
                 proxies: dict,
                 conn_socket: socket.socket, 
                 client_addr_tuple :tuple
                ) -> None:
        self.socket = conn_socket
        self.client_addr_tuple = client_addr_tuple
        self.thread_number = thread_number
        self.proxies = proxies
        self.tmp_dir = tmp_dir

    def run(self) -> None:
        