import socket
from colorama import Fore, Style


class client_daemon:
    def __init__(self, 
                 url: str, 
                 client_addr_ipv4: str, 
                 to_server_port: int,
                 to_manager_port: int 
                ) -> None:
        self.url = url
        self.client_addr_ipv4 = client_addr_ipv4
        self.to_server_port = to_server_port
        self.to_manager_port = to_manager_port

    def ask_manager_for_server_list(self, manager_addr_ipv4: str, manager_port: int) -> None:
        """
        这个函数负责： 联系manager, 获得可用的server的地址、端口清单
        """

        # 初始化连接到manager的socket
        to_manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        to_manager_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        to_manager_socket.bind((self.client_addr_ipv4, self.to_manager_port))

        # 连接到manager
        print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
              f"connect to manager: {manager_addr_ipv4}:{str(manager_port)}...")
        to_manager_socket.connect((manager_addr_ipv4, manager_port))
        print(Fore.GREEN, "succeed -> ",
              Style.RESET_ALL, "connection established")

        # 发送消息，请求server list
        print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
              f"send 'server up' to manager: {manager_addr_ipv4}:{str(manager_port)}...")
        to_manager_socket.send("server_up".encode())
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL, "sent")
