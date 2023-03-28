# 从萌娘百科获取干员图片
# 现在萌娘百科网站有反爬虫机制了，有的时候获取不了

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import json

# 萌娘百科网站
operator_url = "https://zh.moegirl.org.cn/明日方舟:"

# driver = webdriver.Edge("C:/Users/Johnny Song/edgedriver_win64/msedgedriver.exe")
driver = webdriver.Safari()


def get_operator_img(name):
    """从萌娘百科获取干员立绘"""
    # name: chinese name
    filename = "img/illustration/" + name + ".png"
    if os.path.exists(filename):
        print("img already at:", filename)  # don't overwrite
        return filename

    img_url = "https://zh.moegirl.org.cn/File:明日方舟立绘_" + name + "_1.png"
    url = operator_url + name + "#"
    driver.get(img_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))

    # div = driver.find_element(By.CLASS_NAME, "ak-operator-complex")
    # img = div.find_element(By.CLASS_NAME, "TabContentText").find_element(By.TAG_NAME, "img").get_attribute("src")
    # 获得真实url
    img = driver.find_element(By.CSS_SELECTOR, "div .fullImageLink").find_element(By.TAG_NAME, "a").get_attribute("href")
    print(img)
    picture = requests.get(img).content

    with open(filename, "wb") as file:
        file.write(picture)
        print("saved", filename)
        return filename


def get_long_img(name, img):
    """从萌娘百科获取干员半身像"""
    filename = "img/long_image/" + name + ".png"
    if os.path.exists(filename):
        print("img already at:", filename)  # don't overwrite
        return filename

    picture = requests.get(img).content

    with open(filename, "wb") as file:
        file.write(picture)
        print("saved", filename)
        return filename


def get_head_img():
    banners = json.load(open("banners.json"))
    print(len(banners))
    for b in banners:
        for o in b["prob_up"]:
            print(o)
            filename = "img/head_image/" + o["name"] + ".png"
            if os.path.exists(filename):
                print("img already at:", filename)  # don't overwrite
                continue
            try:
                # 保存头像图片
                img = o["img"]
                print(img)
                picture = requests.get(img).content
                with open(filename, "wb") as file:
                    file.write(picture)
                    print("saved", filename)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    get_head_img()
    driver.close()
