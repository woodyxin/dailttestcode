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
import json
from urllib.parse import urlparse
import random

# -------- 配置 --------
INSTAGRAM_USERNAME = "yunjieshuodao"
INSTAGRAM_PASSWORD = "4673597wx"
TARGET_USER = "florescentx"
CHROMEDRIVER_PATH = r"D:\\1_development\\06 TOOL\\chromedriver-win64\\chromedriver.exe"
DOWNLOAD_FOLDER = r"D:\\4_cache\\python\\pythonNCBITest\\webcrawler\\pinterest_images\\instagram_videos"
PROXY = "127.0.0.1:7890"

# 更真实的请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}


# -------- 创建驱动器 --------
def create_driver():
    options = Options()

    # 代理设置
    options.add_argument(f'--proxy-server=http://{PROXY}')

    # 反检测设置
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 设置用户代理
    options.add_argument(f'--user-agent={HEADERS["User-Agent"]}')

    # 禁用图片加载以提高速度（可选）
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # options.add_experimental_option("prefs", prefs)

    # 实验性选项
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # 执行反检测脚本
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


# -------- 登录Instagram --------
def instagram_login(driver, username, password):
    print("正在登录Instagram...")
    driver.get("https://www.instagram.com/accounts/login/")

    # 等待页面加载
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
    except:
        print("❌ 登录页面加载失败")
        debug_page_content(driver)
        return False

    # 随机延迟，模拟人类行为
    time.sleep(random.uniform(2, 4))

    try:
        # 输入用户名
        username_field = driver.find_element(By.NAME, "username")
        username_field.clear()
        for char in username:
            username_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

        time.sleep(random.uniform(1, 2))

        # 输入密码
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        for char in password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

        time.sleep(random.uniform(1, 2))
        password_field.send_keys(Keys.RETURN)

        # 等待登录完成
        time.sleep(8)

        # 检查是否有错误信息
        error_elements = driver.find_elements(By.XPATH,
                                              "//*[contains(text(), 'incorrect') or contains(text(), '错误') or contains(text(), 'Sorry')]")
        if error_elements:
            print("❌ 登录失败，可能是用户名或密码错误")
            for error in error_elements:
                print(f"错误信息: {error.text}")
            return False

        # 处理各种弹窗
        popup_selectors = [
            "//button[contains(text(), 'Not Now')]",
            "//button[contains(text(), '稍后再说')]",
            "//button[contains(text(), '现在不')]",
            "//button[contains(text(), 'Save Info')]",
            "//button[contains(text(), '保存信息')]",
            "//button[@class='_a9-- _a9_1']"  # 通用关闭按钮
        ]

        for selector in popup_selectors:
            try:
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                ).click()
                time.sleep(2)
                print(f"已处理弹窗")
            except:
                continue

        # 验证登录状态
        time.sleep(3)
        if check_login_status(driver):
            print("✅ 登录成功")
            return True
        else:
            print("❌ 登录验证失败")
            debug_page_content(driver)
            return False

    except Exception as e:
        print(f"❌ 登录过程中出错: {e}")
        debug_page_content(driver)
        return False


# -------- 检查登录状态 --------
def check_login_status(driver):
    """检查是否成功登录"""
    try:
        # 检查是否在登录页面
        if "login" in driver.current_url:
            print("❌ 仍然在登录页面，登录可能失败")
            return False

        # 检查是否有搜索框（登录成功的标志）
        search_elements = driver.find_elements(By.CSS_SELECTOR,
                                               "input[placeholder*='搜索'], input[placeholder*='Search']")
        if search_elements:
            print("✅ 登录成功")
            return True

        print("⚠️ 登录状态不确定")
        return False
    except:
        return False


