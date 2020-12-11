import sys
from colorama import Fore, Style


class MyDistributor:
    def __init__(self) -> None:
        pass

    @staticmethod
    def download_interval_list(left_point: int, right_point: int, number_of_parts: int) -> list[list]:
        """
        此函数将[left_point, right_point]区间分为number_of_parts块，并返回list[number_of_parts][2]
        """
        length = right_point - left_point + 1
        if length < number_of_parts:
            # error - 分快数大于文件大小，以至于无法分块
            print(Fore.RED, "error -> ", Style.RESET_ALL, "number of parts > file size")
            sys.exit(0)
        base_interval = length // number_of_parts
        remainder = length % number_of_parts
        size_list = [base_interval] * number_of_parts
        while remainder != 0:
            for i in range(number_of_parts):
                size_list[i] += 1
                remainder -= 1
                if remainder == 0:
                    break
        for i in range(1, number_of_parts):
            size_list[i] += size_list[i - 1]
        interval_list = [[0] * 2 for _ in range(number_of_parts)]
        for i in range(number_of_parts):
            if i == 0:
                interval_list[i][1] = size_list[0] - 1
            else:
                interval_list[i][0] = size_list[i-1]
                interval_list[i][1] = size_list[i] - 1
        return interval_list
