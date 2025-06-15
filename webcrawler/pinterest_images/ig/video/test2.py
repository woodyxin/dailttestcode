from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests

from webcrawler.pinterest_images.clashtest import driver

# -------- 配置 --------
INSTAGRAM_USERNAME = "yunjieshuodao"
INSTAGRAM_PASSWORD = "4673597wx"
TARGET_USER = "florescentx"  # 目标账号
CHROMEDRIVER_PATH = r"D:\\1_development\\06 TOOL\\chromedriver-win64\\chromedriver.exe"
DOWNLOAD_FOLDER = r"D:\\4_cache\\python\\pythonNCBITest\\webcrawler\\pinterest_images\\instagram_videos"
PROXY = "127.0.0.1:7890"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# -------- 驱动 --------
def create_driver():
    options = Options()
    options.add_argument(f'--proxy-server=http://{PROXY}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--start-maximized')
    service = Service(CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)

# -------- 登录 --------
def instagram_login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)
    time.sleep(5)
    for text in ["Not Now", "稍后再说"]:
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{text}')]"))
            ).click()
        except:
            continue

# -------- 滚动并收集Reels链接 --------
def scroll_and_collect_reel_links(driver):
    driver.get(f"https://www.instagram.com/{TARGET_USER}/reels/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article a[href*='/reel/']"))
    )
    links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    print("开始滚动并收集Reels帖子链接...")

    while True:
        for elem in driver.find_elements(By.CSS_SELECTOR, "article a[href*='/reel/']"):
            href = elem.get_attribute("href")
            if href and href not in links:
                links.add(href)
                print(f"找到Reel链接：{href}")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    print(f"共抓取到 {len(links)} 条Reels链接。")
    return list(links)

# -------- 抽取mp4 --------
def extract_mp4_url(driver, post_url):
    driver.get(post_url)
    print(f"访问：{post_url}")
    try:
        video = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        src = video.get_attribute("src")
        if src and src.endswith(".mp4"):
            print(f"✅ 提取到视频：{src}")
            return src
        else:
            print(f"警告：video标签的src非mp4：{src}")
    except Exception as e:
        print(f"❌ 提取失败：{e}")

    with open("debug_reel_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    return None

# -------- 下载视频 --------
def download_video(url, folder, index):
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            filename = os.path.join(folder, f"reel_{index}.mp4")
            with open(filename, 'wb') as f:
                f.write(r.content)
            print(f"✅ 保存成功：{filename}")
        else:
            print(f"❌ 下载失败，状态码：{r.status_code}")
    except Exception as e:
        print(f"❌ 下载异常：{e}")

# -------- 主流程 --------
def main():
    driver = create_driver()
    try:
        instagram_login(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        reel_links = scroll_and_collect_reel_links(driver)
        video_urls = [extract_mp4_url(driver, url) for url in reel_links]
        video_urls = [u for u in video_urls if u]
        print(f"共提取到 {len(video_urls)} 个mp4视频链接")
        for i, url in enumerate(video_urls):
            download_video(url, DOWNLOAD_FOLDER, i)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()



