import imp
import os
import requests
from traitlets import default

from blocks import client_api
from blocks.block import Block
from blocks.page import Page
from text.web import getUrlInfo
from text.div import get_div, get_bmDiv
from utils import file
# ============================================================


# type = tableofcontents
def transTableOfContents(block: Block):
    return "\n[TOC]\n"  # ! @[TOC]自定义


# todo 如果前一个块不是 list 缩进会生成代码块 md
def transParagraph(block: Block, level=0):
    fmt = """
{tab}{content}
"""
    paragraph = block.Paragraph
    if file.file_last_btype == 1:
        return fmt.format(tab="\t"*level, content=paragraph['mdtext'])
    else:
        return fmt.format(tab="", content=paragraph['mdtext'])


# todo Need Test 前面的空行
# type = divider
def transDivider(block: Block):
    fmt = """
{content}
"""
    divider = block.Divider
    return fmt.format(content=divider['divider'])


# todo Need Test
# type = bulleted_list
# 无序列表只关心 层级即可； 可能含有children
def transBulletedList(block: Block, level=0):
    fmt = """
{tab}- {content}
"""
    bulleted_list = block.BulletedList
    content = fmt.format(tab="\t"*level, content=bulleted_list['mdtext'])
    previous_type = bulleted_list['type']
    for child in block.children():
        if child.type == previous_type:
            content = content[:-1]
        previous_type = child.type
        content += block2md(child, level+1)
    return content


# !有 children level++, 返回就--; level 是相对父级区块需要缩进的层级
# todo Need Test
# type = NumeredList
# level: 上一个区块的层级
def transNumberedList(block: Block, level=0):
    fmt = """
{tab}1. {content}
"""
    numbered_list = block.NumberedList
    content = fmt.format(
        tab="\t"*level, content=numbered_list['mdtext'])
    previous_type = numbered_list['type']
    for child in block.children():
        if child.type == previous_type:
            content = content[:-1]
        previous_type = child.type
        content += block2md(child, level+1)  # 子块的index=0
    return content


# todo Need Test
# type = quote
# Quote块 可能有children
# notion中第一段文字是内容，后续都是 children块
# todo quote不算做缩进层级，连续的quote嵌套只是 加 >
def transQuote(block: Block, level=0):
    fmt = """
{tab}> {content}
"""
    quote = block.Quote
    content = fmt.format(tab="\t"*level, content=quote['mdtext'])
    previous_type = quote['type']
    for child in block.children():
        # if child.type == previous_type:
        #     content = content[:-1]
        # previous_type = child.type
        # 如果遇到子页面，只是返回输出一个链接，内容由子页面自己生成
        childContent = block2md(child, 0)  # 子块相对该块的层级为0
        content += childContent
        # content += "\n> " + childContent
    content += '\n'
    return content


# todo Need Test, 例如相邻todo的空行情况/缩进
# type = todo
def transTodo(block: Block, level=0):
    fmt = """
{tab}{content}
"""
    todo = block.Todo
    content = ""
    if todo['checked']:
        content = fmt.format(tab="\t"*level, content="- [x] " + todo['mdtext'])
    else:
        content = fmt.format(tab="\t"*level, content="- [ ] " + todo["mdtext"])
    for child in block.children():
        content = content[:-1]
        content += block2md(child, level+1)
    return content


# type = toggle
# 添加markdown为了自定义样式, 如果为了在typora显示md内容，可以加上一个空行在summary后面
# todo 为了简化不会缩进，子块会
def transToggle(block: Block, level: int = 0):
    fmt = """
<details class="markdown">
<summary><b>{title}</b></summary>
{content}
</details>
"""
    toggle = block.Toggle
    content = ""
    for child in block.children():
        content += block2md(child, level)
    return fmt.format(title=toggle['mdtext'], content=content.strip('\n'))


# todo Need Test
# type = equation
def transEquation(block: Block):
    fmt = """
$$
{content}
$$
"""
    equation = block.Equation
    return fmt.format(content=equation['equation'])


# type = code
# 忽略代码块中，文本的样式信息
# todo 为了方便代码块不会缩进
def transCode(block: Block):
    fmt = """
```{language}
{content}
```
"""
    code = block.Code
    # caption = "<h4>{}</h4>".format(code["caption"])
    return fmt.format(language=code['language'], content=code['plaintext'])


# type = table
# table block + table row blocks
# todo 简化，不会缩进
def transTable(block: Block):
    fmt = """
{content}
"""
    table_width = block.Table['table_width']
    row_delimiter = "|" + ("|".join(["---"]*table_width)) + "|\n"

    table = ""
    index = 0
    for table_row in block.children():
        tds = table_row.TableRow['cells']
        tds = [text.replace("\n", "<br>") for text in tds]
        table += "|" + "|".join(tds) + "|\n"
        if index == 0:
            table += row_delimiter
        index += 1
    return fmt.format(content=table)


