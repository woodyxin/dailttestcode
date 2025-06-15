import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

# --- 配置 ---
PROXY = "127.0.0.1:7890"  # Clash本地代理端口
CHROMEDRIVER_PATH = r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe"
TARGET_URL = "https://hentailoop.com/manga/all-sorts-of-wives/read/"
DOWNLOAD_FOLDER = (r"D:\4_cache\python\pythonNCBITest\webcrawler\pinterest_images\hentai_images")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

proxies = {
    "http": f"http://{PROXY}",
    "https": f"http://{PROXY}"
}

# --- 函数 ---
def create_driver_with_proxy(proxy):
    options = Options()
    options.add_argument(f'--proxy-server=http://{proxy}')
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def is_valid_image(src, width, height):
    if not src:
        return False
    if width < 300 or height < 300:
        return False
    lower_src = src.lower()
    blacklist = ['profile', 'avatar', 'thumbnail', 'thumb', 'icon']
    if any(keyword in lower_src for keyword in blacklist):
        return False
    return True

def scroll_and_collect_images(driver):
    driver.get(f"https://hentailoop.com/manga/all-sorts-of-wives/read/")
    time.sleep(5)

    img_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    print("开始无限滚动抓取图片...")

    while True:
        imgs = driver.find_elements(By.TAG_NAME, "img")
        for img in imgs:
            try:
                src = img.get_attribute("src")
                width = driver.execute_script("return arguments[0].naturalWidth;", img)
                height = driver.execute_script("return arguments[0].naturalHeight;", img)
            except StaleElementReferenceException:
                continue
            except Exception:
                continue
            if is_valid_image(src, width, height) and src not in img_urls:
                img_urls.add(src)
                print(f"抓取图片: {src} 大小: {width}x{height}")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("没有更多内容，滚动结束。")
            break
        last_height = new_height

    return img_urls
# 漫画很多是黑白线稿图，有些图片宽高达标（>=300）但颜色很单一，可能被误判或过滤掉了。
#
# 目前代码只用宽高做筛选，没有判断图片“颜色丰富度”或“灰度”之类的特征，黑白漫画图确实可能被忽略。

def download_images(img_urls, folder=DOWNLOAD_FOLDER):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for i, url in enumerate(img_urls):
        try:
            resp = requests.get(url, headers=HEADERS, proxies=proxies, timeout=30)
            if resp.status_code == 200:
                ext = url.split('?')[0].split('.')[-1]
                filename = os.path.join(folder, f"image_{i}.{ext}")
                with open(filename, "wb") as f:
                    f.write(resp.content)
                print(f"已保存: {filename}")
            else:
                print(f"下载失败 状态码 {resp.status_code}: {url}")
        except Exception as e:
            print(f"下载异常: {e} - {url}")

def main():
    driver = create_driver_with_proxy(PROXY)
    try:
        driver.get(TARGET_URL)
        time.sleep(5)
        img_urls = scroll_and_collect_images(driver)
        print(f"共抓取到 {len(img_urls)} 张大图")
        download_images(img_urls)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
