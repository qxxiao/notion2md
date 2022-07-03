

# all block
import notion_client

from blocks import client_api
from blocks import cache
from blocks.basicblock import BasicBlock
from text.md import html_render, md_render
from text.md import plain_text


# object 是 所有 page, block, database 的类别
# type 是 基本块的类型 h1,...,
# todo 包括child_page, child_database...

class Block(BasicBlock):
    """
    # todo 注意有 unsupported 类型的 block(例如执行数据库的链接 in app)
    """

    def __init__(self, id, parent, created_time,  created_by, last_edited_time, last_edited_by,
                 type, type_config, has_children,
                 archived=False, object='block'):

        super().__init__(id, parent, created_time,  created_by, last_edited_time, last_edited_by,
                         archived, object)
        # 作为基本块时，名称以及对应的配置/内容
        # 特别的 child_page / child_database
        self.type = type  # todo 决定其主要的行为
        # page/database作为 block 的时候, type名称作为key的对象只有titele属性 {title: 'test'}
        self.type_config = type_config
        self.has_children = has_children
        self.object = object

    def __str__(self):
        return super().__str__() + \
            "as block(all): " +\
            "\n\t[type]:" + self.type + \
            "\n\t[has_children]:" + str(self.has_children)+'\n'

    #############################
    # 迭代 block 的 children block 都是页面中的元素块
    # 而特殊的 child_page(不会有children) / child_database(不会有children)
    # 而对于一些常见的block元素是允许有children的
    @staticmethod
    def dic2block(child):
        return Block(child['id'], child['parent'], child['created_time'], child['created_by'],
                     child['last_edited_time'], child['last_edited_by'], child['type'], child[child['type']],
                     child['has_children'], child['archived'], child['object'])

    def children(self, page_size: int = 500, start_cursor: str = None):
        if not self.has_children:
            return []  # todo 如果没有children，返回空列表, iterable
        # if self.type == 'child_page' or self.type == 'child_database':
        #     assert cache.defaultCache.block(self.id) is not None

        res = client_api.Notion.notion.blocks.children.list(
            self.id, page_size=page_size, start_cursor=start_cursor)
        for child in res['results']:
            block = Block.dic2block(child)
            yield block

        while res['has_more']:
            res = client_api.Notion.notion.blocks.children.list(
                self.id, page_size=page_size, start_cursor=res['next_cursor'])
            # yield from res['result']
            for child in res['results']:
                block = Block.dic2block(child)
                yield block

    @property  # heading_1, heading_2, heading_3
    def Header(self):
        assert self.type == 'heading_1' or self.type == 'heading_2' or self.type == 'heading_3'
        return {
            'type': self.type,
            # #号后面的内容是指定的标题
            'hashTag': "#"*int(self.type[-1]),
            'mdtext': md_render(self.type_config['rich_text']),
            'plaintext': '',
        }

    @property
    def Paragraph(self):
        assert self.type == 'paragraph'
        return {
            'type': self.type,
            'mdtext': md_render(self.type_config['rich_text']),
            'plaintext': '',
        }

    @property  # children 被划分到 /chidren api
    def BulletedList(self):
        """
        return {type:, mdtext:, plaintext:}
        """
        assert self.type == 'bulleted_list_item'
        return {
            'type': self.type,
            'mdtext': md_render(self.type_config['rich_text']),
            'plaintext': '',
        }

    @property
    def NumberedList(self):
        """
        return {type:, mdtext:, plaintext:''}
        """
        assert self.type == 'numbered_list_item'
        return {
            'type': self.type,
            'mdtext': md_render(self.type_config['rich_text']),
            'plaintext': '',
        }

    @property
    def Callout(self):
        """
        return {type:, htmltext:, mdtext:'', plaintext:'', icon, color}
        """
        assert self.type == 'callout'
        return {
            'type': self.type,
            'mdtext': '',  # md_render(self.type_config['rich_text']),
            'htmltext': html_render(self.type_config['rich_text']),
            'plaintext': '',  # todo 所有 rich_text子数组的 plain_text连接join
            # callout 中其余属性, 可以加上color背景色/主体的字体色
            # # emoji(默认), external(url), file(url, expire_time)
            'icon': {
                # 如果是 file 不下载不关心其expire_time 使用默认图标即可
                'type': self.type_config['icon']['type'],
                'emoji': self.type_config['icon'].get('emoji', ""),
                'url': "" if self.type_config['icon']['type'] == "emoji" else self.type_config['icon'][self.type_config['icon']['type']]['url'],
                # 是否是外链, emoji从emoji读取
                'external': self.type_config['icon']['type'] == 'external',
            },
            'color': self.type_config['color']  # 'blue_background'
        }

    @property
    def Quote(self):
        """
        type, mdtext, plaintext='', color
        """
        assert self.type == 'quote'
        return {
            'type': self.type,
            'mdtext': md_render(self.type_config['rich_text']),
            'plaintext': '',  # todo
            # "default",'blue_background'...
            'color': self.type_config['color']
        }

    @property
    def Todo(self):
        assert self.type == 'to_do'
        # 舍弃 块的 color 属性
        return {
            'type': self.type,
            'mdtext': md_render(self.type_config['rich_text']),
            'plaintext': '',  # todo
            'checked': self.type_config['checked'],  # True/False
        }

    @property
    def Toggle(self):
        """
        type, mdtext, plaintext='', color。
        mdtext返回toggle内容/title, 里面内容需要获取children
        """
        assert self.type == 'toggle'
        return {
            'type': self.type,
            'mdtext': md_render(self.type_config['rich_text']),
            'plaintext': '',  # todo
            'color': self.type_config['color'],
        }

    @property
    def Code(self):
        """
        type, mdtext=None, plaintext, language,caption
        """
        assert self.type == 'code'
        # 注意 notion 中可以给代码文字添加颜色等, 使用应该使用 plaintext
        # 使用 plain_text 并且将 mention text丢弃(换行写入文件就好了)
        return {
            'type': self.type,
            'mdtext': None,  # md_render(self.type_config['rich_text']),
            'plaintext': plain_text(self.type_config['rich_text']),  # 对于代码有用
            'language': self.type_config['language'],
            'caption': self.type_config['caption'],  # todo 数组转换mdtext
        }

    @property
    def ChildPage(self):  # child page block
        """
        page block, 主要只要调用就获取了page, 可以直接从 cache 中得到页面Page(url,icon,properties)
        会确保缓存了 Page, page Block(就是self)
        id 就是 self.id, 这里仅仅返回 type和子页面的title
        """
        # 子页面作为 block; 获取子页面的的块可以通过 blocks/id/childrens api 获取
        assert client_api.Notion is not None
        assert self.type == 'child_page'
        # 由于是 child_page 块, 可以先直接缓存并缓存其 Page
        if cache.defaultCache.block(self.id) is None:
            cache.defaultCache.setBlock(self.id, self)
        client_api.Notion.getPage(self.id)  # only to cache page
        return {
            'type': self.type,
            'title': self.type_config['title'],
            'has_children': self['has_children'],
        }

    # todo 查询数据库的 子页面使用 query查询得到 Page
    # todo 完善
    @property
    def ChildDatabase(self):
        """
        """
        assert self.type == 'child_database'
        return {
            'type': self.type,  # fixed child_database
            'title': self.type_config['title'],  # database title
            'has_children': self['has_children'],  # 应该固定是 False
        }

    # todo 只能使用 url as link
    @property
    def Embed(self):
        """
        notion use Embedly, to validate and request metadata for embeds given a URL;
        使用的 类型有： Twitter,Google Drive documents,Gist,Codepen,PDFs, Google Maps, Sketch...
        api can get url
        """
        assert self.type == 'embed'
        return {
            'type': self.type,
            'url': self.type_config['url'],
            'caption': self.type_config['caption'],  # []
        }

    @property
    def Image(self):
        """
        url ending in .png, .jpg, .jpeg, .gif, .tif, .tiff, .bmp, .svg, or .heic;
        return {type:, external:, url:, caption}
        """
        assert self.type == 'image'
        # file object => file / external
        return {
            'type': self.type,
            # 如果是 file 不关心其expire_time需要下载（即 external 是 False）
            'external': self.type_config['type'] == 'external',  # True/False
            'url': self.type_config[self.type_config['type']]['url'],
            # todo 数组转换mdtext
            'caption': plain_text(self.type_config['caption']),
        }

    @property
    def Video(self):
        """
        url ending in .mkv, .flv, .gifv, .avi, .mov, .qt, .wmv, .asf, .amv, .mp4, .m4v, .mpeg, .mpv, .mpg, .f4v, etc;
        return {type:, external:, url:, caption}
        """
        assert self.type == 'video'
        # file object => file / external
        return {
            'type': self.type,  # fixed video # todo 这里是block类型
            # 如果是 file 不关心其expire_time需要下载（即 external 是 False）
            'external': self.type_config['type'] == 'external',  # True/False
            'url': self.type_config[self.type_config['type']]['url'],
            'caption': plain_text(self.type_config['caption']),
        }

    @property
    def File(self):
        """
        与 image/video一样, 存储样式
        """
        assert self.type == 'file'
        # file object => file / external
        return {
            'type': self.type,  # fixed file
            'external': self.type_config['type'] == 'external',  # True/False
            'url': self.type_config[self.type_config['type']]['url'],
            # [rich_text] # todo 转换为mdtext
            'caption': self.type_config['caption'],
        }

    @property
    def PDF(self):
        """
        使用 /Embed pdf类型会自动转为pdf block; 默认使用pdf会预览pdf
        """
        assert self.type == 'pdf'
        # file object => file / external
        return {
            'type': self.type,  # fixed pdf
            'external': self.type_config['type'] == 'external',  # True/False
            'url': self.type_config[self.type_config['type']]['url'],
        }

    @property
    def Bookmark(self):
        """
        普通链接，会获取标题等；与 pdf/file 类似
        """
        assert self.type == 'bookmark'
        # file object => file / external
        return {
            'type': self.type,  # fixed bookmark
            'external': True,   # 只能为 外部链接(bookmark属性只有url)
            'url': self.type_config['url'],
            # [rich_text] # todo 转换为mdtext
            'caption': self.type_config['caption'],
        }

    @property
    def LinkPreview(self):
        """
        类似Bookmark, 不过是预览链接(同步更新)
        link_preview block 只能返回,不能通过api创建
        """
        assert self.type == 'link_preview'
        return{
            'type': self.type,  # fixed link_preview
            'external': True,   # todo 自己添加的属性
            'url': self.type_config['url'],
        }


