
import os

from notion_client import Client

from convertor.page2md import page2md
from blocks import client_api
from utils import file as _


# todo Properties marked with an * are available to integrations with any capabilities.
# todo 需要打开集成的所有的权限
token = os.environ.get("NOTION_TOKEN", None)
while token is None:
    token = input("NOTION_TOKEN is not set, input:\n")

file = os.environ.get("NOTION_PAGES", None)
while file is None:
    file = input("NOTION_PAGES is not set, input:\n")
client_api.Notion = client_api.ClientAPI(Client(auth=token))

file_id = file.split("/")[-1]
# ?v=...
file_id = file_id.split("?")[0]
file_id = file_id[-32:]

page2md(client_api.Notion.getPage(file_id))
print("notion2md done!")
