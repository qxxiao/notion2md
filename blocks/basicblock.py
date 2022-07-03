
# common block as block, page, database
# 注意不表示一种类型，只是共用的属性
# 上层类型有: block通用块(包括 chil_page块， chil_database块); page页面, database数据库

from utils.time import formatTime


class BasicBlock:
    """
    A basic block is common property of a block.
    For block, page as block, database as block:
        1. object => always "block"
        2. id     => "3e8fa88f60d14ce691951ac818760301"
        3. created_time/created_by   => "2020-03-17T19:10:04.968Z"/部分User
        4. last_edited_time/last_edited_by
        5. archived => False/True
        6. parent
    """

    def __init__(self,
                 id, parent, created_time,  created_by, last_edited_time, last_edited_by,
                 archived=False,
                 object='block'):
        # object can be "block", "page", "database"; but use block api is always "block"
        # time format: "2020-03-17T19:10:04.968Z" USA time
        self.id = id
        # {type: 'page_id', page_id: 'xxxxxx'}
        # {type: 'database_id', database_id: 'xxxxxx'}
        # {type: 'workspace', workspace: True}
        self.parent = parent
        self.created_time = formatTime(created_time)  # string
        self.created_by = created_by['id']  # string(user id)
        self.last_edited_time = formatTime(last_edited_time)  # string
        self.last_edited_by = last_edited_by['id']  # string(user id)
        self.archived = archived
        # "block", "page", "database"
        self.object = object

    def __str__(self):
        return "common part: \n\t" + "[id]:" + self.id + \
            "\n\t[parent]: " + self.parent['type'] + \
            ":" + self.parent[self.parent['type']] + \
            "\n\t-----------------------------------------------------\n"
