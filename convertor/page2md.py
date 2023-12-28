import os
import time
import uuid

from blocks import client_api
from blocks.block import Block
from blocks.database import Database
from blocks.page import Page
from text.web import getUrlInfo
from text.div import get_div, get_bmDiv
from utils import ufile

#
file_last_btype = 0
# ============================================================


# type = tableofcontents
def transTableOfContents(block: Block, level=0):
    return "\n[TOC]\n"  # ! @[TOC]自定义


def transHeading(block: Block, level: int = 0):
    header = block.Header
    return '\n' + header['hashTag'] + ' ' + header['mdtext'] + '\n'


def transParagraph(block: Block, level: int = 0):
    fmt = """
{tab}{content}
"""
    paragraph = block.Paragraph
    if file_last_btype == 1:
        return fmt.format(tab="\t"*level, content=paragraph['mdtext'])
    else:
        return fmt.format(tab="", content=paragraph['mdtext'])


# type = divider
def transDivider(block: Block, level=0):
    fmt = """
{content}
"""
    divider = block.Divider
    return fmt.format(content=divider['divider'])


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


# type = NumeredList
# level: 块的层级
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


# type = quote; may have children
# notion中第一段文字是quote text，后续都是 children块
# quote不算做缩进层级，连续的quote嵌套只是 加 >
def transQuote(block: Block, level=0):
    fmt = """
{tab}> {content}
"""
    quote = block.Quote
    content = fmt.format(tab="\t"*level, content=quote['mdtext'])
    previous_type = quote['type']
    for child in block.children():
        childContent = block2md(child, 0)  # 子块相对该块的层级为0
        content += childContent
    content += '\n'
    return content


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


# type = equation
def transEquation(block: Block, level=0):
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
def transCode(block: Block, level=0):
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
def transTable(block: Block, level=0):
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


# def downloadFile(url, file_type: str):
#     """
#     file_type: image/file 用来标识文件的前缀
#     返回下载的文件的相对路径(执行路径)
#     """
#     if file_type == "image":
#         file.image_count += 1
#     else:
#         file.file_count += 1
#     # 不带后缀文件名
#     static_dir = os.path.join(ufile.cur_dir, "static")
#     filename = file_type + \
#         "_{}".format(file.image_count if file_type ==
#                      "image" else file.file_count)

#     if not os.path.exists(static_dir):
#         os.mkdir(static_dir)
#     else:
#         filelist = os.listdir(static_dir)
#         for name in filelist:
#             if name.startswith(filename):
#                 return "./static/" + name
#     # 下载文件
#     try:
#         res = requests.get(url, allow_redirects=True, timeout=(3, 5))
#     except:
#         print("download file error: {}".format(url))
#         return ""
#     # 添加文件后缀
#     try:
#         ftype = res.headers['Content-Type'].split(';')[0].split(
#             '/')[1].split('+')[0].split('.')[-1].split('-')[-1]
#         filename += "." + ftype
#     except:
#         filename += ".file"
#     # ftype = url.split("?")[-2].split(".")[-1] # ?查询字符串
#     filepath = os.path.join(static_dir, filename)
#     with open(filepath, "wb") as f:
#         f.write(res.content)
#     return "./static/" + filename


# type = img
# 返回(单行url), 如果是 file 类型需要下载
def transImage(block: Block, level=0):
    fmt = """
![{title}]({url})
"""
    image = block.Image
    if image['external'] == True:
        return fmt.format(title=image['caption'], url=image['url'])
    # notion file类型, 在 ufile.cur_dir 下保存文件
    # filepath = downloadFile(image['url'], "image")
    filename = image['url'].split("?")[0].split("/")[-1]
    # 使用 timestamp 生成文件名+后缀
    filename = str(time.time()) + '-' + str(uuid.uuid4()) + \
        "-" + filename
    # 加入下载列表
    ufile.download_list.put({
        "url": image['url'],
        "path": ufile.cur_dir,
        "filename": "image_"+filename
    })
    return fmt.format(title=filename, url="./static/"+"image_"+filename)


# type = video
# 兼容 嵌入的视频
def transVideo(block: Block, level=0):
    vd = """
<video width="100%" preload="none" poster="" controls>
    <source src="{url}" type="video/mp4">
    <source src="{url}" type="video/webm">
    <source src="{url}" type="video/ogg" />
    <p>Your browser doesn't support HTML5 video. Here is a <a href="{url}">link to the video</a> instead.</p>
</video>
"""
    # width="720" height="500" youtube
    # width="720" height="580" bili
    iframe = """
<center><iframe width="100%" {height} src="{url}" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe></center>
"""
    video = block.Video
    url: str = video['url']
    if video['external'] == True:
        if url.startswith("https://www.youtube.com/watch?v="):
            url = url.replace("watch?v=", "embed/")
            return iframe.format(height='height="500"', url=url)
    # notion file类型, 在 ufile.cur_dir 下保存文件
    # filepath = downloadFile(url, "video")
    filename = url.split("?")[0].split("/")[-1]
    filename = str(time.time()) + '-' + str(uuid.uuid4()) + \
        "-" + filename
    # 加入下载列表
    ufile.download_list.put({
        "url": url,
        "path": ufile.cur_dir,
        "filename": "video_"+filename
    })
    return vd.format(url="./static/"+"video_"+filename)


