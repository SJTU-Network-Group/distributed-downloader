import sys
from utils.file_tools import MyFileTools
from server.worker.server_daemon import ServerDaemon
import yaml
from colorama import Fore, Style
import socket


def create_work_dir() -> None:
    """
    This function is aimed to create some useful dir for working.
    """
    if config['TARGET_DIR'] is not None:
        MyFileTools.create_dir(config['TARGET_DIR'])
    else:
        print(Fore.RED, "error -> ", Style.RESET_ALL,
              "please give download path in config file.")
        sys.exit(1)
    if config['TMP_DIR'] is not None:
        MyFileTools.create_dir(config['TMP_DIR'])
    else:
        print(Fore.RED, "error -> ", Style.RESET_ALL,
              "please give temp path in config file.")
        sys.exit(1)


if __name__ == "__main__":
    with open('./config/server_config.yml', 'rt') as rf:
        config = yaml.load(rf, yaml.FullLoader)
    create_work_dir()
    server_addr_ipv4 = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                                     if not ip.startswith("127.")][:1],
                                    [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
                                      for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    server = ServerDaemon(server_addr_ipv4=server_addr_ipv4, to_client_port=config['TO_CLIENT_PORT'],
                          to_manager_port=config['TO_MANAGER_PORT'], thread_number=config['THREAD_NUM'],
                          tmp_dir=config['TMP_DIR'], target_dir=config['TARGET_DIR'], proxies=config['PROXIES'])
    server.tell_manager_server_up(config['MANAGER_ADDR_IPV4'], config['MANAGER_PORT'])
    server.listen_for_client()
    # TODO: user gives instruction to jump this listen loop.
