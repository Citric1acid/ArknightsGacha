# class of Arknights operator
import json
from objprint import objjson

# 读取不可寻访干员
with open("not_in_banner.dat") as file:
    not_in_banner = file.read().split()

# 读取限定干员
with open("limited.dat") as file:
    limited = file.read().split()

# 读取较早的干员（只在中坚寻访中出现）
with open("early.dat") as file:
    early = file.read().split()


class Operator:
    """明日方舟干员"""
    STAR = "★"
    # 所有职业
    careers = ["先锋", "狙击", "近卫", "术师", "重装", "医疗", "特种", "辅助"]
    careers_en = ["vanguard", "sniper", "guard", "caster", "defender", "medic", "specialist", "supporter"]

    def __init__(self, name: str, en_name: str, star: int, career: str, link=None,
                 img=None, long_img=None, sm_img=None, in_pool=None):
        # in_pool: 0 = never, 1 = always, 2 = limited, 3 = early
        self.name = name
        self.en_name = en_name
        self.star = star
        self.career = career
        self.link = link
        self.img = img
        self.long_img = long_img
        self.sm_img = sm_img
        if in_pool is not None:
            self.in_pool = in_pool
        elif name in limited:
            self.in_pool = 2
        elif star < 3 or name in not_in_banner:
            self.in_pool = 0
        elif name in early:
            self.in_pool = 3
        else:
            self.in_pool = 1

    @classmethod
    def from_json(cls, filename):
        return json.load(open(filename, encoding='utf-8'), object_hook=parse)

    def to_json(self):
        return objjson(self)

    def __str__(self):
        return 'Operator({}, {}, {}, {}, ..., {})'.format(self.name, self.en_name, self.star, self.career, self.in_pool)

    def display(self):
        print(Operator.STAR * self.star, self.name, self.en_name, self.career)

    def update(self, other):
        if other.name: self.name = other.name
        if other.en_name: self.en_name = other.en_name
        if other.star: self.star = other.star
        if other.career: self.career = other.career
        if other.in_pool: self.in_pool = other.in_pool


class Banner:
    def __init__(self, banner_name: str, limited: int, prob_up: dict, choices=None):
        self.banner_name = banner_name
        self.limited = limited
        self.prob_up = prob_up

    @classmethod
    def from_json(cls, filename):
        return json.load(open(filename, encoding='utf-8'), object_hook=parse)

    def to_json(self):
        return objjson(self)

    def __str__(self):
        return 'Banner({}, {}, {})'.format(self.banner_name, self.limited, self.prob_up)

    def update(self, other):
        if other.banner_name: self.banner_name = other.banner_name
        if other.limited: self.limited = other.limited
        if other.prob_up: self.prob_up = other.prob_up


def parse(obj: dict):
    if '.type' not in obj:  # default
        return obj
    type = obj['.type']
    del obj['.type']
    if type == 'Operator':
        return Operator(**obj)
    elif type == 'Banner':
        return Banner(**obj)
    else:
        return obj
