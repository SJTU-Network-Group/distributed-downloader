import sys
from colorama import Fore, Style


class my_distributer:
    def __init__(self) -> None:
        pass

    @staticmethod
    def download_interval_for_threads(left_point: int, right_point: int, thread_number: int) -> list[list]:
        """
        此函数将[left_point, right_point]区间分为thread_number块，并返回list[thread_number][2]
        """
        length = right_point - left_point + 1
        if length < thread_number:
            #! error - 线程数大于文件大小，以至于无法分块
            print(Fore.BLUE, "thread number is too large", Style.RESET_ALL)
            sys.exit(0)
        base_interval = length // thread_number
        remainder = length % thread_number
        size_list = [base_interval] * thread_number
        while remainder != 0:
            for i in range(thread_number):
                size_list[i] += 1
                remainder -= 1
                if remainder == 0:
                    break
        for i in range(1, thread_number):
            size_list[i] += size_list[i - 1]
        interval_list = [[0] * 2 for _ in range(thread_number)]
        for i in range(thread_number):
            if i == 0:
                interval_list[i][1] = size_list[0] - 1
            else:
                interval_list[i][0] = size_list[i-1]
                interval_list[i][1] = size_list[i] - 1
        return interval_list
