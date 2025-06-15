import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

# --- 配置 ---
PROXY = "127.0.0.1:7890"
CHROMEDRIVER_PATH = r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe"
INSTAGRAM_USERNAME = "yunjieshuodao"
INSTAGRAM_PASSWORD = "4673597wx"
TARGET_USER = "florescentx"
DOWNLOAD_FOLDER = r"D:\4_cache\python\pythonNCBITest\webcrawler\pinterest_images\instagram_reels"

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

def instagram_login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(7)  # 等待登录完成

    # 关闭“保存登录信息”弹窗
    try:
        not_now_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
        not_now_btn.click()
        time.sleep(3)
    except NoSuchElementException:
        pass

    # 关闭“开启通知”弹窗
    try:
        not_now_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
        not_now_btn.click()
        time.sleep(3)
    except NoSuchElementException:
        pass

def scroll_and_collect_reels_post_links(driver):
    reels_url = f"https://www.instagram.com/{TARGET_USER}/reels/"
    driver.get(reels_url)
    time.sleep(5)

    post_links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    print(f"开始无限滚动抓取 {TARGET_USER} 的Reels帖子链接...")

    while True:
        anchors = driver.find_elements(By.TAG_NAME, "a")
        for a in anchors:
            href = a.get_attribute("href")
            if href and f"/reel/" in href and href not in post_links:
                post_links.add(href)
                print(f"抓取到Reel帖子链接: {href}")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("没有更多Reels帖子链接，滚动结束。")
            break
        last_height = new_height

    return post_links

def collect_video_url_from_reel_page(driver, reel_url):
    driver.get(reel_url)
    time.sleep(5)
    try:
        video = driver.find_element(By.TAG_NAME, "video")
        src = video.get_attribute("src")
        if src and src.startswith("http"):
            print(f"Reel视频链接: {src}")
            return src
    except Exception as e:
        print(f"单个Reel页抓视频异常: {e} - {reel_url}")
    return None

def download_videos(video_urls, folder=DOWNLOAD_FOLDER):
    if not os.path.exists(folder):
        os.makedirs(folder)

    for i, url in enumerate(video_urls):
        try:
            print(f"下载视频 {i + 1}/{len(video_urls)}: {url}")
            resp = requests.get(url, headers=HEADERS, proxies=proxies, timeout=60)
            if resp.status_code == 200:
                ext = url.split('?')[0].split('.')[-1]
                filename = os.path.join(folder, f"video_{i}.{ext}")
                with open(filename, "wb") as f:
                    f.write(resp.content)
                print(f"已保存: {filename}")
            else:
                print(f"下载失败，状态码: {resp.status_code} - {url}")
        except Exception as e:
            print(f"下载异常: {e} - {url}")

def main():
    driver = create_driver_with_proxy(PROXY)
    try:
        instagram_login(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        reels_post_links = scroll_and_collect_reels_post_links(driver)
        print(f"共抓取到 {len(reels_post_links)} 条Reels帖子链接。")

        video_urls = set()
        for link in reels_post_links:
            src = collect_video_url_from_reel_page(driver, link)
            if src:
                video_urls.add(src)

        print(f"共收集到 {len(video_urls)} 个Reels视频链接，开始下载...")
        download_videos(video_urls)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
