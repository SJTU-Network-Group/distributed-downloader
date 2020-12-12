import yaml
import sys
import os
from utils.file_tools import MyFileTools
from client.worker.client_daemon import ClientDaemon
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


if __name__ == '__main__':
    with open('../config/client_config.yml', 'rt') as rf:
        config = yaml.load(rf, yaml.FullLoader)
    create_work_dir()

    assert len(sys.argv) >= 2, 'must give urls that need to download.'
    url = sys.argv[1]
    client_addr_ipv4 = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                                     if not ip.startswith("127.")][:1],
                                    [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
                                      for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    filename = os.path.basename(url.replace("%20", "_"))
    # TODO: change filename to the real file type (ref: requests.header)

    client = ClientDaemon(url=url,
                          client_addr_ipv4=client_addr_ipv4,
                          to_server_port=config['TO_SERVER_PORT'],
                          to_manager_port=config['TO_MANAGER_PORT'],
                          final_file_path=config['TARGET_DIR'] + filename,
                          tmp_dir=config['TMP_DIR'],
                          proxies=config['PROXIES']
                          )
    client.ask_manager_for_server_list(manager_addr_ipv4=config['MANAGER_ADDR_IPV4'], manager_port=config['MANAGER_PORT'])

    client.connect_to_servers_and_download()

    print("to delete")
    MyFileTools.rm_dir(config['TMP_DIR'])
    print("deleted")
