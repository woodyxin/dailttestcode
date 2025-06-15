import os
import time
import requests
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

# --- 配置 ---
PROXY = "127.0.0.1:7890"  # Clash代理端口
CHROMEDRIVER_PATH = r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe"
TARGET_URL = "https://hentailoop.com/manga/all-sorts-of-wives/read/"
DOWNLOAD_FOLDER = r"D:\4_cache\python\pythonNCBITest\webcrawler\pinterest_images\hentai_images"

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

def is_valid_image_url(src):
    if not src:
        return False
    lower_src = src.lower()
    blacklist = ['profile', 'avatar', 'thumbnail', 'thumb', 'icon', 'sprite']
    if any(keyword in lower_src for keyword in blacklist):
        return False
    return True

def scroll_to_bottom(driver, pause_time=3):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def collect_image_urls(driver):
    imgs = driver.find_elements(By.TAG_NAME, "img")
    img_urls = set()
    for img in imgs:
        try:
            src = img.get_attribute("src")
            if not src:
                src = img.get_attribute("data-src")  # 懒加载图片
            if is_valid_image_url(src):
                img_urls.add(src)
        except StaleElementReferenceException:
            continue
        except Exception:
            continue
    return img_urls

def is_colorful_image(content_bytes):
    try:
        image = Image.open(BytesIO(content_bytes))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        colors = image.getcolors(maxcolors=1000000)
        if colors is None:
            return True  # 颜色丰富
        return len(colors) > 5  # 简单阈值，<=5可能是纯色或极简黑白
    except Exception:
        return True  # 遇错默认保留

def download_images(img_urls, folder=DOWNLOAD_FOLDER):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for i, url in enumerate(img_urls):
        try:
            print(f"下载图片 {i+1}/{len(img_urls)}: {url}")
            resp = requests.get(url, headers=HEADERS, proxies=proxies, timeout=30)
            if resp.status_code == 200:
                if not is_colorful_image(resp.content):
                    print(f"图片颜色过于单一，可能是黑白线稿，仍然保存")
                ext = url.split('?')[0].split('.')[-1]
                if ext.lower() not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    ext = 'jpg'  # 默认扩展名
                filename = os.path.join(folder, f"image_{i}.{ext}")
                with open(filename, "wb") as f:
                    f.write(resp.content)
                print(f"已保存: {filename}")
            else:
                print(f"下载失败，状态码 {resp.status_code}: {url}")
        except Exception as e:
            print(f"下载异常: {e} - {url}")

def main():
    driver = create_driver_with_proxy(PROXY)
    try:
        driver.get(TARGET_URL)
        time.sleep(5)
        print("开始滚动加载页面...")
        scroll_to_bottom(driver, pause_time=4)
        print("开始抓取图片链接...")
        img_urls = collect_image_urls(driver)
        print(f"共抓取到 {len(img_urls)} 张图片")
        download_images(img_urls)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