# type = link_to_page
# ! 不支持链接到database的块， api get nothing but only "unsurpported"
# 与 child_page 操作一样，下载链接的页面到 file_cur_dir
# 不支持数据库，对单个页面的链接，获取页面的内容
def transChildPageOrLinkToPage(block: Block, level=0):
    # 返回链接的 page 结构 或者 child_page块的 page 结构
    if block.type == "child_page":
        page = client_api.Notion.getPage(block.id)
    else:
        page = block.LinkToPage
    ufile.cur_dir = os.path.join(ufile.cur_dir, "subpages")
    # 创建子页面文件夹
    if os.path.exists(ufile.cur_dir) is False:
        os.makedirs(ufile.cur_dir)
    page2md(page)
    # use relative path
    link = "\n[{title}]({url})\n".format(
        title=page.title, url=os.path.join("./subpages", page.title + ".md"))
    ufile.cur_dir = os.path.dirname(ufile.cur_dir)
    return link


# ! need test
def transCallout(block: Block, level=0):
    callout = block.Callout
    # "💬" "🔗"
    # 不下载 notion file 图标，如果没有使用默认图标
    icon = callout['icon']['emoji']  # if link default "💡"
    if callout['icon']['external']:
        icon = callout['icon']['url']
    return get_div(callout['htmltext'], color=callout['color'], icon=icon)


def transBookmark(block: Block, level=0):
    bookmark = block.Bookmark
    # new api only support url in bookmark
    title, description, icon = getUrlInfo(bookmark['url'])
    return get_bmDiv(bookmark['url'], title, description, icon)


def transEmbed(block: Block, level=0):
    # width="720" height="450"
    fmt = """
<center><iframe width="100%" {height} src="{url}" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe></center>
"""
    # embed 含有多种类型的嵌入，比如 bilibili, gist, pdfs...
    # youtube 在 notion直接使用 video格式链接
    # todo Add more embed type
    embed = block.Embed
    # case : https://player.bilibili.com/player.html?aid=37634220&bvid=BV1vt411S7ou&cid=66164724&page=1&high_quality=1
    if embed['url'].startswith("https://player.bilibili.com"):
        return fmt.format(height='height="570"', url=embed['url'])
    # 外部视频(youtube被优化了作为video类型)嵌入,外部服务嵌入，比如 gist，codepen，google map,doc...
    return "\n[{title}]({url})\n".format(title=embed['url'], url=embed['url'])


def transFile(block: Block, level=0):
    # 文件资源链接，外链或notion file
    file = block.File
    filename = file['url'].split("?")[0].split("/")[-1]
    if file['external']:
        return "\n[{title}]({url})\n".format(title=filename, url=file['url'])
    # notion file
    # filepath = downloadFile(file['url'], "file")
    # 加入下载列表
    filename = str(time.time()) + '-' + str(uuid.uuid4()) + \
        "-" + filename
    ufile.download_list.put({
        "url": file['url'],
        "path": ufile.cur_dir,
        "filename": "file_" + filename
    })
    return "\n[{title}]({url})\n".format(title=filename, url="./static/file_" + filename)


def transPdf(block: Block, level=0):
    # 表示嵌入的 pdf类型，同file处理方式
    pdf = block.Pdf
    filename = pdf['url'].split("?")[0].split("/")[-1]
    if pdf['external']:
        return "\n[{title}]({url})\n".format(title=filename, url=pdf['url'])
    # notion file
    # filepath = downloadFile(pdf['url'], "file")  # pdf
    # 加入下载列表
    filename = str(time.time()) + '-' + str(uuid.uuid4()) + \
        "-" + filename
    ufile.download_list.put({
        "url": pdf['url'],
        "path": ufile.cur_dir,
        "filename": "pdf_" + filename
    })
    return "\n[{title}]({url})\n".format(title=filename, url="./static/pdf_" + filename)


def transAudio(block: Block, level=0):
    audio = block.Audio
    filename = audio['url'].split("?")[0].split("/")[-1]
    if audio['external']:
        return "\n[{title}]({url})\n".format(title=filename, url=audio['url'])
    # notion file
    # filepath = downloadFile(audio['url'], "file")  # audio
    # 加入下载列表
    filename = str(time.time()) + '-' + str(uuid.uuid4()) + \
        "-" + filename
    ufile.download_list.put({
        "url": audio['url'],
        "path": ufile.cur_dir,
        "filename": "audio_" + filename
    })
    return "\n[{title}]({url})\n".format(title=filename, url="./static/audio_" + filename)


