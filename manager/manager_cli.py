import yaml
import sys
import os
from utils.file_tools import MyFileTools
from manager.worker.manager_daemon import ManagerDaemon
from utils.requests import MyRequests
from colorama import Fore, Style
import socket


if __name__ == "__main__":
    with open('./config/manager_config.yml', 'r') as f:
        config = yaml.load(f, yaml.FullLoader)
    manager_addr_ipv4 = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                                     if not ip.startswith("127.")][:1],
                                    [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
                                      for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    manager = ManagerDaemon(manager_addr_ipv4=manager_addr_ipv4, listen_port=config['MANAGER_PORT'])
    manager.listen()
