# database 与 其中的页面有细微区别

# 主要在于 property
# description
# is_inline

from text.md import plain_text
from blocks import cache
from blocks.page import Page
from blocks import client_api


class Database():
    def __init__(self, id, url, title, prop, is_inline, icon=None, cover=None, description=[],
                 object='database'):
        self.id = id  # database id
        self.url = url
        self._title = title  # rich_text
        self.prop = prop
        self.is_inline = is_inline
        self.icon = icon
        self.cover = cover
        self.description = description
        self.object = object

    def __str__(self):
        return cache.defaultCache.block(self.id).__str__() + \
            "-------------------------------------------------------------" +\
            "\n\t[url]:" + self.url + \
            "\n\t[title]:" + self.title[0]['plain_text'] + \
            "\n\t[is_inline]:" + str(self.is_inline) + \
            "\n\t[icon]:" + str(self.icon) + \
            "\n\t[cover]:" + str(self.cover) + \
            "\n\t[description]:" + str(self.description) + "\n\n"

    @property
    def title(self):
        return plain_text(self._title)  # 去除 rich_text

    @staticmethod
    def dic2page(child: dict):
        return Page(child['id'], child['url'], child['properties'], child['icon'], child['cover'], child['object'])

    # 查询数据库所有子页面，返回子页面的 id 列表
    # 使用 POST https: // api.notion.com/v1/databases/{database_id}/query

    def children(self, page_size: int = 500, start_cursor: str = None):
        assert client_api.Notion is not None
        # 根据结果 childpage
        res = client_api.Notion.notion.databases.query(
            self.id, page_size=page_size, start_cursor=start_cursor)
        if res['results'] is None or len(res['results']) == 0:
            return []
        for page in res['results']:
            page = self.dic2page(page)
            cache.defaultCache.setPage(page.id, page)
            # add block to cache
            client_api.Notion.getBlock(page.id)
            yield page

        while res['has_more']:
            res = client_api.Notion.notion.databases.query(
                self.id, page_size=page_size, start_cursor=res['next_cursor'])
            for page in res['results']:
                page = self.dic2page(page)
                cache.defaultCache.setPage(page.id, page)
                # add block to cache
                client_api.Notion.getBlock(page.id)
                yield page
