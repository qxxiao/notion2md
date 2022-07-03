

from notion_client import Client

from blocks.cache import defaultCache
from blocks.page import Page
from blocks.block import Block
from blocks.database import Database

from pprint import pprint


class ClientAPI():
    def __init__(self, client: Client) -> None:
        self.notion = client

    # return users generator
    def get_user_list(self):
        res = self.notion.users.list(page_size=10)
        yield from res['results']
        # res['next_cursor'] is not None || res['has_more'] is True
        while res['has_more']:
            res = self.notion.users.list(
                page_size=10, start_cursor=res['next_cursor'])
            yield from res['results']

    # 处理 page
    # - 取 page 以及 获取 page 的 block
    # - 加入缓存
    # 说明：可以获取 page 的 property【page property item, 从 数据库继承过来的或者 只有title】
    #      使用复杂的查询需要用到 pages/{page_id}/properties/{property_id}

    def getPage(self, page_id):
        """
        获取 page
        同时会获取 page block, 确保加入缓存
        """
        if defaultCache.page(page_id) is not None:
            return defaultCache.page(page_id)

        pageRes = self.notion.pages.retrieve(page_id)  # page
        page = Page(pageRes['id'], pageRes['url'], pageRes['properties'],
                    pageRes['icon'], pageRes['cover'], pageRes['object'])
        defaultCache.setPage(page.id, page)

        if defaultCache.block(page_id) is None:
            blockRes = self.notion.blocks.retrieve(
                page_id)  # block => for children
            block = Block(blockRes['id'], blockRes['parent'], blockRes['created_time'], blockRes['created_by'],
                          blockRes['last_edited_time'], blockRes['last_edited_by'], blockRes['type'], blockRes[blockRes['type']], blockRes['has_children'], blockRes['archived'], blockRes['object'])
            defaultCache.setBlock(block.id, block)
        return page

    def getBlock(self, block_id):
        """
        获取 block(包括page block, database block)
        会确保page block, database block 加入缓存
        """
        if defaultCache.block(block_id) is not None:
            return defaultCache.block(block_id)

        blockRes = self.notion.blocks.retrieve(
            block_id)  # block => for children
        block = Block(blockRes['id'], blockRes['parent'], blockRes['created_time'], blockRes['created_by'],
                      blockRes['last_edited_time'], blockRes['last_edited_by'], blockRes['type'], blockRes[blockRes['type']], blockRes['has_children'], blockRes['archived'], blockRes['object'])
        # todo 检查，只有对页面/数据库 顶级block 加入缓存
        if block.type == 'child_page' or block.type == 'child_database':
            defaultCache.setBlock(block.id, block)
        return block

    def getDatabase(self, database_id):
        """
        获取 database
        会确保database block 加入缓存
        """
        if defaultCache.database(database_id) is not None:
            return defaultCache.database(database_id)

        databaseRes = self.notion.databases.retrieve(database_id)  # database
        database = Database(databaseRes['id'], databaseRes['url'], databaseRes['title'], databaseRes['properties'],
                            databaseRes['is_inline'], databaseRes['icon'], databaseRes['cover'], databaseRes['description'], databaseRes['object'])
        defaultCache.setDatabase(database.id, database)

        if defaultCache.block(database_id) is None:
            blockRes = self.notion.blocks.retrieve(
                database_id)  # block => for children
            block = Block(blockRes['id'], blockRes['parent'], blockRes['created_time'], blockRes['created_by'],
                          blockRes['last_edited_time'], blockRes['last_edited_by'], blockRes['type'], blockRes[blockRes['type']], blockRes['has_children'], blockRes['archived'], blockRes['object'])
            defaultCache.setBlock(block.id, block)
        return database

    def getProperty(self, page_id, property_id):
        """
        获取 page property
        pages/{page_id}/properties/{property_id}
        """
        property = self.notion.request(
            path=f"pages/{page_id}/properties/{property_id}", method="GET")
        # Tags: multiselect; return 字符串列表
        value = property[property['type']]
        if property['type'] == 'multi_select':
            return [item['name'] for item in value]
        # date 如果是日期，返回字符串(格式依赖notion设置)
        if property['type'] == 'date':
            return value['start']
        # title, rich_text, relation and people property
        # api 返回分页列表, 只返回第一页内容
        if property['type'] == 'property_item' and value['type'] == 'rich_text':
            return "".join([t['rich_text']["plain_text"] for t in property["results"]])
        return None


Notion: ClientAPI = None
