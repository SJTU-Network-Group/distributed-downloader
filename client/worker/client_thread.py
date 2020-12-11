import socket
import threading
from colorama import Fore, Style


class client_thread(threading.Thread):
    """
    this class provides interface to connect to server thread and download file segment
    """

    def __init__(self,
                 port: int,                       # socket端口
                 # 此thread请求的片段文件在http(s)响应体中的的比特区间
                 download_interval: tuple[int],
                 server_addr_ipv4: str,           # 此thread连接的server的ipv4地址
                 url: str,                        # 下载链接
                 file_path: str                   # 下载好的(片段)文件存储地址
                 ) -> None:
        threading.Thread.__init__(self)
        self.url = url
        self.port = port
        self.server_addr_ipv4 = server_addr_ipv4
        self.download_interval = download_interval
        self.file_path = file_path
        # initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self) -> None:
        # 连接到服务器
        self.connect_to_server()
        # 发送meta-data
        self.send_meta_data()
        # 开始接受文件
        self.receive_file_segment(self.file_path)
        # 文件接收完成，关闭socket
        self.close_connection()

    def connect_to_server(self) -> None:
        print(Fore.YELLOW, "trying -> ", Style.RESET_ALL,
              f"connect to server: {self.server_addr_ipv4}:{self.port}...")
        self.socket.connect(self.server_addr_ipv4, self.port)
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL,
              f"connect to server: {self.server_addr_ipv4}:{self.port}!")

    def send_meta_data(self) -> None:
        download_meta_data = {}
        download_meta_data["url"] = self.url
        download_meta_data["download_interval"] = self.download_interval
        message: bytes = str(download_meta_data).encode()
        # 阻塞，直至发送成功
        print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
              f"send meta-data to server: {self.server_addr_ipv4}:{self.port}...")
        self.socket.sendall(message)  
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL,
              f"meta-data have been sent: {self.server_addr_ipv4}:{self.port}!")

    def receive_file_segment(self, file_path: str) -> None:
        file_size = self.download_interval[1] - self.download_interval[0] + 1
        print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
              f"receive file segment from: {self.server_addr_ipv4}:{self.port}...")
        # 可靠接受 - 阻塞，直到接受完成
        with open(file_path, mode='wb') as wf:
            while file_size > 0:
                data_block = self.socket.recv(4096)
                wf.write(data_block)
                file_size -= len(data_block)
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL,
              f"file segment have been received from: {self.server_addr_ipv4}:{self.port}!")

    def close_connection(self) -> None:
        print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
              f"disconnect to : {self.server_addr_ipv4}:{self.port}!")
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL,
              f"disconnect to : {self.server_addr_ipv4}:{self.port}!")

