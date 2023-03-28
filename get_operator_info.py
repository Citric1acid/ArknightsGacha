# 明日方舟模拟寻访系统
# get operator info from moegirl website

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from objprint import objjson
import json
import atexit
import img_scratcher

website = "https://zh.moegirl.org.cn/明日方舟/干员图鉴#"
driver_path = ""
outputfile = "operators.json"
output_pools = "pools.json"

# driver = webdriver.Safari()
driver = img_scratcher.driver  # 避免重复创建driver
atexit.register(driver.close)


class Operator:
    """明日方舟干员"""
    # 现阶段需手动添加新干员是否不可寻访/是否限定的信息
    STAR = "★"
    # 所有职业
    careers = ["先锋", "狙击", "近卫", "术师", "重装", "医疗", "特种", "辅助"]
    careers_en = ["vanguard", "sniper", "guard", "caster", "defender", "medic", "specialist", "supporter"]
    # 不可寻访干员
    not_in_banner = {'阿米娅', '暴行', '断罪者', '九色鹿',
                   '安德切尔', '艾丝黛尔', '清流', '因陀罗', '火神',
                   '讯使', '嘉维尔', '坚雷', '伊桑', '微风', '布丁', '蜜莓', '石英', '雪绒', '柏喙', '稀音', '图耶', '埃拉托',
                   '格拉尼', '锡兰', '炎客', '拜松', '雪雉', '铸铁', '苦艾', '亚叶', '特米米', '薄绿', '鞭刃', '罗宾',
                   '炎狱炎熔', '暴雨', '歌蕾蒂娅', '贝娜', '龙舌兰', '野鬃', '耶拉', '寒芒克洛丝', '暮落', '见行者', '海蒂',
                   '流明', '车尔尼', '星源', '至简', '海沫', '达格达', '伺夜', '谜图', '截云',
                   '灰烬', '霜华', '闪击', '战车', '罗小黑'}
    # 限定干员
    limited = {'年', 'W', '迷迭香', '夕', '浊心斯卡蒂', '假日威龙陈', '耀骑士临光', '令', '归溟幽灵鲨', '百炼嘉维尔', '缄默德克萨斯', '重岳'}

    def __init__(self, name: str, en_name: str, star: int, career: str, link=None, img=None, in_pool=None):
        # in_pool: 0 = never, 1 = always, 2 = limited
        self.name = name
        self.en_name = en_name
        self.star = star
        self.career = career
        self.link = link
        self.img = img
        if in_pool is not None:
            self.in_pool = in_pool
        elif name in Operator.limited:
            self.in_pool = 2
        elif star < 3 or name in Operator.not_in_banner:
            self.in_pool = 0
        else:
            self.in_pool = 1

    def display(self):
        print(Operator.STAR * self.star, self.name, self.en_name, self.career)

    def store_img_file(self):
        img_scratcher.get_operator_img(self.name)
        if self.img is not None:
            img_scratcher.get_long_img(self.name, self.img)


def get_info(_max_count=None) -> list[Operator]:
    """用selenium从萌娘百科网站获取所有干员信息"""
    driver.get(website)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))

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

        operator = Operator(name, en_name, star, career, link, img)
        operator.display()
        result.append(operator)

    return result


if __name__ == '__main__':
    info = get_info()
    # 获取图片
    for operator in info:
        try:
            operator.store_img_file()
        except Exception as e:
            print(e)
            
    # 转换成json文件
    info_json = objjson(info)
    json.dump(info_json, open(outputfile, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=4)
    with open("operators_.js", "w", encoding="utf-8") as file:
        file.write("operators = " + json.dumps(info_json, ensure_ascii=False, indent=4))
    print("保存至", outputfile)
    print("共有", len(info), "干员")
