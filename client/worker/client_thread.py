import socket
import threading
from colorama import Fore, Style


class ClientThread(threading.Thread):
    """
    this class provides interface to connect to server thread and download file segment
    """

    def __init__(self,             
                 thread_id: int,                  # 用于在区分不同的线程的输出
                 url: str,                        # 下载链接
                 server_addr_tuple: tuple,        # 此thread连接的server的(ipv4地址:str, port:int)
                 download_interval: list[int],    # 此thread请求的片段文件在http(s)响应体中的的比特区间
                 file_path: str,                  # 下载好的(片段)文件存储`地址/名称`
                 client_addr_ipv4: str,           # client的ipv4地址
                 to_server_port: int              # client的socket端口
                 ) -> None:
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.url = url
        self.server_addr_tuple = server_addr_tuple
        self.download_interval = download_interval
        self.file_path = file_path

        # 初始化client的socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((client_addr_ipv4, to_server_port))

    def run(self) -> None:
        # 连接到服务器
        self.connect_to_server()
        # 发送meta-data
        self.send_meta_data()
        # 开始接受文件
        self.receive_file_segment(self.file_path)
        # 文件接收完成，关闭socket
        self.disconnect()

    def connect_to_server(self) -> None:
        print(Fore.YELLOW, f"\nthread-{str(self.thread_id)} trying -> ", Style.RESET_ALL,
              f"connect to server: {self.server_addr_tuple[0]}:{str(self.server_addr_tuple[1])}...")
        self.socket.connect(self.server_addr_tuple)
        print(Fore.GREEN, f"thread-{str(self.thread_id)} succeed -> ", Style.RESET_ALL,
              "connection established")

    def send_meta_data(self) -> None:
        download_meta_data = {"url": self.url, "download_interval": self.download_interval}
        message: bytes = str(download_meta_data).encode()
        # 阻塞，直至发送成功
        print(Fore.YELLOW, f"\nthread-{str(self.thread_id)} trying -> ", Style.RESET_ALL,
              f"send meta-data to server: {self.server_addr_tuple[0]}:{str(self.server_addr_tuple[1])}...")
        self.socket.sendall(message)  
        print(Fore.GREEN, f"thread-{str(self.thread_id)} succeed -> ", Style.RESET_ALL,
              "meta-data has been sent!")

    def receive_file_segment(self, file_path: str) -> None:
        file_size = self.download_interval[1] - self.download_interval[0] + 1
        print(Fore.YELLOW, f"\nthread-{str(self.thread_id)} trying -> ", Style.RESET_ALL,
              f"receive file segment from: {self.server_addr_tuple[0]}:{str(self.server_addr_tuple[1])}...")
        # 可靠接受 - 阻塞，直到接受完成
        with open(file_path, mode='wb') as wf:
            while file_size > 0:
                data_block = self.socket.recv(4096)
                wf.write(data_block)
                file_size -= len(data_block)
        print(Fore.GREEN, f"thread-{str(self.thread_id)} succeed -> ", Style.RESET_ALL,
              "file segment has been received!")

    def disconnect(self) -> None:
        print(Fore.YELLOW, f"\nthread-{str(self.thread_id)} trying -> ", Style.RESET_ALL,
              f"disconnect from: {self.server_addr_tuple[0]}:{str(self.server_addr_tuple[1])}...")
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print(Fore.GREEN, f"thread-{str(self.thread_id)} succeed -> ", Style.RESET_ALL,
              "disconnected")
