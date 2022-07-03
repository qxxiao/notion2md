# https://github.com/echo724/notion2md/blob/main/notion2md/convertor/richtext.py

mapper = {
    "b": "**{text}**",  # bold
    "i": "*{text}*",  # italic
    "s": "~~{text}~~",  # strikethrough
    "c": "`{text}`",   # code
    "m": "${text}$",  # math/latex expression
    ######################################
    "a": "[{text}]({url})",  # link
    "u": "<u>{text}</u>",  # underline
    "color": "<font color='{color}'>{text}</font>",  # color
    # background
    "bg": "<span style='background-color: {bgcolor}' >{text}</span>",
}

# colors
enum_color = {
    'default': '#37352f',  # default color and background
    'gray': '#f1f1ef', 'gray_background': '#f1f1ef',
    'brown': '#9e6b53', 'brown_background': '#f4eeee',
    'orange': '#da720f', 'orange_background': '#faecdd',
    # #fefe00 in md; #fbf3da in notion [yellow_background]
    'yellow': '#dab071', 'yellow_background': '#fefe00',
    'green': '#458361', 'green_background': '#edf3ec',
    'blue': '#337ea9', 'blue_background': '#e7f3f8',
    'purple': '#9065b0', 'purple_background': '#f7f3f8',
    'pink': '#c04d8a', 'pink_background': '#fbf2f5',
    'red': '#d44c47', 'red_background': '#fdebec',
    'teal': '#4b9b9b', 'teal_background': '#eaf7f7',  # old api teal
}

# 忽略了 基本块最外层的 color 属性，表示该块的颜色
# Color of the block
# text, equation, mention


def md_render(rich_text: list):
    res = ""
    for chunk in rich_text:
        # lin_preview 版本的mention 可以在 plain_text/ href 中提取作为 link
        if chunk['type'] == 'mention' and chunk['mention']['type'] != 'link_preview':
            continue
        cur = chunk['plain_text'].strip()
        if cur == "":
            res += " "
            continue
        if chunk["type"] == "equation":  # 也可以是 chunk['equation']['expression']
            cur = mapper["m"].format(text=cur)

        # common annotations
        if chunk['annotations']['code']:
            cur = mapper["c"].format(text=cur)
        if chunk['annotations']['strikethrough']:
            cur = mapper["s"].format(text=cur)
        if chunk['annotations']['bold']:
            cur = mapper["b"].format(text=cur)
        if chunk['annotations']['italic']:
            cur = mapper["i"].format(text=cur)
        if chunk['annotations']['underline']:
            cur = mapper["u"].format(text=cur)
        color = chunk['annotations']['color']
        if color != "default":
            if color.endswith("background"):
                cur = mapper["bg"].format(
                    bgcolor=enum_color.get(color, ""), text=cur)
            else:
                cur = mapper["color"].format(
                    color=enum_color.get(color, ""), text=cur)
        if chunk['href'] != None:
            cur = mapper["a"].format(
                text=cur, url=chunk['href'])
        res += cur
    return res


def plain_text(rich_text: list):
    res = ""
    for chunk in rich_text:
        if chunk['type'] == 'mention' and chunk['mention']['type'] != 'link_preview':
            continue
        cur = chunk['plain_text']
        res += cur
    return res


# for callout html text
def html_render(rich_text: list):
    # 使用html标签渲染
    # pattern = re.compile(r"==(.*?)==")
    # content = re.sub(pattern, r"<mark>\1</mark>", content)
    res = ""
    for chunk in rich_text:
        if chunk['type'] == 'mention' and chunk['mention']['type'] != 'link_preview':
            continue
        cur = chunk['plain_text'].strip()
        if cur == "":
            res += " "
            continue
        # if chunk["type"] == "equation":
        #     # plaintext
        #     pass
        if chunk['annotations']['code']:
            cur = "<code>{}</code>".format(cur)
        if chunk['annotations']['strikethrough']:
            cur = "<del>{}</del>".format(cur)
        if chunk['annotations']['bold']:
            cur = "<strong>{}</strong>".format(cur)
        if chunk['annotations']['italic']:
            cur = "<em>{}</em>".format(cur)
        if chunk['annotations']['underline']:
            cur = "<u>{}</u>".format(cur)
        color = chunk['annotations']['color']
        if color != "default":
            if color.endswith("background"):
                cur = "<span style='background-color:{}'>{}</span>".format(
                    enum_color.get(color, ""), cur)
            else:
                cur = "<font color='{}'>{}</font>".format(
                    enum_color.get(color, ""), cur)
        if chunk['href'] != None:
            cur = "<a href='{}' target='_blank'>{}</a>".format(
                chunk['href'], cur)
        res += cur
    return res
