from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import requests

PROXY = "127.0.0.1:7890"
proxies = {
    "http": f"http://{PROXY}",
    "https": f"http://{PROXY}"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/114.0.0.0 Safari/537.36"
}




INSTAGRAM_USERNAME = "yunjieshuodao"
INSTAGRAM_PASSWORD = "4673597wx"
TARGET_USER = "florescentx"
CHROMEDRIVER_PATH = r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe"
DOWNLOAD_FOLDER = r"D:\4_cache\python\pythonNCBITest\webcrawler\pinterest_images\instagram_images"

def create_driver_with_proxy(proxy):
    options = Options()
    options.add_argument(f'--proxy-server=http://{proxy}')
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def instagram_login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

    # 关闭“保存登录信息”弹窗
    try:
        driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]").click()
    except:
        pass
    time.sleep(3)
    # 关闭“开启通知”弹窗
    try:
        driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]").click()
    except:
        pass
    time.sleep(2)

def scroll_and_collect_images(driver):
    driver.get(f"https://www.instagram.com/{TARGET_USER}/")
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
            if width >= 300 and height >= 300 and src not in img_urls:
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

def download_images(img_urls, folder=DOWNLOAD_FOLDER):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for i, url in enumerate(img_urls):
        try:
            response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
            if response.status_code == 200:
                ext = url.split('?')[0].split('.')[-1]
                filename = os.path.join(folder, f'image_{i}.{ext}')
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"已保存: {filename}")
            else:
                print(f"下载失败，状态码: {response.status_code} - {url}")
        except Exception as e:
            print(f"下载异常: {e} - {url}")

def main():
    driver = create_driver_with_proxy(PROXY)
    try:
        instagram_login(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        images = scroll_and_collect_images(driver)
        print(f"总共抓取到 {len(images)} 张大图")
        download_images(images)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