# -------- 调试页面内容 --------
def debug_page_content(driver):
    """调试当前页面内容"""
    print(f"当前URL: {driver.current_url}")
    print(f"页面标题: {driver.title}")

    # 保存页面截图
    try:
        driver.save_screenshot("debug_screenshot.png")
        print("页面截图已保存: debug_screenshot.png")
    except:
        pass

    # 保存页面源码
    try:
        with open("debug_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("页面源码已保存: debug_page_source.html")
    except:
        pass

    # 检查是否有错误信息
    error_messages = driver.find_elements(By.XPATH,
                                          "//*[contains(text(), 'Sorry') or contains(text(), '抱歉') or contains(text(), 'Error') or contains(text(), '错误')]")
    if error_messages:
        for msg in error_messages:
            print(f"发现错误信息: {msg.text}")


# -------- 收集Reels链接 --------
def scroll_and_collect_reel_links(driver, max_scrolls=10):
    print(f"访问 {TARGET_USER} 的Reels页面...")

    # 首先检查登录状态
    if not check_login_status(driver):
        print("❌ 登录验证失败，尝试重新登录")
        return []

    # 访问用户主页
    profile_url = f"https://www.instagram.com/{TARGET_USER}/"
    print(f"先访问用户主页: {profile_url}")
    driver.get(profile_url)
    time.sleep(random.uniform(3, 5))

    # 检查用户是否存在
    if "Page Not Found" in driver.page_source or "用户不存在" in driver.page_source:
        print(f"❌ 用户 {TARGET_USER} 不存在或无法访问")
        debug_page_content(driver)
        return []

    # 查找Reels标签并点击
    reels_tab_found = False
    reels_selectors = [
        "a[href*='/reels/']",
        "//a[contains(@href, '/reels/')]",
        "//a[contains(text(), 'Reels') or contains(text(), '短视频')]"
    ]

    for selector in reels_selectors:
        try:
            if selector.startswith("//"):
                reels_tab = driver.find_element(By.XPATH, selector)
            else:
                reels_tab = driver.find_element(By.CSS_SELECTOR, selector)

            print(f"找到Reels标签，点击...")
            driver.execute_script("arguments[0].click();", reels_tab)
            time.sleep(random.uniform(3, 5))
            reels_tab_found = True
            break
        except:
            continue

    if not reels_tab_found:
        print("❌ 没有找到Reels标签，可能该用户没有发布Reels")
        debug_page_content(driver)
        return []

    # 等待Reels页面加载，使用更宽松的条件
    print("等待Reels内容加载...")
    wait_selectors = [
        "article",
        "div[role='main']",
        "main",
        "//div[contains(@class, 'reel') or contains(@class, 'video')]"
    ]

    page_loaded = False
    for selector in wait_selectors:
        try:
            if selector.startswith("//"):
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            else:
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            page_loaded = True
            print(f"✅ 页面加载成功，找到元素: {selector}")
            break
        except:
            continue

    if not page_loaded:
        print("❌ Reels页面加载超时")
        debug_page_content(driver)
        return []

    # 开始收集链接
    links = set()
    scroll_count = 0
    no_new_links_count = 0

    print("开始收集Reels链接...")

    while scroll_count < max_scrolls and no_new_links_count < 3:
        initial_count = len(links)

        # 多种选择器尝试查找reel链接
        link_selectors = [
            "a[href*='/reel/']",
            "a[href*='/p/']",  # 有时reels也用/p/
            "//a[contains(@href, '/reel/')]",
            "//a[contains(@href, '/p/')]"
        ]

        for selector in link_selectors:
            try:
                if selector.startswith("//"):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)

                for elem in elements:
                    href = elem.get_attribute("href")
                    if href and ('/reel/' in href or '/p/' in href) and href not in links:
                        links.add(href)
                        print(f"发现新链接: {href}")
            except:
                continue

        # 检查是否有新链接
        if len(links) == initial_count:
            no_new_links_count += 1
        else:
            no_new_links_count = 0

        # 滚动页面
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(3, 5))
        scroll_count += 1

        print(f"已滚动 {scroll_count}/{max_scrolls} 次，当前找到 {len(links)} 个链接")

    if not links:
        print("❌ 没有找到任何链接，进行调试...")
        debug_page_content(driver)

    print(f"共收集到 {len(links)} 个链接")
    return list(links)


