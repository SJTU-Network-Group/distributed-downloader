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
                 download_interval: list[int],
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

    def run(self) -> None:
        print(
            Fore.BLACK, f"Connecting to server:{self.server_addr_ipv4}..", Style.RESET_ALL)
        self.socket.connect(self.server_addr_ipv4, self.port)
        print(Fore.GREEN,
              f"Connected to server:{self.server_addr_ipv4}", Style.RESET_ALL)
        # send meta-data to server:
        download_meta_data = {}
        download_meta_data["url"] = self.url
        download_meta_data["download_interval"] = self.download_interval
        # 编码为二进制格式，才能用sendall发送
        message: bytes = str(download_meta_data).encode()
        self.socket.sendall(message)  # 阻塞，直至发送成功
        print(
            Fore.GREEN, f"Download meta-data sent to server:{self.server_addr_ipv4} successfully !", Style.RESET_ALL)
        self.receive_file_segments(self.file_path)
        self.close_connection()

    def receive_file_segment(self, file_path: str) -> None:
        buffer_size = 4096  # bytes
        print(
            Fore.CYAN, f"Start reciving file segment from server:{self.server_addr_ipv4}..", Style.RESET_ALL)
        with open(file_path, mode='wb') as wf:
            data_block = self.socket.recv(buffer_size)
            while data_block != None:
                wf.write(data_block)
                data_block = self.socket.recv(buffer_size)
        print(
            Fore.GREEN, f"Finish reciving file segment from server:{self.server_addr_ipv4}!", Style.RESET_ALL)

    def close_connection(self) -> None:
        self.socket.close()
        print(Fore.GREEN,
              f"Connection to server:{self.server_addr_ipv4} closed!")
