

from blocks.block import Block
from blocks import cache


class Page():
    # notion page interactive
    def __init__(self, id, url, prop, icon=None, cover=None, object='page'):
        self.id = id  # page id
        self.url = url
        self.prop = prop
        self.icon = icon
        self.cover = cover
        self.object = object  # 固定，'page'

    def __str__(self):
        return cache.defaultCache.block(self.id).__str__() + \
            "-------------------------------------------------------------" +\
            "\n\t[object](real type):" + self.object + \
            "\n\t[url]:" + self.url + \
            "\n\t[title]:" + self.title + \
            "\n\t[icon]:" + str(self.icon) + \
            "\n\t[cover]:" + str(self.cover) + "\n\n"

    # todo 将 title 属性使用 block api 重新查询 => 先查询写入缓存，再查询缓存 done
    @property  # 查询页面标题
    def title(self):
        assert cache.defaultCache.block(self.id) is not None
        # 2022-06-28 api没有信息 => 需要使用 block
        return cache.defaultCache.block(self.id).type_config['title']

    #############################
    # 迭代 page 的 children block
    # # 间接调用 as block 的 children

    def children(self, page_size: int = 500, start_cursor: str = None):
        # assert cache.defaultCache.block(self.id) is not None  # 判断是否存在
        # if not cache.defaultCache.block(self.id).has_children:
        #     return None
        # res = client.blocks.children.list(
        #     self.id, page_size=page_size, start_cursor=start_cursor)
        # yield from res['results']
        # while res['has_more']:
        #     res = client.blocks.children.list(
        #         self.id, page_size=page_size, start_cursor=res['start_cursor'])
        #     yield from res['result']
        block: Block = cache.defaultCache.block(self.id)
        assert block is not None
        return block.children(page_size=page_size, start_cursor=start_cursor)

    def Block(self):
        assert cache.defaultCache.block(self.id) is not None
        return cache.defaultCache.block(self.id)
