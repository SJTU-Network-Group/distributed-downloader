import socket     
import sys        # 错误时退出
import uuid       # 生成唯一的下载文件名
import threading
from colorama import Fore, Style
from utils.downloader import my_downloader  
from utils.file_tools import my_file_tools  # 传输完成后删除服务端文件

class server_thread(threading.Thread):
    def __init__(self,
                 tmp_dir: str,
                 target_dir: str,
                 thread_number: int,
                 proxies: dict,
                 conn_socket: socket.socket,
                 client_addr_tuple: tuple
                 ) -> None:
        self.tmp_dir = tmp_dir
        self.target_dir = target_dir
        self.thread_number = thread_number
        self.proxies = proxies
        self.socket = conn_socket
        self.client_addr_tuple = client_addr_tuple

    def run(self) -> None:
        # 接受meta-data:
        print(Fore.LIGHTYELLOW_EX,
              f"waiting for meta-data from client: {self.client_addr_tuple[0]}:{str(self.client_addr_tuple[1])}...", Style.RESET_ALL)
        meta_data: bytes = self.socket.recv(bufsize=2048)
        meta_data: str = meta_data.decode()
        meta_data: dict = eval(meta_data)
        if not ('url' in meta_data and 'download_interval' in meta_data):
            print(Fore.RED, "error -> ", Style.RESET_ALL, "meta-data corrupted!")
            sys.exit(0)
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL,
              "meta-data is recieved successfully:")
        print(meta_data)

        # 开始下载片段
        url = meta_data['url']
        left_point = meta_data['download_interval'][0]
        right_point = meta_data['download_interval'][1]
        # 使用uuid生成一个唯一的文件名
        file_name = str(uuid.uuid1())
        # 阻塞，直到下载结束，下载好的文件路径为`target_dir + file_name`
        my_downloader().download(url=url,
                                 tmp_dir=self.tmp_dir,
                                 target_dir=self.target_dir,
                                 file_name=file_name,
                                 left_point=left_point,
                                 right_point=right_point,
                                 thread_number=self.thread_number,
                                 proxies=self.proxies
                                 )

        # 下载完成，开始传输文件到client
        self.send_file_segment(self.target_dir + file_name)

        # 关闭socket
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL,
              f"socket to : {self.client_addr_tuple[0]}:{str(self.client_addr_tuple[1])} closed!")

        # 删除文件
        my_file_tools.delete_file(self.target_dir + file_name)
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL, "file segment deleted")

    def send_file_segment(self, file_path: str):
        with open(file_path, mode='rb') as rf:
            buffer = rf.read(2048)
            while buffer:
                self.socket.sendall(buffer)
                buffer = rf.read(2048)
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL,
              f"file segment sent to client: {self.client_addr_tuple[0]}:{str(self.client_addr_tuple[1])}!")
