import yaml
import sys
from utils.file_tools import my_file_tools
from client.worker.client_daemon import client_daemon
from utils.requests import my_requests


if __name__ == '__main__':
    with open('../config/client_config.yml', 'r') as f:
        config = yaml.load(f, yaml.FullLoader)
    file_tools = my_file_tools()
    my_file_tools.create_dir(config['TEMP_DIR'])
    if config['DOWNLOAD_DIR'] is not None:
        my_file_tools.create_dir(config['DOWNLOAD_DIR'])
    assert len(sys.argv) >= 2, 'must give urls that need to download.'
    url = sys.argv[1]
    client = client_daemon(url)
    client.fetch_server_list((config['TRACKER_HOST'], config['TRACKER_PORT']), config['CLIENT_TRACKER_BIND_PORT'])

    request = my_requests()
    response = request.request(url=url, proxies=config['PROXY'])
