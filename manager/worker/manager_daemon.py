import socket
import sys
import threading
from pprint import pprint
from colorama import Fore, Style
from utils.requests import MyRequests
from utils.distributor import MyDistributor
from utils.file_tools import MyFileTools
from manager.worker.manager_thread import ManagerThread


class ManagerDaemon:
    def __init__(self,
                 manager_addr_ipv4: str,
                 listen_port: int        # manager
                 ) -> None:
        self.manager_addr_ipv4 = manager_addr_ipv4
        self.listen_port = listen_port

        # 初始化监听的socket
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind((self.manager_addr_ipv4, self.listen_port))

        self.mutex = threading.Lock()
        self.server_list = []  # 格式为: [(server的ipv4地址: str, server的端口号: int),...]

    def listen(self) -> None:
        self.listen_socket.listen(5)
        print(
            f"listening on {self.manager_addr_ipv4}:{str(self.listen_port)}...")
        while True:
            conn_socket, conn_addr_tuple = self.listen_socket.accept()
            print(Fore.GREEN, "\nsucceed -> ", Style.RESET_ALL,
                  f"connected to : {conn_addr_tuple[0]}:{str(conn_addr_tuple[1])}")
            _manager_thread = ManagerThread(
                server_list=self.server_list,
                conn_socket=conn_socket,
                conn_addr_tuple=conn_addr_tuple,
                mutex=self.mutex
            )
            _manager_thread.start()
