import requests


class my_requests:
    def __init__(self) -> None:
        pass

    @staticmethod
    def request(url: str, proxies: dict = None, timeout: int = 5):
        resp = requests.Session.request(
            method='GET', url=url, proxies=proxies, timeout=timeout)
        return resp

    @classmethod
    def partial_supported(cls, url: str = None, proxies: dict = None, response: requests.Response = None) -> bool:
        if url != None:
            resp = cls().request(url=url, proxies=proxies)
        elif response != None:
            resp = response
        else:
            return False
        partial_supported = 'Accept-Ranges' in resp.headers and resp.headers['Accept-Ranges'] == 'bytes'
        return partial_supported

    @staticmethod
    def partial_request(url: str, left_point: int, right_point: int, file_path: str, proxies: dict = None, timeout=5) -> None:
        """
        此函数将被多线程执行，负责将${url}的[${left_point}, ${right_point}]比特下载为${file_path}
        """
        resp = requests.Session().request(method="GET",
                                          url=url,
                                          proxies=proxies,
                                          timeout=timeout,
                                          headers={
                                              'Range': 'bytes=%d-%d' % (left_point, right_point)},
                                          stream=True  # 分块写入，防止大文件下载导致内存溢出
                                          )
        with open(file_path, mode='wb') as wf:
            for chunk in resp.iter_content(chunk_size=5120):
                if chunk:
                    wf.write(chunk)
        resp.close()
