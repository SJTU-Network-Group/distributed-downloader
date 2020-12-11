import socket


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

    def ask_manager_for_server_list(self, track_address: str, client_tracker_bind_port: str) -> None:
        """
        这个函数负责： 联系manager, 获得可用的server的地址、端口清单
        """

        # 初始化连接到manager的socket
        to_manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        to_manager_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        to_manager_socket.bind((self.client_addr_ipv4, self.to_manager_port))
