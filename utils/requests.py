import requests


class my_requests:
    def __init__(self) -> None:
        pass


    def request(self, url: str, proxies: dict=None, timeout :int=5):
        resp = requests.Session.request(method='GET', url=url, proxies=proxies, timeout=timeout)
        return resp


    def partial_supported(self, url :str, proxies :dict=None) -> bool:
        resp = self.request(url=url, proxies=proxies)
        partial_supported =  'Accept-Ranges' in resp.headers and resp.headers['Accept-Ranges'] == 'bytes'
        return partial_supported


    def partial_request(self, url: str, left_point: int, right_point: int, file_path: str, proxies: dict=None, timeout=5) -> None:
        resp = requests.Session.request(method="GET", 
                                        url=url, 
                                        proxies=proxies, 
                                        timeout=timeout, 
                                        headers={'Range': 'bytes=%d-%d' % (left_point, right_point)}
                                        )
        # TODO: downloading process to be finished 
        resp.close()
    