import requests
from bs4 import BeautifulSoup

# 设置 Headers 模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

# 目标 URL
url = 'https://www.douban.com/'

# 发送请求
response = requests.get(url, headers=headers)

# 检查响应状态
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # 抓取首页上所有链接的文本和地址
    links = soup.find_all('a')
    for link in links:
        text = link.get_text(strip=True)
        href = link.get('href')
        if text and href:
            print(f'{text}: {href}')
else:
    print('请求失败，状态码：', response.status_code)
