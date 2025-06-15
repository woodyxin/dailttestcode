from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time

# 代理地址
proxy = "127.0.0.1:7890"

# 1. 指定 chromedriver 路径，创建 Service 对象
service = Service(r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe")

# 2. 配置 Chrome 代理选项
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f'--proxy-server=http://{proxy}')

# 3. 用 Service 启动 ChromeDriver，带代理参数
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get("https://www.pinterest.com/login/")

    # 等待账号输入框出现
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "id")))

    # 输入账号和密码
    driver.find_element(By.NAME, "id").send_keys("99woodyxin@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("4673597wx")

    # 点击登录按钮
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # 等待登录成功，页面加载
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))

    # 滚动页面加载更多图片
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    imgs = driver.find_elements(By.TAG_NAME, "img")
    print(f"找到图片数量: {len(imgs)}")

    # 创建 requests session，带代理
    session = requests.Session()
    session.proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }

    DOWNLOAD_FOLDER = "pinterest_images"
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    # 转换 selenium 的 cookie 到 requests session
    selenium_cookies = driver.get_cookies()
    for cookie in selenium_cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    count = 0
    for img in imgs:
        src = img.get_attribute("src")
        if src and src.startswith("http"):
            try:
                if src.endswith(".jpg") or src.endswith(".png"):
                    img_data = session.get(src).content
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
