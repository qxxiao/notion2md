from multiprocessing.pool import ThreadPool
import threading
import os
from queue import Queue
import requests


# 确保在执行的时候导入此文件
exported_dir = "notion2md_files"
# root_dir = os.getcwd()  # as root directory: absolute path
root_dir = os.curdir  # as root directory: relative path

# 更新 root_dir 首页写入位置
root_dir = os.path.join(root_dir, exported_dir)

if not os.path.exists(root_dir):
    os.makedirs(root_dir)
else:
    print("exported_dir already exists: {}".format(root_dir))
    # exit(1)
os.chdir(root_dir)
cur_dir = os.curdir  # . = current directory
# print(cur_dir)
# print(os.path.dirname(cur_dir))


# todo 不返回文件名, 使用默认参数的文件名(不保证重名和文件类型)
"""
file={
    url: "https://www.baidu.com",
    path: ".subpages", # cur_dir
    filename: "baidu.html",
}
"""
download_list = Queue(maxsize=500)
crt_dir_mtx = threading.Lock()


def download_file():
    global crt_dir_mtx
    while True:
        f = download_list.get()
        if f is None:
            download_list.put(None)
            return
        # download file with filename args
        # !./static
        static_dir = os.path.join(f["path"], "static")
        is_download = False
        crt_dir_mtx.acquire()
        if not os.path.exists(static_dir):
            os.mkdir(static_dir)
        # 判断文件是否存在
        elif os.path.exists(os.path.join(static_dir, f["filename"])):
            is_download = True
        crt_dir_mtx.release()
        if is_download:
            continue
        filepath = os.path.join(static_dir, f['filename'])
        try:
            res = requests.get(f['url'], stream=True,
                               allow_redirects=True, timeout=(5, 6))
            with open(filepath, "wb") as fd:
                for chunk in res.iter_content(chunk_size=10240):
                    fd.write(chunk)
        except:
            print("download file error: {}".format(f['url']))
            continue


def download(nthreads=8):
    # 下载任务数量是不确定的，但是线程数量是固定的
    # threads = []
    # for _ in range(nthreads):
    #     t = threading.Thread(target=download_file)
    #     t.start()
    #     threads.append(t)
    # for t in threads:
    #     t.join()
    pool = ThreadPool(nthreads)
    for _ in range(nthreads):
        pool.apply_async(download_file)
    pool.close()
    pool.join()
