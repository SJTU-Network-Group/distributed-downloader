import socket
from time import thread_time
from colorama import Fore, Style
from server.worker import server_thread

class server_daemon:
    def __init__(self, 
                 server_addr_ipv4: str, 
                 server_port: str, 
                 thread_number: int,    # server多线程下载的线程数(要向下传给multi_thread_download)
                 tmp_dir: str,          # 临时文件夹 (存放着多线程下载得到的file segments)
                 target_dir: str,       # 目标文件夹 (合并后的下载文件存放目录)
                 proxies: dict          # 下载使用的proxies
                ) -> None:
        self.server_addr_ipv4 = server_addr_ipv4
        self.server_port = server_port
        self.thread_number = thread_number  
        self.tmp_dir = tmp_dir
        self.target_dir = target_dir
        self.proxies = proxies
        # socket初始化
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((server_addr_ipv4, server_port))

    def listen(self) -> None:
        self.socket.listen(5)
        print(f"listening on {self.server_addr_ipv4}:{self.server_port}...")
        while True:
            client_socket, client_addr_tuple = self.socket.accept()
            _server_thread = server_thread(
                tmp_dir=self.tmp_dir,
                thread_number=self.thread_number,
                proxies=self.proxies,
                client_socket=client_socket,
                client_addr_tuple=client_addr_tuple
            )
            _server_thread.start()
