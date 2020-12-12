import socket
import sys
import threading
from pprint import pprint
from colorama import Fore, Style
from utils.requests import MyRequests
from utils.distributor import MyDistributor
from utils.file_tools import MyFileTools
from client.worker.client_thread import ClientThread


class ClientDaemon:
    def __init__(self,
                 url: str,
                 # client ipv4地址
                 client_addr_ipv4: str,
                 # client连接server的socket的断口(from config file)
                 to_server_port: int,
                 # client连接manager的socket的断口(from config file)
                 to_manager_port: int,
                 # 合并之后的下载好的文件的`路径/文件名`(from config file)
                 final_file_path: str,
                 # file segments(各个server下载的)的存储文件夹(from config file)
                 tmp_dir: str,
                 # (from config file)
                 proxies: dict = None
                 ) -> None:
        self.url = url
        self.client_addr_ipv4 = client_addr_ipv4
        self.to_server_port = to_server_port
        self.to_manager_port = to_manager_port
        self.tmp_dir = tmp_dir
        self.final_file_path = final_file_path
        self.proxies = proxies

        self.server_list = None

    def ask_manager_for_server_list(self, manager_addr_ipv4: str, manager_port: int) -> None:
        """
            联系manager, 获得可用的server的地址、端口清单
            存放在self.server_list里面(所以return None)
            self.server_list格式为: [(server的ipv4地址: str, server的端口号: int),...]
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
              f"send 'ask for server list' to manager: {manager_addr_ipv4}:{str(manager_port)}...")
        to_manager_socket.sendall("ask_for_server_list".encode())
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL, "sent")

        # 接收server_list
        print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
              f"receive server_list from manager: {manager_addr_ipv4}:{str(manager_port)}...")
        self.server_list: bytes = to_manager_socket.recv(4096)
        self.server_list: str = self.server_list.decode()
        self.server_list: list = eval(self.server_list)
        if not self.server_list:
            print(Fore.RED, "warning -> ",
                  Style.RESET_ALL, "server_list is None")
            sys.exit(0)
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL,
              "server_list has been received")
        pprint(self.server_list)

        # 接收完成，关闭连接，销毁socket
        print(Fore.YELLOW, "\ntrying -> ", Style.RESET_ALL,
              f"disconnect from: {manager_addr_ipv4}:{str(manager_port)}...")
        to_manager_socket.shutdown(socket.SHUT_RDWR)
        to_manager_socket.close()
        print(Fore.GREEN, "succeed -> ", Style.RESET_ALL, "disconnected")

    def connect_to_servers_and_download(self) -> None:
        """
            (主函数，调用之前必须先调用ask_manager_for_server_list来获取self.server_list)
            该函数为每一个server创建一个线程去连接，然后完成file segments的获取
            最后合并file segments得到最终文件，路径为self.final_file_path
            """
        print(Fore.YELLOW, f"\nclient daemon trying -> ", Style.RESET_ALL,
              f"connect to servers and begin distributed downloading")
        # 取得file_size来获得下载区间
        download_interval_list = self._get_download_interval_for_servers()
        # 创建多个线程，连接到每一个server，进行下载
        for index, server_addr_tuple in enumerate(self.server_list):
            download_interval = download_interval_list[index]
            _client_thread = ClientThread(
                index,
                self.url,
                tuple(server_addr_tuple),
                download_interval,
                self.tmp_dir + 'segment_' + str(index),
                self.client_addr_ipv4,
                self.to_server_port
            )
            _client_thread.start()
        # 等待所有线程结束
        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()
        print(Fore.GREEN, f"\nclient daemon succeed -> ", Style.RESET_ALL,
              "file segments have been received")

        # 下载完成，合并所有的file segments
        print(Fore.YELLOW, f"\nclient daemon trying -> ", Style.RESET_ALL,
              "merge file segments...")
        segment_file_path_list = [self.tmp_dir + 'segment_' + str(index) for index in range(len(self.server_list))]
        MyFileTools.append_file(
              src_path_list=segment_file_path_list,
              tar_path=self.final_file_path
        )
        # 合并完成，删除所有的file segments
        for f in segment_file_path_list:
            MyFileTools.delete_file(f)
        print(Fore.GREEN, f"\nclient daemon succeed -> ", Style.RESET_ALL,
              "file segments have been merged")

    def _get_download_interval_for_servers(self) -> list:
        print(Fore.YELLOW, f"client daemon trying -> ", Style.RESET_ALL,
              "get download intervals for servers...")
        resp = MyRequests.head(url=self.url, proxies=self.proxies)
        file_size = int(resp.headers['Content-Length'])
        download_interval_list = MyDistributor.download_interval_list(
            left_point=0,
            right_point=file_size - 1,
            number_of_parts=len(self.server_list)
        )
        print(Fore.GREEN, f"client daemon succeed -> ", Style.RESET_ALL,
              "have gotten download intervals for servers")
        return download_interval_list
