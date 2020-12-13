import requests
import threading
from colorama import Fore, Style
from tqdm import tqdm


class MyRequests:
    def __init__(self) -> None:
        pass

    @staticmethod
    def request(url: str, proxies: dict = None, timeout: int = 5):
        resp = requests.request(
            method='GET', url=url, proxies=proxies, timeout=timeout)
        return resp

    @staticmethod
    def head(url: str, proxies: dict = None, timeout: int = 5):
        resp = requests.head(url=url, proxies=proxies, timeout=timeout)
        return resp

    @classmethod
    def partial_supported(cls, url: str = None, proxies: dict = None, response: requests.Response = None) -> bool:
        if url is not None:
            resp = cls().head(url=url, proxies=proxies)
        elif response is not None:
            resp = response
        else:
            return False
        partial_supported = 'Accept-Ranges' in resp.headers and resp.headers['Accept-Ranges'] == 'bytes'
        return partial_supported

    @staticmethod
    def partial_request(url: str, left_point: int, right_point: int, file_path: str, proxies: dict = None,
                        timeout=20) -> None:
        """
        此函数将被多线程执行，负责将${url}的[${left_point}, ${right_point}]比特下载为${file_path}
        """

        #print(Fore.YELLOW, f"multi-threaded downloader-{str(threading.current_thread().ident)}  trying -> ", Style.RESET_ALL,
        #      f"download file segment  [{left_point}B,{right_point}B] from: {url}...")
        resp = requests.request(method="GET",
                                url=url,
                                proxies=proxies,
                                timeout=timeout,
                                headers={
                                    'Range': 'bytes=%d-%d' % (left_point, right_point)},
                                stream=True  # 分块写入，防止大文件下载导致内存溢出
                                )
        bar = tqdm(total=(right_point - left_point + 1))
        bar.unit = 'B'
        bar.unit_scale = True
        with open(file_path, mode='wb') as wf:
            for chunk in resp.iter_content(chunk_size=5120):
                bar.update(len(chunk))
                if chunk:
                    wf.write(chunk)
        resp.close()
        bar.close()
        #print(Fore.GREEN, f"multi-threaded downloader-{str(threading.current_thread().ident)}  succeed -> ",
        #      Style.RESET_ALL,
        #      f"download file segment  [{left_point}B,{right_point}B] from: {url}...")
