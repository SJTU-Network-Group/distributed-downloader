import socket
import sys
import threading
from pprint import pprint
from colorama import Fore, Style
from utils.requests import MyRequests
from utils.distributer import MyDistributor
from utils.file_tools import MyFileTools
from client.worker.client_thread import ClientThread

class ManagerDaemon:
    def __init__(self,
                 manager_addr_ipv4: str,
                 to_server_port: int,
                 to_client_port: int
                 ) -> None:
        self.manager_addr_ipv4 = manager_addr_ipv4
        self.to_server_port = to_server_port
        self.to_client_port = to_client_port
        self.active_server_addr_ipv4 = []
        # IP list for active servers
        self.to_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.to_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.to_server_socket.bind((self.manager_addr_ipv4, self.to_server_port))
        self.to_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.to_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # dubious
        self.to_client_socket.bind((self.manager_addr_ipv4, self.to_client_port))

    def listen_for_client(self) -> None:
        self.to_client_socket.listen(5)  # dubious
        print(
            f"listening on {self.manager_addr_ipv4}:{str(self.to_client_port)}...")
        while True:
            conn_socket, client_addr_tuple = self.to_client_socket.accept()
            print(Fore.GREEN, "\nsucceed -> ", Style.RESET_ALL,
                  f"connected to client: {client_addr_tuple[0]}:{str(client_addr_tuple[1])}")