# ------------------------------------------------

    @property
    def Equation(self):
        assert self.type == 'equation'
        return {
            'type': self.type,
            # A KaTeX compatible string
            'equation': self.type_config['expression'],
        }

    @property
    def Divider(self):
        assert self.type == 'divider'
        return {
            'type': self.type,
            'divider': '---',  # return {} in api
        }

    @property
    def TableOfContents(self):
        assert self.type == 'table_of_contents'
        return {
            'type': self.type,
            'color': self.type_config['color'],  # 默认 gray 表示字体颜色
            'toc': '[TOC]',  # 一般md 文件是 [TOC]; or @[TOC] # todo
        }

    @property
    def Breadcrumb(self):
        """
        显示notion页面在workspace的位置, api无用
        """
        assert self.type == 'breadcrumb'
        return {
            'type': self.type,
        }

    @property
    def ColumnList(self):
        assert self.type == 'column_list'
        # 返回所有的column block.(每个column block是parent block)
        assert self.has_children
        # 每个 columns block 都是Block(type='column')
        columns = list(self.children(1000))  # max 1000 columns
        # todo 解析每一列获取 每一列的blocks
        return {
            'type': self.type,
            'length': len(columns),
            # list of column blocks(parent block) ;type is Block
            # todo 需要获取每个column Block的 children bloks
            'columns': columns,
        }

    @property
    def Template(self):
        """
        模板block, api 无用
        """
        assert self.type == 'template'
        return {
            'type': self.type,
            'template': None,  # has_children 为 True
        }

    @property
    def LinkToPage(self):
        """
        直接返回查询的page;
        # todo ;Notion app 支持链接到数据库，支持跳转;
        # todo ;api 对于数据库，类型是 unsurpported, 值是{}; 目前不支持
        """
        assert client_api.Notion is not None
        # 排除 unsoported 类型(例如链接到数据库，notion app可以)
        assert self.type == 'link_to_page'
        # if self.type == 'unsoported':
        #     return None
        return client_api.Notion.getPage(self.type_config[self.type_config['type']])
        # return {
        #     'type': self.type,
        #     'id': self.type_config[self.type_config['type']],  # page_id
        # }

    @property
    def SyncedBlock(self):
        # todo [https://developers.notion.com/reference/block#synced-block-blocks]
        # Original Synced Block
        # Reference Synced Blocks
        pass

    @property
    def Table(self):
        """
        type, table_width, has_column_header, has_row_header\n  
        Tables are parent blocks for table row children, only contain children of type table_row.\n
        需要用此id 查询该表的所有table_row
        """
        assert self.type == 'table'
        return {
            'type': self.type,
            'table_width': self.type_config['table_width'],  # 列数(创建后不能通过api更改)
            # 是否有列头, 即第一行作为表头
            'has_column_header': self.type_config['has_column_header'],
            # 是否有行头，即第一列作为表头
            'has_row_header': self.type_config['has_row_header'],
        }

    @property
    def TableRow(self):
        """
        type, cells
        # todo 应该与Table一起用, table块查询children结果就是table_row
        只能作为table块的子块, 不会作为页面的子块
        """
        assert self.type == 'table_row'
        cells = self.type_config['cells']  # 一行的单元格数组
        # 解析每个单元格, richtext 数组
        # todo 使用 plain_text 只获取文本内容
        cells = [md_render(cell) for cell in cells]
        return {
            'type': self.type,
            'cells': cells  # 每一行的数据(md text)
        }
