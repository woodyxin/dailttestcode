from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
import os

# 你的chromedriver路径
driver_path = r'D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe'

# Clash代理地址（HTTP代理）
proxy = "127.0.0.1:7890"


chrome_options = Options()
chrome_options.add_argument(f'--proxy-server=http://{proxy}')
chrome_options.add_argument('--headless')  # 无界面
chrome_options.add_argument('--disable-gpu')

service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

def scroll_down(driver, times=5, pause=2):
    """滚动页面加载更多图片"""
    for _ in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)

def download_image(url, folder, idx, proxies):
    try:
        ext = url.split('?')[0].split('.')[-1]
        file_path = os.path.join(folder, f"img_{idx}.{ext}")
        if os.path.exists(file_path):
            print(f"{file_path} 已存在，跳过")
            return
        img_data = requests.get(url, proxies=proxies, timeout=10).content
        with open(file_path, 'wb') as f:
            f.write(img_data)
        print(f"下载成功: {file_path}")
    except Exception as e:
        print(f"下载失败: {url}，错误: {e}")

def main():
    url = "https://www.instagram.com/lilithcavalierex/"
    driver.get(url)

    scroll_down(driver, times=10, pause=3)

    # 找所有图片元素
    imgs = driver.find_elements(By.TAG_NAME, "img")

    download_folder = "instagram_images"
    os.makedirs(download_folder, exist_ok=True)

    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }

    count = 1
    seen = set()
    for img in imgs:
        src = img.get_attribute('src')
        if src and src.startswith("http") and src not in seen:
            seen.add(src)
            download_image(src, download_folder, count, proxies)
            count += 1

    driver.quit()

if __name__ == '__main__':
    main()
