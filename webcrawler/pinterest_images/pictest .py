import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# chromedriver 路径
CHROMEDRIVER_PATH = r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe"
# 图片保存目录
DOWNLOAD_FOLDER = "pornpic_images"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# 设置浏览器代理，端口改成你 Clash 实际的 HTTP 代理端口
chrome_options.add_argument('--proxy-server=http://127.0.0.1:7890')

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 给 requests 设置代理
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

try:
    driver.get("https://www.pornpics.de/")
    time.sleep(5)

    # 滚动加载更多图片
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    imgs = driver.find_elements(By.TAG_NAME, "img")
    print(f"找到图片数量: {len(imgs)}")

    count = 0
    for img in imgs:
        src = img.get_attribute("src")
        if src and src.startswith("http"):
            try:
                if src.endswith(".jpg") or src.endswith(".png"):
                    img_data = requests.get(src, proxies=proxies).content
                    ext = src.split(".")[-1].split("?")[0]
                    file_name = os.path.join(DOWNLOAD_FOLDER, f"img_{count}.{ext}")
                    with open(file_name, "wb") as f:
                        f.write(img_data)
                    count += 1
            except Exception as e:
                print(f"下载失败: {src}，错误: {e}")

    print(f"成功下载图片数量: {count}")

finally:
    driver.quit()
