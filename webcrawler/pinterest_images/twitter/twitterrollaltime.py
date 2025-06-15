from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests

# Clash 代理地址（请根据你实际修改）
PROXY = "127.0.0.1:7890"

# ChromeDriver 路径
driver_path = r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe"

# 目标Twitter账号主页和登录页
TWITTER_URL = "https://twitter.com/DirtyAngelXXX"
TWITTER_LOGIN_URL = "https://twitter.com/login"

# 图片保存目录
SAVE_DIR = "twitter_photos"
os.makedirs(SAVE_DIR, exist_ok=True)

# 你的Twitter账号和密码，替换成真实的
TWITTER_USERNAME = "luckybigdick"
TWITTER_PASSWORD = "4673597wx"


def setup_driver(proxy=PROXY):
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=http://{proxy}')
    # chrome_options.add_argument("--headless")  # 如果不想看浏览器窗口，取消注释

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def twitter_login(driver, username, password):
    driver.get(TWITTER_LOGIN_URL)
    wait = WebDriverWait(driver, 15)

    # 输入用户名
    username_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
    username_input.send_keys(username)

    # 点击“下一步”
    next_button = driver.find_element(By.XPATH, '//span[text()="下一步" or text()="Next"]/..')
    next_button.click()

    # 等待密码输入框，输入密码
    password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    password_input.send_keys(password)

    # 点击登录
    login_button = driver.find_element(By.XPATH, '//span[text()="登录" or text()="Log in"]/..')
    login_button.click()

    # 等待主页加载完成，确认登录成功
    wait.until(EC.presence_of_element_located((By.XPATH, '//a[@href="/home"]')))
    print("登录成功！")


def infinite_scroll_and_collect_images(driver, scroll_pause_time=3, max_no_change=3):
    """
    无限滚动直到页面高度连续max_no_change次不变化，认为到底了。
    每次滚动后收集图片链接，返回全部图片URL集合。
    """
    img_urls = set()
    no_change_count = 0
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        # 收集图片链接
        imgs = driver.find_elements(By.XPATH, '//img[contains(@src,"twimg.com/media")]')
        for img in imgs:
            src = img.get_attribute("src")
            if src:
                img_urls.add(src.split("?")[0])

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            no_change_count += 1
            print(f"页面高度未变化，连续{no_change_count}次")
            if no_change_count >= max_no_change:
                print("检测到底，停止滚动。")
                break
        else:
            no_change_count = 0
            last_height = new_height
            print(f"页面高度更新为{new_height}，继续滚动...")

    return img_urls


def download_image(url, folder=SAVE_DIR):
    # 加上参数请求大图
    url_with_params = url + "?format=jpg&name=large"

    local_filename = os.path.join(folder, url.split("/")[-1].split("?")[0] + ".jpg")
    if os.path.exists(local_filename):
        print(f"已存在，跳过：{local_filename}")
        return
    try:
        proxies = {"http": f"http://{PROXY}", "https": f"http://{PROXY}"}
        r = requests.get(url_with_params, proxies=proxies, timeout=15)
        if r.status_code == 200:
            with open(local_filename, 'wb') as f:
                f.write(r.content)
            print(f"下载成功：{local_filename}")
        else:
            print(f"下载失败，状态码：{r.status_code}，URL：{url_with_params}")
    except Exception as e:
        print(f"下载异常：{e}，URL：{url_with_params}")


def main():
    driver = setup_driver()
    try:
        twitter_login(driver, TWITTER_USERNAME, TWITTER_PASSWORD)
        time.sleep(3)

        driver.get(TWITTER_URL)
        time.sleep(5)

        img_urls = infinite_scroll_and_collect_images(driver, scroll_pause_time=3, max_no_change=3)

        print(f"共找到 {len(img_urls)} 张图片，开始下载...")
        for url in img_urls:
            download_image(url)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
