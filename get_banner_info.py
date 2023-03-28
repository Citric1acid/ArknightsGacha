# 从萌娘百科获取卡池信息

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from objprint import objjson
import requests
import os
import json

# 获取卡池的页面
banner_url = "https://zh.moegirl.org.cn/zh-cn/明日方舟/卡池"
output = "banners.json"

driver = webdriver.Safari()


class Banner:
    # {"banner_name": banner_name, "limited": bool, "prob_up": List[(name, star, prob, img)]}
    def __init__(self, banner_name: str, limited: bool, names: list, stars: list, probs: list, imgs: list):
        self.banner_name = banner_name
        self.limited = limited
        self.prob_up = [{"name": names[i], "star": stars[i], "prob": probs[i], "img": imgs[i]} for i in range(len(names))]

    def get_img(self):
        for operator in self.prob_up:
            filename = "img/head_image/" + operator["name"] + ".png"
            if os.path.exists(filename):
                print("img already at:", filename)  # don't overwrite
                continue
            try:
                # 保存头像图片
                picture = requests.get(operator["img"]).content
                with open(filename, "wb") as file:
                    file.write(picture)
                    print("saved", filename)
            except Exception as e:
                print(e)


def get_banners() -> list[Banner]:
    # 先获得所有干员信息
    with open("operators.json") as file:
        data = json.load(file)
        all_operators = {x["name"]: x for x in data}

    driver.get(banner_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    result = []
    banners = driver.find_element(By.TAG_NAME, "table").find_elements(By.TAG_NAME, "tr")
    for b in banners:
        td = b.find_elements(By.TAG_NAME, "td")
        if not td: continue
        name = td[0].text.split('※', 1)[0].rstrip()
        print(name)
        # 从第二列和第三列获得概率提升的干员
        up = td[1].find_elements(By.TAG_NAME, "a") + td[2].find_elements(By.TAG_NAME, "a")
        operators = [a.get_attribute("title") for a in up]
        print(operators)
        stars = [all_operators[o]["star"] for o in operators]
        limited = any(all_operators[o]["in_pool"] == 2 for o in operators)
        if not operators:  # 没有概率提升干员
            limited = True
        head_imgs = [a.find_element(By.TAG_NAME, "img").get_attribute("data-lazy-src") for a in up]

        # 如果没有限定，默认概率是六星50%, 五星50%, 四星20%
        prob = [0.5 if s >= 5 else 0.2 for s in stars]
        if limited and len(operators) >= 2:
            # 简化成前两个六星70%, 后几个六星*5
            if stars[0] == 6 and stars[1] == 6:
                prob[0] = prob[1] = 0.7
            for i in range(2, len(operators)):
                if stars[i] == 6:
                    prob[i] = "*5"

        banner = Banner(name, limited, operators, stars, prob, head_imgs)
        result.append(banner)

    return result


if __name__ == '__main__':
    banners = get_banners()
    for b in banners:
        b.get_img()

    # 转换成json文件
    banners_json = objjson(banners)
    json.dump(banners_json, open(output, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=4)
    with open("banners_.js", "w", encoding="utf-8") as file:
        file.write("banners = " + json.dumps(banners_json, ensure_ascii=False, indent=4))
    print("保存至", output)
    driver.close()