# -------- 提取视频URL --------
def extract_video_url(driver, post_url):
    print(f"正在提取视频: {post_url}")
    driver.get(post_url)

    # 等待视频元素加载
    try:
        video_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )

        # 多种方式尝试获取视频URL
        video_url = None

        # 方式1: 直接获取src属性
        video_url = video_element.get_attribute("src")
        if video_url:
            print(f"✅ 通过src属性获取到视频URL")
            return video_url

        # 方式2: 查找source标签
        sources = driver.find_elements(By.CSS_SELECTOR, "video source")
        for source in sources:
            src = source.get_attribute("src")
            if src:
                print(f"✅ 通过source标签获取到视频URL")
                return src

        # 方式3: 执行JavaScript获取
        video_url = driver.execute_script("""
            const video = document.querySelector('video');
            return video ? video.src || video.currentSrc : null;
        """)

        if video_url:
            print(f"✅ 通过JavaScript获取到视频URL")
            return video_url

        # 方式4: 从网络请求中获取
        time.sleep(3)  # 等待视频加载
        logs = driver.get_log('performance')
        for log in logs:
            message = json.loads(log['message'])
            if message['message']['method'] == 'Network.responseReceived':
                url = message['message']['params']['response']['url']
                if '.mp4' in url or 'video' in url:
                    print(f"✅ 从网络日志获取到视频URL")
                    return url

    except Exception as e:
        print(f"❌ 提取视频URL失败: {e}")

    return None


# -------- 下载视频 --------
def download_video(url, folder, filename):
    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = os.path.join(folder, filename)

    # 如果文件已存在，跳过
    if os.path.exists(filepath):
        print(f"⏭️ 文件已存在，跳过: {filename}")
        return True

    try:
        print(f"正在下载: {filename}")

        # 创建session以支持代理
        session = requests.Session()
        if PROXY:
            session.proxies = {
                'http': f'http://{PROXY}',
                'https': f'http://{PROXY}'
            }

        # 发送请求
        response = session.get(url, headers=HEADERS, stream=True, timeout=30)
        response.raise_for_status()

        # 写入文件
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"✅ 下载成功: {filename}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败 {filename}: {e}")
        return False
    except Exception as e:
        print(f"❌ 下载异常 {filename}: {e}")
        return False


# -------- 主函数 --------
def main():
    driver = None
    try:
        # 创建驱动器
        print("正在启动浏览器...")
        driver = create_driver()
        print("✅ 浏览器启动成功")

        # 登录
        if not instagram_login(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD):
            print("❌ 登录失败，程序退出")
            return

        # 收集链接
        reel_links = scroll_and_collect_reel_links(driver)

        if not reel_links:
            print("❌ 没有找到任何Reels链接，程序退出")
            return

        print(f"找到 {len(reel_links)} 个链接，开始下载...")

        # 提取和下载视频
        success_count = 0
        total_count = len(reel_links)

        for i, link in enumerate(reel_links, 1):
            print(f"\n处理第 {i}/{total_count} 个视频...")

            # 提取视频URL
            video_url = extract_video_url(driver, link)

            if video_url:
                # 生成文件名
                reel_id = link.split('/reel/')[-1].split('/')[0] if '/reel/' in link else \
                link.split('/p/')[-1].split('/')[0]
                filename = f"{TARGET_USER}_reel_{reel_id}.mp4"

                # 下载视频
                if download_video(video_url, DOWNLOAD_FOLDER, filename):
                    success_count += 1
            else:
                print(f"❌ 无法提取视频URL: {link}")

            # 随机延迟，避免被检测
            time.sleep(random.uniform(2, 5))

        print(f"\n🎉 下载完成! 成功: {success_count}/{total_count}")

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()

        # 调试信息
        if driver:
            debug_page_content(driver)

    finally:
        if driver:
            print("正在关闭浏览器...")
            driver.quit()


if __name__ == '__main__':
    main()