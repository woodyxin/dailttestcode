from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import requests
from selenium.webdriver.chrome.service import Service

# Clash代理地址
PROXY = "127.0.0.1:7890"  # Clash HTTP代理

# ChromeDriver路径
driver_path = r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe"

# 目标Twitter账号主页
TWITTER_URL = "https://twitter.com/DirtyAngelXXX"

# 图片保存目录
SAVE_DIR = "twitter_photos"
os.makedirs(SAVE_DIR, exist_ok=True)

def setup_driver(proxy=PROXY):
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=http://{proxy}')
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--headless")  # 如需无头模式，取消注释

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scroll_down(driver, scroll_pause_time=2, max_scrolls=5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def download_image(url, folder=SAVE_DIR):
    local_filename = os.path.join(folder, url.split("/")[-1].split("?")[0])
    if os.path.exists(local_filename):
        print(f"已存在，跳过：{local_filename}")
        return
    try:
        proxies = {"http": f"http://{PROXY}", "https": f"http://{PROXY}"}
        r = requests.get(url, proxies=proxies, timeout=10)
        if r.status_code == 200:
            with open(local_filename, 'wb') as f:
                f.write(r.content)
            print(f"下载成功：{local_filename}")
        else:
            print(f"下载失败，状态码：{r.status_code}，URL：{url}")
    except Exception as e:
        print(f"下载异常：{e}，URL：{url}")

def main():
    driver = setup_driver()
    driver.get(TWITTER_URL)
    time.sleep(5)  # 等待页面加载

    scroll_down(driver, max_scrolls=10)

    imgs = driver.find_elements("xpath", '//img[contains(@src,"twimg.com/media")]')

    img_urls = set()
    for img in imgs:
        src = img.get_attribute("src")
        if src:
            img_urls.add(src.split("?")[0])

    print(f"找到 {len(img_urls)} 张图片，开始下载...")

    for url in img_urls:
        download_image(url)

    driver.quit()

if __name__ == "__main__":
    main()

