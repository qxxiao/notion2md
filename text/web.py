
import requests
from bs4 import BeautifulSoup


def getUrlInfo(url: str):
    """
    获取url页面的 header 信息,
    使用 bs4 模块解析 headers 返回 title, description, icon
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    if url.strip() == "":
        return "", "", ""
    title, description, icon = url.split('/')[2], "", "🔖"
    try:
        response = requests.get(url, headers=headers,
                                allow_redirects=True, timeout=1.5)
    except:
        return title, description, icon
    response.encoding = 'utf-8'
    # 使用 bs4 模块解析 headers 返回 title, description, icon
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        title = soup.find('title').text
    except:
        pass
    try:
        description = soup.find(
            'meta', attrs={'name': 'description'}).get('content')[:100]
    except:
        pass
    try:
        icon = soup.find('link', attrs={'rel': 'icon'}).get('href')
        if not icon.startswith('http') and not icon.startswith('data:image'):
            if icon.startswith('/'):
                icon = "/".join(url.split('/')[:3] + icon.split('/')[1:])
            else:
                icon = "/".join(url.split('/')[:-1] + [icon])
    except:
        pass
    return title, description, icon


if __name__ == '__main__':
    for text in getUrlInfo('https://www.baidu.com'):
        print(text)
