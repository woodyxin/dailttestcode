from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()

# 设置代理地址，端口根据你 Clash 实际配置调整
chrome_options.add_argument('--proxy-server=http://127.0.0.1:7890')

service = Service(r"D:\1_development\06 TOOL\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://au.pinterest.com/")
print(driver.title)
print("success")

driver.quit()
