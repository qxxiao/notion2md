from blocks.block import Block
from blocks.page import Page
from blocks.database import Database


# 只用来页面，页面块；数据库，数据库块；
class Cache(object):
    def __init__(self):
        self.__block_cache = {}
        self.__page_cache = {}
        self.__database_cache = {}

    @property
    def blockSize(self):
        return len(self.__block_cache)

    @property
    def pageSize(self):
        return len(self.__page_cache)

    @property
    def databaseSize(self):
        return len(self.__database_cache)

    # for block
    def block(self, id) -> Block or None:
        if id in self.__block_cache:
            return self.__block_cache[id]
        return None

    def setBlock(self, id, value):
        self.__block_cache[id] = value

    # for page
    def page(self, id) -> Page or None:
        if id in self.__page_cache:
            return self.__page_cache[id]
        return None

    def setPage(self, id, value):
        self.__page_cache[id] = value

    # for database
    def database(self, id) -> Database or None:
        if id in self.__database_cache:
            return self.__database_cache[id]
        return None

    def setDatabase(self, id, value):
        self.__database_cache[id] = value


defaultCache = Cache()
