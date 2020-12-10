import os 
import shutil

class my_file_tools:
    '''
    这个类封装了一些本项目中需要的文件处理手段
    '''
    def __init__(self) -> None:
        pass

    def append_file(self, src_path_list : list[str], tar_path : str) -> None:
        # 以二进制的形式将src_path_list的内容逐一追加到tar_path末尾
        with open(tar_path, mode='wb') as wf:
            for src_path in src_path_list:
                with open(src_path, mode='rb') as rf:
                    shutil.copyfileobj(src_path, tar_path)

    def delete_file(self, path : str) -> None:
        # 删除path指定的文件
        os.remove(path)

