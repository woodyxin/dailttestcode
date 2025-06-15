from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests

PROXY = "127.0.0.1:7890"
CHROMEDRIVER_PATH = r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe"
DOWNLOAD_FOLDER = r"D:\4_cache\python\pythonNCBITest\webcrawler\pinterest_images\instagram_images"

INSTAGRAM_USERNAME = "yunjieshuodao"
INSTAGRAM_PASSWORD = "4673597wx"
TARGET_USER = "florescentx"

proxies = {
    "http": f"http://{PROXY}",
    "https": f"http://{PROXY}"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/114.0.0.0 Safari/537.36"
}

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

def scroll_and_collect_reel_links(driver):
    driver.get(f"https://www.instagram.com/{TARGET_USER}/reels/")
    time.sleep(5)

    reel_links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    print("开始无限滚动抓取Reels帖子链接...")

    while True:
        try:
            # 等待至少有Reels帖子链接加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article a[href*='/reel/']"))
            )
        except TimeoutException:
            print("超时，未检测到Reels帖子链接。")

        links = driver.find_elements(By.CSS_SELECTOR, "article a[href*='/reel/']")
        for link in links:
            href = link.get_attribute("href")
            if href and href not in reel_links:
                reel_links.add(href)
                print(f"抓取到Reel帖子链接: {href}")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("没有更多Reels帖子链接，滚动结束。")
            break
        last_height = new_height

    return list(reel_links)

def extract_video_url(driver, reel_url):
    driver.get(reel_url)
    time.sleep(5)  # 等待页面加载和视频元素出现

    try:
        video = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        video_url = video.get_attribute("src")
        if video_url and video_url.startswith("http"):
            print(f"提取到视频链接: {video_url}")
            return video_url
    except TimeoutException:
        print(f"超时未找到视频元素: {reel_url}")
    except Exception as e:
        print(f"提取视频失败: {e}")

    return None

def download_video(video_url, folder=DOWNLOAD_FOLDER, index=0):
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        response = requests.get(video_url, proxies=proxies, headers=headers, timeout=30)
        if response.status_code == 200:
            ext = video_url.split('?')[0].split('.')[-1]
            filename = os.path.join(folder, f'reel_video_{index}.{ext}')
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"已保存: {filename}")
        else:
            print(f"下载失败，状态码: {response.status_code} - {video_url}")
    except Exception as e:
        print(f"下载异常: {e} - {video_url}")

def main():
    driver = create_driver_with_proxy(PROXY)
    try:
        instagram_login(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

        reel_links = scroll_and_collect_reel_links(driver)
        print(f"共抓取到 {len(reel_links)} 条Reels帖子链接。")

        video_urls = []
        for i, url in enumerate(reel_links):
            video_url = extract_video_url(driver, url)
            if video_url:
                video_urls.append(video_url)

        print(f"共收集到 {len(video_urls)} 个Reels视频链接，开始下载...")

        for i, video_url in enumerate(video_urls):
            download_video(video_url, index=i)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
