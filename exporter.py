
import os
import threading

from notion_client import Client

from convertor.page2md import page2md
from blocks import client_api  # init NotionAPI client
from utils import ufile


# todo Properties marked with an * are available to integrations with any capabilities.
# todo 需要打开集成的所有的权限
token = os.environ.get("NOTION_TOKEN", None)
while token is None:
    token = input("NOTION_TOKEN is not set, input:\n")

link = os.environ.get("NOTION_PAGES", None)
while link is None:
    link = input("NOTION_PAGES is not set, input:\n")
client_api.Notion = client_api.ClientAPI(Client(auth=token))

file_id = link.split("/")[-1]
# ?v=...
file_id = file_id.split("?")[0]
file_id = file_id[-32:]


def export_md(file_id):
    page = client_api.Notion.getPage(file_id)
    # 线程 parser 负责解析 notion block
    # 线程池负责 下载文件并写入
    parser = threading.Thread(
        target=page2md, args=(page,), name="parser")
    downloader = threading.Thread(
        target=ufile.download, args=(8,), name="downloader")
    parser.start()
    downloader.start()
    parser.join()
    print('下载文件中......')
    downloader.join()
    print("notion2md done!")


if __name__ == '__main__':
    export_md(file_id)
