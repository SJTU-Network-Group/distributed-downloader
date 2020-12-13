import threading
from test import tqdm_thread


if __name__ == "__main__":
    for i in range(4):
        t = tqdm_thread.TqdmMulti()
        t.start()