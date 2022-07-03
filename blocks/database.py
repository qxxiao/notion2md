# database 与 其中的页面有细微区别

# 主要在于 property
# description
# is_inline

from text.md import plain_text
from blocks import cache


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

    # 查询数据库所有子页面，返回子页面的 id 列表
    # 使用 POST https: // api.notion.com/v1/databases/{database_id}/query