def downloadFile(url, file_type: str):
    """
    file_type: image/file
    返回下载的文件的相对路径(执行路径)
    """
    res = requests.get(url, allow_redirects=True)
    if res.status_code != 200:
        print("download file error: {}".format(url))
        return
    if file_type == "image":
        file.image_count += 1
    else:
        file.file_count += 1

    filename = file_type + \
        "_{}".format(file.image_count if file_type ==
                     "image" else file.file_count)
    if file_type == "image":
        filename += ".png"
    elif file_type == "video":
        filename += ".mp4"
    else:
        filename += ".pdf"
    static_dir = os.path.join(file.cur_dir, "static")
    if not os.path.exists(static_dir):
        os.mkdir(static_dir)
    filepath = os.path.join(static_dir, filename)
    with open(filepath, "wb") as f:
        f.write(res.content)
    return filepath


# type = img
# 返回(单行url), 如果是 file 类型需要下载
def transImage(block: Block):
    fmt = """
![{title}]({url} "{caption}")
"""
    image = block.Image
    if image['external'] == True:
        return fmt.format(title=image['caption'], url=image['url'], caption=image['caption'])
    # notion file类型, 在 file.cur_dir 下保存文件
    filepath = downloadFile(image['url'], "image")
    return fmt.format(title=image['caption'], url=filepath, caption=image['caption'])


# type = video
# 兼容 嵌入的视频
def transVideo(block: Block):
    vd = """
<video width="720" height="450" preload="none" poster="" controls>
    <source src="{url}" type="video/mp4">
    <source src="{url}" type="video/webm">
    <source src="{url}" type="video/ogg" />
    <p>Your browser doesn't support HTML5 video. Here is a <a href="{url}">link to the video</a> instead.</p>
</video>
"""
    iframe = """
<center><iframe width="720" height="450" src="{url}" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe></center>
"""
    video = block.Video
    url: str = video['url']
    if video['external'] == True:
        if url.startswith("https://www.youtube.com/watch?v="):
            url = url.replace("watch?v=", "embed/")
            return iframe.format(url=url)
    # notion file类型, 在 file.cur_dir 下保存文件
    filepath = downloadFile(url, "video")
    return vd.format(url=filepath)


# type = link_to_page
# ! 不支持链接到database的块， api get nothing but only "unsurpported"
# todo 与 child_page 操作一样，下载链接的页面到 file_cur_dir
# 不支持数据库，对单个页面的链接，获取页面的内容
def transChildPageOrLinkToPage(block: Block):
    # 返回链接的 page 结构 或者 child_page块的 page 结构
    if block.type == "child_page":
        page = client_api.Notion.getPage(block.id)
    else:
        page = block.LinkToPage
    # todo 注意写入文件时，先改变file.cur_dir
    file.cur_dir = os.path.join(file.cur_dir, "subpages")
    # 创建子页面文件夹
    if os.path.exists(file.cur_dir) is False:
        os.makedirs(file.cur_dir)
    page2md(page)
    link = "\n[{title}]({url})\n".format(
        title=page.title, url=os.path.join(file.cur_dir, page.title + ".md"))
    # todo 这里改回来
    file.cur_dir = os.path.dirname(file.cur_dir)
    return link


# ! need test
def transCallout(block: Block):
    callout = block.Callout
    # "💬" "🔗"
    # 不下载 notion file 图标，如果没有使用默认图标
    icon = "💡" if not callout['icon']['emoji'] else callout['icon']['emoji']
    if callout['icon']['external']:
        icon = callout['icon']['url']
    return get_div(callout['htmltext'], color=callout['color'], icon=icon)


def transBookmark(block: Block):
    bookmark = block.Bookmark
    # new api only support url in bookmark
    title, description, icon = getUrlInfo(bookmark['url'])
    return get_bmDiv(bookmark['url'], title, description, icon)


def transEmbed(block: Block):
    fmt = """
<center><iframe width="720" height="450" src="{url}" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe></center>
"""
    # embed 含有多种类型的嵌入，比如 bilibili, gist, pdfs...
    # youtube 在 notion直接使用 video格式链接
    embed = block.Embed
    # case : https://player.bilibili.com/player.html?aid=37634220&bvid=BV1vt411S7ou&cid=66164724&page=1&high_quality=1
    if embed['url'].startswith("https://player.bilibili.com"):
        return fmt.format(url=embed['url'])
    return """
    [{title}]({url})
    """.format(title=embed['url'], url=embed['url'])


# todo
# type = syncedblock 同步块 忽略

# todo
# 处理 Child database blocks

# todo
# type = Column List and Column Blocks


