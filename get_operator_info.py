# 明日方舟模拟寻访系统
# 从萌娘百科获取干员信息

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
from objprint import objjson
import json
import atexit
from ak_operator import Operator

website = "https://zh.moegirl.org.cn/明日方舟/干员图鉴#"
driver_path = ""
outputfile = "operators.json"

try:
    driver = webdriver.Safari()
except WebDriverException:
    driver = webdriver.Edge()
atexit.register(driver.close)


def get_info(_max_count=None) -> list[Operator]:
    """用selenium从萌娘百科网站获取所有干员信息"""
    driver.get(website)
    driver.implicitly_wait(10)
    # 关闭弹窗
    if ec.presence_of_element_located((By.CLASS_NAME, "n-card")):
        close_button = driver.find_element(By.CLASS_NAME, "n-card").find_element(By.TAG_NAME, "button")
        print("关闭弹窗")
        close_button.click()
    # 等待加载
    WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.CLASS_NAME, "akIllLayer7")))

    result = []
    container = driver.find_element(By.CLASS_NAME, "mw-parser-output")
    operator_panel = container.find_elements(By.CLASS_NAME, "akIll")
    if _max_count:  # only for test
        operator_panel = operator_panel[:_max_count]
    for o in operator_panel:
        # 获得并储存干员信息
        name = o.find_element(By.CLASS_NAME, "akIllLayer7").text
        en_name = o.find_element(By.CLASS_NAME, "akIllLayer8").text
        star = len(o.find_element(By.CLASS_NAME, "akIllLayer1").find_element(By.TAG_NAME, "img").get_attribute("alt"))
        career = o.find_element(By.CLASS_NAME, "akIllLayer4").find_element(By.TAG_NAME, "img").get_attribute("alt")
        link = "https://zh.moegirl.org.cn/明日方舟:" + name + "#"
        m = o.find_element(By.CLASS_NAME, "akIllLayer2").find_element(By.TAG_NAME, "img")
        img = m.get_attribute("src") or m.get_attribute("data-lazy-src")

        operator = Operator(name, en_name, star, career, link, long_img=img)
        operator.display()
        result.append(operator)

    return result


if __name__ == '__main__':
    info = get_info()
    # 转换成json文件
    data = objjson(info)
    json.dump(data, open(outputfile, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=4)
    print("保存至", outputfile)
    print("共有", len(info), "干员")