# 处理 Child database blocks
def transChildDatabase(block: Block, level=0):
    database: Database = client_api.Notion.getDatabase(block.id)
    res = ""
    for page in database.children():
        ufile.cur_dir = os.path.join(ufile.cur_dir, "subpages")
        if os.path.exists(ufile.cur_dir) is False:
            os.makedirs(ufile.cur_dir)
        page2md(page)
        # use relative path
        link = "\n[{title}]({url})  \n".format(
            title=page.title, url=os.path.join("./subpages", page.title + ".md"))
        ufile.cur_dir = os.path.dirname(ufile.cur_dir)
        res += link
    return res


# todo
# type = breadcrumb

# todo
# type = synced_block 同步块


handlers = {
    "heading_1": transHeading,
    "heading_2": transHeading,
    "heading_3": transHeading,
    # ---
    "paragraph": transParagraph,
    "bulleted_list_item": transBulletedList,
    "numbered_list_item": transNumberedList,
    "code": transCode,
    "toggle": transToggle,
    "quote": transQuote,
    "bookmark": transBookmark,
    "callout": transCallout,
    "to_do": transTodo,
    "table": transTable,
    "image": transImage,
    "video": transVideo,
    "embed": transEmbed,
    "file": transFile,
    "pdf": transPdf,
    "audio": transAudio,
    "table_of_contents": transTableOfContents,
    "divider": transDivider,
    # ! link_to_database in api is unsupported type
    "link_to_page": transChildPageOrLinkToPage,
    "child_page": transChildPageOrLinkToPage,
    "child_database": transChildDatabase,
    # ---
    "column_list": None,  # type = Column List and Column Blocks
    # ......
}


def block2md(block: Block, level: int = 0) -> str:
    global file_last_btype
    handle = handlers.get(block.type, None)
    blockmd = ""
    if handle is not None:
        # start = time.time()*1000
        blockmd = handle(block, level)
        # end = time.time()*1000
    if block.type == "numbered_list_item" or block.type == "bulleted_list_item" or block.type == "to_do":
        file_last_btype = 1
    else:
        file_last_btype = 0
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
            # 加入下载列表
            filename = page.cover['file']['url'].split("?")[0].split("/")[-1]
            filename = str(time.time()) + '-' + str(uuid.uuid4()) + \
                "-" + filename
            ufile.download_list.put({
                "url": page.cover['file']['url'],
                "path": ufile.cur_dir,
                "filename": "image_" + filename
            })
            meta["cover"] = "./static/image_" + filename

    if page.icon != None:
        if page.icon['type'] == "external":
            meta["icon"] = page.icon['external']['url']
        elif page.icon['type'] == "emoji":
            meta["icon"] = page.icon['emoji']
        else:
            filename = page.icon['file']['url'].split("?")[0].split("/")[-1]
            filename = str(time.time()) + '-' + str(uuid.uuid4()) + \
                "-" + filename
            ufile.download_list.put({
                "url": page.icon['file']['url'],
                "path": ufile.cur_dir,
                "filename": "image_" + filename
            })
            meta["icon"] = "./static/image_" + filename

    # 查询额外信息 database page
    if block.parent['type'] == "database_id":
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


def _stop_download():
    if ufile.cur_dir == os.curdir:
        ufile.download_list.put(None)


# page2md
# or not return
def page2md(page: Page) -> str:
    global file_last_btype
    assert client_api.Notion is not None
    file_last_btype = 0
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
    fp = os.path.join(ufile.cur_dir, page.title+'.md')
    if os.path.exists(fp):
        local_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(os.stat(fp).st_ctime))
        if local_time > page.Block().last_edited_time:
            _stop_download()
            return
    print("\033[1;32m正在导出页面: ", page.title, "......\033[0m")
    md = ''
    for block in page.children():
        # 如果遇到 链接页面或者子页面，递归生成 md
        # block.type == 'child_page' or block.type == 'link_to_page'已经在下面 block2md 中递归处理了
        md += block2md(block)
    ######################
    _stop_download()
    # 获取页面的属性
    # title, description, cover, icon
    meta = get_page_meta(page)
    header = md_header.format(
        title=meta['title'], date=meta['created'], tags=",".join(meta['tags']), cover=meta['cover'], url=meta['url'])
    if meta['desc'] != "":
        header += digest.format(digest=meta['desc'])
    mdfile = header + md
    # ! write to file
    # ! 注意， ufile.cur_dir 由调用者处理，首页默认在  ./notion2md_files
    if os.path.exists(ufile.cur_dir) is False:
        os.makedirs(ufile.cur_dir)
    with open(fp, 'wt') as f:
        f.write(mdfile)
    print("\033[1;33m导出页面: ", page.title, "完成\033[0m")
    return mdfile