def block2md(block: Block, level: int = 0) -> str:
    blockmd = ""
    if block.type == "unsupported":
        return blockmd
    if block.type == "heading_1" or block.type == "heading_2" or block.type == "heading_3":
        header = block.Header
        blockmd = header['hashTag'] + ' ' + header['mdtext'] + '\n'
    elif block.type == "paragraph":
        blockmd = transParagraph(block, level)
    elif block.type == "bulleted_list_item":
        blockmd = transBulletedList(block, level)
    elif block.type == "numbered_list_item":
        blockmd = transNumberedList(block, level)
    elif block.type == "code":
        blockmd = transCode(block)
    elif block.type == "toggle":
        blockmd = transToggle(block, level)
    elif block.type == "quote":
        blockmd = transQuote(block, level)
    elif block.type == "bookmark":
        blockmd = transBookmark(block)
    elif block.type == "callout":
        blockmd = transCallout(block)
    elif block.type == "to_do":
        blockmd = transTodo(block, level)
    elif block.type == 'table':
        blockmd = transTable(block)
    elif block.type == "image":
        blockmd = transImage(block)
    elif block.type == "video":
        blockmd = transVideo(block)
    elif block.type == "embed":
        blockmd = transEmbed(block)
    # other file type
    # ! no link_to_page, but child_page or child_database
    elif block.type == "link_to_page" or block.type == "child_page":
        blockmd = transChildPageOrLinkToPage(block)
    elif block.type == "table_of_contents":
        blockmd = transTableOfContents(block)
    elif block.type == "divider":
        blockmd = transDivider(block)
    elif block.type == "child_database":
        pass
    elif block.type == "column_list":
        pass
    else:
        pass
    # ---------------
    if block.type == "numbered_list_item" or block.type == "bulleted_list_item" or block.type == "to_do":
        file.file_last_btype = 1
    else:
        file.file_last_btype = 0
    return blockmd


def get_page_meta(page: Page):
    block = page.Block()  # as Block
    meta = {
        "url": page.url,  # page url
        "title": page.title,  # page title
        "cover": "",  # page cover(None)
        "icon": "",  # page icon(None)
        "created": block.created_time,  # page created time
        "last_edited": block.last_edited_time,  # page last edited time
        # --------for database subpage
        "tags": [],  # page tags[Tags]
        "categories": "",  # page categories[Category]
        "desc": "",  # page description[Desc]
    }
    if page.cover != None:
        if page.cover['type'] == "external":
            meta["cover"] = page.cover['external']['url']
        else:
            filepath = downloadFile(page.cover['file']['url'], "image")
            meta["cover"] = filepath

    if page.icon != None:
        if page.icon['type'] == "external":
            meta["icon"] = page.icon['external']['url']
        elif page.icon['type'] == "emoji":
            meta["icon"] = page.icon['emoji']
        else:
            filepath = downloadFile(page.icon['file']['url'], "image")
            meta["icon"] = filepath

    # 查询额外信息 database page
    if block.parent['type'] == "database":
        for prop in page.prop:
            # multi-select
            if ['tag', 'tags', 'Tag', 'Tags', 'TAGS'].count(prop) > 0:
                meta['tags'] = client_api.Notion.getProperty(
                    page.id, page.prop[prop]['id'])
            # multi-select
            elif ['category', 'categories', 'Category', 'CATEGORY', 'CATEGORIES'].count(prop) > 0:
                meta['categories'] = client_api.Notion.getProperty(
                    page.id, page.prop[prop]['id'])
            # rich text
            elif ['desc', 'description', 'Desc', 'DESC', 'DESCRIPTION'].count(prop) > 0:
                meta['desc'] = client_api.Notion.getProperty(
                    page.id, page.prop[prop]['id'])
    return meta


# page2md
# or not return
def page2md(page: Page) -> str:
    md_header = """---
title: '{title}'
date: {date}
tags: [{tags}]
published: true
hideInList: false
isTop: false
feature: {cover}
url: {url}
---
"""
    digest = """{digest}
<!-- more -->
"""
    assert client_api.Notion is not None
    file.file_last_btype = 0
    """
    将 page 转换为 md
    """
    print("\033[1;32m正在导出页面: ", page.title, "......\033[0m")
    md = ''
    for block in page.children():
        # 如果遇到 链接页面或者子页面，递归生成 md
        # block.type == 'child_page' or block.type == 'link_to_page'已经在下面 block2md 中递归处理了
        md += block2md(block)
    # 获取页面的属性
    # title, description, cover, icon
    meta = get_page_meta(page)
    header = md_header.format(
        title=meta['title'], date=meta['created'], tags=",".join(meta['tags']), cover=meta['cover'], url=meta['url'])
    if meta['desc'] != "":
        header += digest.format(digest=meta['desc'])
    mdfile = header + md
    # ! write to file
    title = page.title
    filepath = os.path.join(file.cur_dir, title+'.md')
    # ! 注意， file.cur_dir 由调用者处理，首页默认在  ./notion2md_files
    if os.path.exists(file.cur_dir) is False:
        os.makedirs(file.cur_dir)
    with open(filepath, 'wt') as f:
        f.write(mdfile)
    print("\033[1;33m导出页面: ", title, "完成\033[0m")
    return mdfile
