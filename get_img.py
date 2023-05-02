# 从萌娘百科和PRTS wiki获取干员图片
# 现在萌娘百科网站有反爬虫机制了，有的时候获取不了

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
import requests
import os
import json
from objprint import objjson
import atexit
from ak_operator import Operator

outputfile = "operators.json"

try:
    driver = webdriver.Safari()
except WebDriverException:
    driver = webdriver.Edge()


def get_img_url(o: Operator):
    name = o.name
    img_url = "https://zh.moegirl.org.cn/File:明日方舟立绘_" + name + "_1.png"
    driver.get(img_url)
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, "img")))

    # 获得真实url
    img = driver.find_element(By.CSS_SELECTOR, "div .fullImageLink").find_element(By.TAG_NAME, "a").get_attribute(
        "href")
    print(name, img)
    o.img = img
    return img


def get_img(o: Operator):
    """从萌娘百科获取干员立绘"""
    name = o.name
    filename = "img/illustration/" + name + ".png"
    if os.path.exists(filename):
        print("img already at:", filename)  # don't overwrite
        return filename

    img = o.img or get_img_url(o)
    picture = requests.get(img).content
    with open(filename, "wb") as file:
        file.write(picture)
        print("saved", filename)
        return filename


def get_long_img(o: Operator):
    """从萌娘百科获取干员半身像"""
    name = o.name
    long_img = o.long_img
    filename = "img/long_image/" + name + ".png"
    if os.path.exists(filename):
        print("img already at:", filename)  # don't overwrite
        return filename

    picture = requests.get(long_img).content
    with open(filename, "wb") as file:
        file.write(picture)
        print("saved", filename)
        return filename


def get_head_img_url(operators_dict: dict[str, Operator]):
    """从PRTS wiki获得头像"""
    from math import ceil
    url = "https://prts.wiki/w/干员一览"
    driver.get(url)
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, "table#result-table")))

    table = driver.find_element(By.CSS_SELECTOR, "table#result-table")
    next_page = driver.find_element(By.ID, "NextPage")
    pages = ceil(len(operators_dict) / 50)
    for i in range(pages):
        # WebDriverWait(driver, 5).until(lambda x: table.find_element(By.TAG_NAME, "img").is_displayed)
        rows = table.find_elements(By.CSS_SELECTOR, "tr.result-row")
        for r in rows:
            img = r.find_element(By.TAG_NAME, "img")
            # scroll until img shows up
            img.location_once_scrolled_into_view
            WebDriverWait(driver, 1).until(lambda x: img.is_displayed())
            sm_img = img.get_attribute("src")
            div = r.find_elements(By.TAG_NAME, "td")[1].find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div")
            name = div.text
            print(name, sm_img)
            try:
                operators_dict[name].sm_img = sm_img
            except KeyError:
                pass
        # go to the next page
        next_page.click()


def get_head_img(o: Operator):
    name = o.name
    filename = "img/head_image/" + name + ".png"
    if os.path.exists(filename):
        print("img already at:", filename)  # don't overwrite
        return filename

    sm_img = o.sm_img
    if not sm_img:
        print("no head img for ", name)
        return
    picture = requests.get(sm_img).content
    with open(filename, "wb") as file:
        file.write(picture)
        print("saved", filename)
        return filename


if __name__ == "__main__":
    atexit.register(driver.close)
    operators: list[Operator] = Operator.from_json("operators.json")
    operators_dict = {o.name: o for o in operators}
    get_head_img_url(operators_dict)
    for o in operators:
        get_head_img(o)
        get_img_url(o)
        get_img(o)
        get_long_img(o)
    data = objjson(operators)
    json.dump(data, open(outputfile, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=4)
    print("保存至", outputfile)
    print("共有", len(operators), "干员")
