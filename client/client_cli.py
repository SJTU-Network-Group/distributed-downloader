import yaml
import sys
import os
from utils.file_tools import MyFileTools
from client.worker.client_daemon import ClientDaemon
from utils.requests import MyRequests
from colorama import Fore, Style
from utils.downloader import MyDownloader


if __name__ == '__main__':
    with open('../config/client_config.yml', 'r') as f:
        config = yaml.load(f, yaml.FullLoader)
    file_tools = MyFileTools()
    file_tools.create_dir(config['TEMP_DIR'])
    if config['DOWNLOAD_DIR'] is not None:
        file_tools.create_dir(config['DOWNLOAD_DIR'])
    else:
        print(Fore.RED, "error -> ", Style.RESET_ALL,
              "please give download path in config file.")
    assert len(sys.argv) >= 2, 'must give urls that need to download.'
    url = sys.argv[1]
    client = ClientDaemon(url)
    client.fetch_server_list((config['TRACKER_HOST'], config['TRACKER_PORT']), config['CLIENT_TRACKER_BIND_PORT'])

    request = MyRequests()
    response = request.request(url=url, proxies=config['PROXY'])
    request.close_request(response)

    filesize = int(response.headers['Content-Length'])
    filename = os.path.basename(url.replace("%20", "_"))
    filepath = os.path.join(config['DOWNLOAD_DIR'], filename)

    if response.headers['Accept-Ranges'] != 'bytes':
        print(Fore.RED, "error -> ", Style.RESET_ALL,
              "This download URL does not support range download! Using single thread download on client machine.")


