
import os

from notion_client import Client

from convertor.page2md import page2md
from blocks import client_api
from utils import file as _


# todo Properties marked with an * are available to integrations with any capabilities.
# todo 需要打开集成的所有的权限
token = os.environ["NOTION_TOKEN"]
while token is None:
    token = input("NOTION_TOKEN is not set, input:\n")

file = os.environ["NOTION_PAGES"]
while file is None:
    file = input("NOTION_PAGES is not set, input():\n")
client_api.Notion = client_api.ClientAPI(Client(auth=token))

file_id = file.split("/")[-1]
# ?v=...
file_id = file_id.split("?")[0]
file_id = file_id[-32:]

page2md(client_api.Notion.getPage(file_id))
print("notion2md done!")
