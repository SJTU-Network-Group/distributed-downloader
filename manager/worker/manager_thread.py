import socket
import threading
from pprint import pprint
from copy import deepcopy
from colorama import Fore, Style


class ManagerThread(threading.Thread):
    def __init__(self,
                 server_list: list,   # 跨线程变量：server_list, 维护了可用的server的地址list
                 conn_socket: socket.socket,
                 conn_addr_tuple: tuple,
                 mutex: threading.Lock            # 互斥锁，用于确保对server_list访问的线程安全
                 ) -> None:
        threading.Thread.__init__(self)
        self.server_list = server_list
        self.mutex = mutex
        self.conn_socket = conn_socket
        self.conn_addr_tuple = conn_addr_tuple
        self.thread_id = threading.current_thread().ident  # 用于在输出中区分不同的ManagerThread

    def run(self) -> None:
        message = self.conn_socket.recv(2048).decode()
        if message == 'server_up':
            self.add_server()
        elif message == 'server_down':
            self.rm_server()
        elif message == 'ask_for_server_list':
            self.send_server_list()
        else:
            print(Fore.RED, f"ManagerThread-{str(self.thread_id)} warning -> ", Style.RESET_ALL,
                  f"meaningless message from: {self.conn_addr_tuple[0]}:{str(self.conn_addr_tuple[1])}")
        self.print_server_list()
        self.disconnect()

    def add_server(self) -> None:
        self.conn_socket.sendall("go_ahead".encode())
        target_tuple: bytes = self.conn_socket.recv(2048)
        target_tuple: tuple = eval(target_tuple.decode())
        self.mutex.acquire(timeout=5)
        # self.server_list.append(list(self.conn_addr_tuple))
        self.server_list.append(list(target_tuple))
        self.mutex.release()
        print(Fore.GREEN, f"ManagerThread-{str(self.thread_id)} succeed -> ", Style.RESET_ALL,
              f"add server: {self.conn_addr_tuple[0]}:{str(self.conn_addr_tuple[1])}")

    def rm_server(self) -> None:
        self.conn_socket.sendall("go_ahead".encode())
        target_tuple: bytes = self.conn_socket.recv(2048)
        target_tuple: tuple = eval(target_tuple.decode())
        self.mutex.acquire(timeout=5)
        try:
            self.server_list.remove(list(target_tuple))
        except:
            pass
        self.mutex.release()
        print(Fore.GREEN, f"ManagerThread-{str(self.thread_id)} succeed -> ", Style.RESET_ALL,
              f"remove server: {target_tuple[0]}:{str(target_tuple[1])}")

    def send_server_list(self) -> None:
        self.mutex.acquire(timeout=5)
        server_list_copy = deepcopy(self.server_list)  # 深拷贝：这样不会因为发送的阻塞而阻塞互斥锁
        self.mutex.release()
        self.conn_socket.sendall(str(server_list_copy).encode())
        print(Fore.GREEN, f"ManagerThread-{str(self.thread_id)} succeed -> ", Style.RESET_ALL,
              f"server_list sent to: {self.conn_addr_tuple[0]}:{str(self.conn_addr_tuple[1])}")


    def print_server_list(self) -> None:
        self.mutex.acquire(timeout=5)
        pprint(self.server_list)
        self.mutex.release()

    def disconnect(self) -> None:
        self.conn_socket.shutdown(socket.SHUT_RDWR)
        self.conn_socket.close()
        print(Fore.GREEN, f"ManagerThread-{str(self.thread_id)} succeed -> ", Style.RESET_ALL,
              f"disconnected from: {self.conn_addr_tuple[0]}:{str(self.conn_addr_tuple[1])}")
