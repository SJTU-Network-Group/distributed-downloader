import threading
from colorama import Fore, Style  # 骚气的输出，用来强调warning信息
from utils.requests import my_requests
from utils.file_tools import my_file_tools
from utils.distributer import my_distributer


class my_downloader:
    def __init__(self) -> None:
        self.url: str = None
        self.tmp_dir: str = None  # 临时文件夹 (存放着多线程下载得到的file segments)
        self.target_dir: str = None  # 目标文件夹 (合并后的下载文件存放目录)
        self.file_name: str = None  # 目标文件名 (合并后的下载文件名)
        self.thread_number: int = None  # 多线程下载中的线程个数，在server的config文件中声明
        self.proxies: dict = None
        
    def _single_thread_download(self) -> None:
        """
        工具函数（不对外暴露）
        负责单线程下载，用于多线程下载不被支持时
        """
        my_requests.partial_request(url=self.url,
                                    left_point=self.left_point,
                                    right_point=self.right_point,
                                    file_path=self.target_dir + self.file_name,  # 目标文件存储位置
                                    proxies=self.proxies)

    def _multi_thread_download(self, download_interval_list) -> None:
        """
        工具函数（不对外暴露）
        负责多线程下载, 第i个线程下载的文件为`${tmp_dir}segment_by_thread_${i}`
        """
        for thread_id in range(self.thread_number):
            t = threading.Thread(target=my_requests.partial_request,
                                 kwargs={
                                     'url': self.url,
                                     'proxies': self.proxies,
                                     # file segments的存储路径
                                     'file_path': self.tmp_dir + 'segment_by_thread_' + str(thread_id),
                                     # 第${thread_id}个线程的下载开始比特数
                                     'left_point': download_interval_list[thread_id][0],
                                     # 第${thread_id}个线程的下载结束比特数
                                     'right_point': download_interval_list[thread_id][1]
                                 })
            t.setDaemon(True)
            t.start()
        main_thread = threading.current_thread()
        for each in threading.enumerate():
            if each is main_thread:
                continue
            each.join()

    def _merge_file_segments(self) -> None:
        """
        工具函数（不对外暴露）
        负责合并多线程下载得到的file segments, 并将文件存为${target_dir}${file_name}
        """
        with open(self.target_dir + self.file_name, mode='wb') as target_file:
            file_segments_list = [self.tmp_dir + 'segment_by_thread_' +
                                  str(thread_id) for thread_id in range(self.thread_number)]
            my_file_tools.append_file(file_segments_list, target_file)
            for file_segment in file_segments_list:
                my_file_tools.delete_file(file_segment)

    def download(self, 
                 url: str, 
                 tmp_dir: str, 
                 target_dir: str, 
                 file_name: str, 
                 left_point: int, 
                 right_point: int, 
                 thread_number: int,
                 proxies: dict = None
                ) -> None:
        """
        唯一的对外接口，由distributed-server调用，负责下载文件片段，
        对于该片段，在支持多线程下载时采用多线程下载，不支持时采用单线程下载
        """
        self.url = url
        self.tmp_dir = tmp_dir
        self.target_dir = target_dir
        self.file_name = file_name
        self.thread_number = thread_number
        self.proxies = proxies
        if my_requests.partial_supported(url, proxies) == True:
            # 多线程下载
            download_interval_list = my_distributer.download_interval_list(
                left_point, right_point, self.thread_number)
            self._multi_thread_download(download_interval_list)
            self._merge_file_segments()
        else:
            # 单线程下载
            print(Fore.RED, "Multi-threaded downloading is not supported by ",
                  url, ".\nDownloading will be single-threaded.", Style.RESET_ALL)
            self._single_thread_download(url=url)
