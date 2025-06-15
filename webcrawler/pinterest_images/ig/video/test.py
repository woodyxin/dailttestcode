from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import os
import requests
import re

# 配置参数
PROXY = "127.0.0.1:7890"
CHROMEDRIVER_PATH = r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe"
DOWNLOAD_FOLDER = r"D:\4_cache\python\pythonNCBITest\webcrawler\pinterest_images\instagram_reels"

INSTAGRAM_USERNAME = "yunjieshuodao"
INSTAGRAM_PASSWORD = "4673597wx"
TARGET_USER = "florescentx"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
proxies = {
    "http": f"http://{PROXY}",
    "https": f"http://{PROXY}"
}

def create_driver_with_proxy(proxy):
    options = Options()
    options.add_argument(f"--proxy-server=http://{proxy}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)

def instagram_login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)
    time.sleep(5)
    # 处理登录后弹窗（保存登录信息，开启通知等）
    for _ in range(2):
        try:
            not_now = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
            not_now.click()
            time.sleep(2)
        except:
            pass

def scroll_collect_reel_links(driver):
    driver.get(f"https://www.instagram.com/{TARGET_USER}/reels/")
    time.sleep(5)
    links = set()
    last_height = 0

    print("开始滚动并收集Reels帖子链接...")
    while True:
        reel_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/reel/")]')
        for elem in reel_elements:
            try:
                href = elem.get_attribute("href")
                if href and href not in links:
                    links.add(href)
                    print(f"找到Reels链接: {href}")
            except StaleElementReferenceException:
                continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("没有更多Reels帖子链接，滚动结束。")
            break
        last_height = new_height

    return list(links)

def extract_mp4_url(driver, post_url, timeout=20):
    driver.get(post_url)
    try:
        video = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        src = video.get_attribute("src")
        if src:
            print(f"提取到视频链接: {src}")
            return src
        else:
            print(f"video标签存在但src为空：{post_url}")
    except TimeoutException:
        print(f"未找到video标签（超时）：{post_url}")
    except Exception as e:
        print(f"extract_mp4_url异常：{e}")
    return None

def extract_mp4_url_from_page_source(driver, post_url):
    driver.get(post_url)
    time.sleep(5)
    page_source = driver.page_source
    matches = re.findall(r'https://[^"]+\.mp4', page_source)
    if matches:
        print(f"正则匹配到视频链接: {matches[0]}")
        return matches[0]
    print("未从源码找到视频链接")
    return None

def download_video(url, folder, index):
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        if response.status_code == 200:
            path = os.path.join(folder, f"reel_{index}.mp4")
            with open(path, "wb") as f:
                f.write(response.content)
            print(f"✅ 已保存: {path}")
        else:
            print(f"下载失败: 状态码 {response.status_code} - {url}")
    except Exception as e:
        print(f"下载异常: {e} - {url}")

def main():
    driver = create_driver_with_proxy(PROXY)
    try:
        instagram_login(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        reel_links = scroll_collect_reel_links(driver)
        print(f"共抓取到 {len(reel_links)} 条Reels帖子链接。")

        video_urls = []
        for link in reel_links:
            video_url = extract_mp4_url(driver, link)
            if not video_url:
                # 用源码正则作为备选方案
                video_url = extract_mp4_url_from_page_source(driver, link)
            if video_url:
                video_urls.append(video_url)

        print(f"共收集到 {len(video_urls)} 个Reels视频链接，开始下载...")
        for idx, video_url in enumerate(video_urls):
            download_video(video_url, DOWNLOAD_FOLDER, idx)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()

#test视频捕获成功 下载不成功