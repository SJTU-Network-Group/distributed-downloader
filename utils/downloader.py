import threading
from colorama import Fore, Style  # 骚气的输出，用来强调warning信息
from utils.requests import MyRequests
from utils.file_tools import MyFileTools
from utils.distributor import MyDistributor


class MyDownloader:
    def __init__(self) -> None:
        self.url: str = ''
        self.tmp_dir: str = ''          # 临时文件夹 (存放着多线程下载得到的file segments)
        self.target_dir: str = ''       # 目标文件夹 (合并后的下载文件存放目录)
        self.file_name: str = ''        # 目标文件名 (合并后的下载文件名)
        self.left_point: int = -1
        self.right_point: int = -1
        self.thread_number: int = -1    # 多线程下载中的线程个数，在server的config文件中声明
        self.proxies: dict = {}

    def _single_thread_download(self) -> None:
        """
        工具函数（不对外暴露）
        负责单线程下载，用于多线程下载不被支持时
        """
        print(Fore.RED, "Multi-threaded downloading is not supported by ",
              self.url, ".\nDownloading will be single-threaded.", Style.RESET_ALL)
        MyRequests.partial_request(url=self.url,
                                   left_point=self.left_point,
                                   right_point=self.right_point,
                                   file_path=self.target_dir + self.file_name,  # 目标文件存储位置
                                   proxies=self.proxies)

    def _multi_thread_download(self, download_interval_list) -> None:
        """
        工具函数（不对外暴露）
        负责多线程下载, 第i个线程下载的文件为`${tmp_dir}segment_by_thread_${i}`
        """
        print(Fore.YELLOW, "trying -> ", Style.RESET_ALL,
              f"multi-threaded download ->  [{self.left_point}B,{self.right_point}B] from: {self.url}...")
        for thread_id in range(self.thread_number):
            t = threading.Thread(target=MyRequests.partial_request,
                                 name='downloader-thread-'+str(thread_id),
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
        name_list = ['downloader-thread-'+str(thread_id) for thread_id in range(self.thread_number)]
        for each in threading.enumerate():
            if each.name not in name_list:
                continue
            each.join()

    def _merge_file_segments(self) -> None:
        """
        工具函数（不对外暴露）
        负责合并多线程下载得到的file segments, 并将文件存为${target_dir}${file_name}
        """
        file_segments_list = [self.tmp_dir + 'segment_by_thread_' + str(thread_id) for thread_id in
                              range(self.thread_number)]
        MyFileTools.append_file(file_segments_list, self.target_dir + self.file_name)
        for file_segment in file_segments_list:
            MyFileTools.delete_file(file_segment)

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
        self.left_point = left_point
        self.right_point = right_point
        self.thread_number = thread_number
        self.proxies = proxies
        if MyRequests.partial_supported(url, proxies):
            # 多线程下载
            download_interval_list = MyDistributor.download_interval_list(
                left_point, right_point, self.thread_number)
            self._multi_thread_download(download_interval_list)
            self._merge_file_segments()
        else:
            # 单线程下载
            self._single_thread_download()
