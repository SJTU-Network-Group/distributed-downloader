import os
import shutil


class MyFileTools:
    """
    这个类封装了一些本项目中需要的文件处理手段
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def append_file(src_path_list: list, tar_path: str) -> None:
        # 以二进制的形式将src_path_list的内容逐一追加到tar_path末尾
        with open(tar_path, mode='wb') as wf:
            for src_path in src_path_list:
                with open(src_path, mode='rb') as rf:
                    shutil.copyfileobj(rf, wf)

    @staticmethod
    def delete_file(path: str) -> None:
        os.remove(path)

    @staticmethod
    def create_dir(dirname: str):
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    @staticmethod
    def rm_dir(dirname: str):
        if not os.path.exists(dirname):
            os.rmdir(dirname)
