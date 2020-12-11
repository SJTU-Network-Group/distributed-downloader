import socket
from colorama import Fore, Style
from server.worker import server_thread


class server_daemon:
    def __init__(self,
                 server_addr_ipv4: str,  # 本机的ipv4地址
                 to_client_port: int,   # 与client的socket的通信端口
                 to_manager_port: int,  # 与manager的socket的通信端口
                 # server多线程下载的线程数(要向下传给multi_thread_download)
                 thread_number: int,
                 tmp_dir: str,          # 临时文件夹 (存放着多线程下载得到的file segments)
                 target_dir: str,       # 目标文件夹 (合并后的下载文件存放目录)
                 proxies: dict          # 下载使用的proxies
                 ) -> None:
        self.server_addr_ipv4 = server_addr_ipv4
        self.to_client_port = to_client_port
        self.to_manager_port = to_manager_port
        self.thread_number = thread_number
        self.tmp_dir = tmp_dir
        self.target_dir = target_dir
        self.proxies = proxies
        # to_client_socket的初始化
        self.to_client_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.to_client_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.to_client_socket.bind((server_addr_ipv4, to_client_port))

    def listen_for_client(self) -> None:
        self.socket.listen(5)
        print(
            f"listening on {self.server_addr_ipv4}:{str(self.server_port)}...")
        while True:
            conn_socket, client_addr_tuple = self.socket.accept()
            print(Fore.GREEN, "\nsucceed -> ", Style.RESET_ALL,
                  f"connected to client: {client_addr_tuple[0]}:{str(client_addr_tuple[1])}!")
            _server_thread = server_thread(
                tmp_dir=self.tmp_dir,
                thread_number=self.thread_number,
                proxies=self.proxies,
                conn_socket=conn_socket,
                client_addr_tuple=client_addr_tuple
            )
            _server_thread.start()

    def tell_manager_server_up(self, manager_addr_ipv4: str, manager_port: int) -> None:
        """
        这个函数负责： server向manager通报自己的ipv4_ip以及port, 并表示自己可以服务
        """

        # 初始化连接到manager的socket
        to_manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        to_manager_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        to_manager_socket.bind((self.server_addr_ipv4, self.to_client_port))

        # 连接到manager
        print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
              f"connect to manager: {manager_addr_ipv4}:{str(manager_port)}...")
        to_manager_socket.connect((manager_addr_ipv4, manager_port))
        print(Fore.GREEN, "succeed -> ",
              Style.RESET_ALL, "connection established")

        # 发送消息，表示上线
        print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
              f"send 'server up' to manager: {manager_addr_ipv4}:{str(manager_port)}...")
        to_manager_socket.send("server_up".encode())
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL, "sent")

        # 消息发送完成，关闭连接，销毁socket
        print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
              f"disconnect from: {manager_addr_ipv4}:{str(manager_port)}...")
        to_manager_socket.shutdown(socket.SHUT_RDWR)
        to_manager_socket.close()
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL, "disconnected")

    def tell_manager_server_down(self, manager_addr_ipv4: str, manager_port: int) -> None:
            """
            这个函数负责： server向manager通报自己的ipv4_ip以及port, 并表示自己下线了
            """

            # 初始化连接到manager的socket
            to_manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            to_manager_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            to_manager_socket.bind((self.server_addr_ipv4, self.to_client_port))

            # 连接到manager
            print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
                f"connect to manager: {manager_addr_ipv4}:{str(manager_port)}...")
            to_manager_socket.connect((manager_addr_ipv4, manager_port))
            print(Fore.GREEN, "succeed -> ",
                Style.RESET_ALL, "connection established")

            # 发送消息，表示下线
            print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
                f"send 'server down' to manager: {manager_addr_ipv4}:{str(manager_port)}...")
            to_manager_socket.send("server_down".encode())
            print(Fore.GREEN, "succeed -> ", Style.RESET_ALL, "sent")

            # 消息发送完成，关闭连接，销毁socket
            print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
                f"disconnect from: {manager_addr_ipv4}:{str(manager_port)}...")
            to_manager_socket.shutdown(socket.SHUT_RDWR)
            to_manager_socket.close()
            print(Fore.GREEN, "succeed -> ", Style.RESET_ALL, "disconnected")
