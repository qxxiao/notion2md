

import re
from text.md import enum_color


# 简单样式的 div(callout 或者 自定义)
def get_simpleDiv(content, textColor="default", bgColor="default"):
    fmt = """
<div class="markdown" style="padding: 10px; color: {textColor}; background-color: #e7f3f8;border-top-right-radius: 6px;border-bottom-right-radius: 6px;border: 1px solid #dedfdf;border-left: thick solid {bgColor};">
<span>{content}</span>
</div>
"""
    if textColor == "default":
        textColor = "''"  # "black"
    if bgColor == "default":
        bgColor = "#337ea9"  # 默认蓝色为border-left
    return fmt.format(textColor=textColor, bgColor=bgColor, content=content)


# 用于callout的 div 样式表示
def get_div(content, color="default", icon=None):
    fmt = """
<div class="markdown" style="padding: 10px; color: {textColor}; background-color: {bgColor}; border-radius: 6px; border:{border}">
<div style="width: 28px;height: 28px;margin-left: 0px;margin-right: 10px;position: absolute;">{icon}</div>
<p style="line-height: 28px; margin: 0px 5px 0px 38px !important">{content}</p></div>
"""
    if icon.startswith("http"):
        icon = '<span><img style="height: 28px" src="{}" /></span>'.format(
            icon)
    else:
        icon = '<span style="font-size: 18px;">{}</span>'.format(
            icon)  # width: 100%

    textColor, bgColor, border = enum_color['default'], "#ffffff", "1px solid #dfdfde"

    if color != "default":
        if color.endswith("background"):
            bgColor = enum_color[color]
            # border = "''"
        else:
            textColor = enum_color[color]
    return fmt.format(textColor=textColor, bgColor=bgColor, border=border, icon=icon, content=content)


# 用于 Bookmark的 div 样式表示
def get_bmDiv(url, title, content, icon):
    fmt = """
<div class="markdown" style="padding: 10px;background-color: {bgColor}; border-radius: 6px; border:1px solid #dfdfde">
<div style="width: 28px;height: 28px;margin-left: 0px;margin-right: 10px;position: absolute;">{icon}</div>
<a href={url} target="_blank" style="text-decoration:none"><p style="color: rgb(55, 53, 47); text-overflow: ellipsis;margin: 0px 5px 0px 38px !important"><span style="
font-size: 14px;line-height: 20px;min-height: 24px;margin-bottom: 2px;">{title}</span><br><span style="font-size: 12px; line-height: 16px; color: rgba(55, 53, 47, 0.65); height: 32px">{content}</span><br><span style="font-size: 12px;line-height: 16px;">{url}</span></p></a></div>
"""
    if icon.startswith("http") or icon.startswith("data:image"):
        icon = '<span><img style="height: 28px" src="{}" /></span>'.format(
            icon)
    else:
        # width: 100% # todo icon
        icon = '<span style="font-size: 18px;">{}</span>'.format("🔖")
    bgColor = "#f8f8f8"  # "#ffffff"  # or system default
    border = "1px solid #dfdfde"
    return fmt.format(bgColor=bgColor, border=border, icon=icon, title=title, content=content, url=url)
