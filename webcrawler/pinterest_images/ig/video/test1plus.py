import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 配置
PROXY = "127.0.0.1:7890"
CHROMEDRIVER_PATH = r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe"
DOWNLOAD_FOLDER = r"D:\4_cache\python\pythonNCBITest\webcrawler\pinterest_images\instagram_reels"

INSTAGRAM_USERNAME = "yunjieshuodao"
INSTAGRAM_PASSWORD = "4673597wx"
TARGET_USER = "florescentx"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
PROXIES = {
    "http": f"http://{PROXY}",
    "https": f"http://{PROXY}"
}

def create_driver_with_proxy(proxy):
    options = Options()
    options.add_argument(f"--proxy-server=http://{proxy}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def instagram_login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys("\n")
    time.sleep(7)
    # 处理可能出现的“Not Now”弹窗
    for _ in range(2):
        try:
            not_now_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
            not_now_btn.click()
            time.sleep(2)
        except:
            pass

def scroll_collect_reel_links(driver, target_user):
    driver.get(f"https://www.instagram.com/{target_user}/reels/")
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
            except:
                pass
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("没有更多Reels帖子链接，滚动结束。")
            break
        last_height = new_height
    return list(links)

def extract_mp4_urls(driver, reel_urls):
    """
    使用Chrome DevTools监听视频媒体请求，捕获mp4链接。
    """
    video_urls = []
    driver.execute_cdp_cmd('Network.enable', {})

    # 拦截并收集 mp4 请求url
    intercepted_urls = set()

    def intercept_request(request):
        try:
            url = request.get('request', {}).get('url', '')
            if url.endswith('.mp4'):
                if url not in intercepted_urls:
                    print("捕获到视频链接:", url)
                    intercepted_urls.add(url)
        except Exception:
            pass

    # 绑定监听事件
    driver.execute_cdp_cmd('Network.setRequestInterception', {'patterns': [{'urlPattern': '*'}]})

    # selenium python client 没有直接回调监听接口，需要用 `driver.execute_cdp_cmd`轮询，下面是模拟代码
    # 这里简化处理，selenium不支持直接hook请求事件，
    # 所以改成每个视频页面加载时等待，然后用driver.execute_cdp_cmd('Network.getResponseBody')等方法或从page_source解析

    for url in reel_urls:
        print(f"加载Reels帖子页面: {url}")
        intercepted_urls.clear()
        driver.get(url)
        time.sleep(7)  # 等待网络请求发出

        # 这里用js获取video标签src
        try:
            video = driver.find_element(By.TAG_NAME, "video")
            src = video.get_attribute("src")
            if src and src.startswith("http") and not src.startswith("blob:"):
                print("视频标签直接获取链接:", src)
                video_urls.append(src)
                continue
        except:
            pass

        # fallback: 从页面源码找 JSON 中的 video_url
        page_source = driver.page_source
        import re
        import json
        m = re.search(r'window\._sharedData\s*=\s*({.*?});</script>', page_source)
        if m:
            try:
                data = json.loads(m.group(1))
                video_url = data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['video_url']
                if video_url not in video_urls:
                    print("从页面JSON提取视频链接:", video_url)
                    video_urls.append(video_url)
            except Exception as e:
                print("解析视频链接失败:", e)
        else:
            print(f"未能提取到视频链接: {url}")

    return video_urls

def download_video(url, folder, index):
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        response = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=30)
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
        reel_links = scroll_collect_reel_links(driver, TARGET_USER)
        print(f"共抓取到 {len(reel_links)} 条Reels帖子链接。")

        video_urls = extract_mp4_urls(driver, reel_links)
        print(f"共收集到 {len(video_urls)} 个Reels视频链接，开始下载...")

        for idx, video_url in enumerate(video_urls):
            download_video(video_url, DOWNLOAD_FOLDER, idx)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
