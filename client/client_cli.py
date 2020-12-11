import yaml
import sys
import os
from utils.file_tools import my_file_tools
from client.worker.client_daemon import client_daemon
from utils.requests import my_requests
from colorama import Fore, Style
from utils.downloader import my_downloader


if __name__ == '__main__':
    with open('../config/client_config.yml', 'r') as f:
        config = yaml.load(f, yaml.FullLoader)
    file_tools = my_file_tools()
    file_tools.create_dir(config['TEMP_DIR'])
    if config['DOWNLOAD_DIR'] is not None:
        file_tools.create_dir(config['DOWNLOAD_DIR'])
    else:
        print(Fore.RED, "error -> ", Style.RESET_ALL,
              "please give download path in config file.")
    assert len(sys.argv) >= 2, 'must give urls that need to download.'
    url = sys.argv[1]
    client = client_daemon(url)
    client.fetch_server_list((config['TRACKER_HOST'], config['TRACKER_PORT']), config['CLIENT_TRACKER_BIND_PORT'])

    request = my_requests()
    response = request.request(url=url, proxies=config['PROXY'])
    request.close_request(response)

    filesize = int(response.headers['Content-Length'])
    filename = os.path.basename(url.replace("%20", "_"))
    filepath = os.path.join(config['DOWNLOAD_DIR'], filename)

    if response.headers['Accept-Ranges'] != 'bytes':
        print(Fore.RED, "error -> ", Style.RESET_ALL,
              "This download URL does not support range download! Using single thread download on client machine.")


