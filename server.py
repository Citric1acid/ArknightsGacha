# 模拟寻访系统的主程序, 运行将打开一个本地服务器
# 用flask运行的服务器
from flask import Flask, request, abort
from werkzeug.datastructures import ImmutableMultiDict
import webbrowser
import os
import json
from objprint import objjson
from ak_operator import Operator, Banner

# activate venv
_activate_file = "venv/bin/activate_this.py"
exec(open(_activate_file).read(), {'__file__': _activate_file})

# create flask server
app = Flask(__name__)

# read operators and banners
operators: list[Operator] = Operator.from_json("operators.json")
operators_dict: dict[str, Operator] = {o.name: o for o in operators}
banners: list[Banner] = Banner.from_json("banners.json")
banners_dict: dict[str, Banner] = {b.banner_name: b for b in banners}


@app.route('/', methods=['GET'])
def root():
    return get_file('index.html')


@app.route('/<path:path>', methods=['GET'])
def get_file(path='', **kwargs):
    if not os.path.exists(path):
        abort(404)
        return
    if not is_valid(path):
        abort(403)
        return
    with open(path, 'rb') as file:
        content = file.read()
        if kwargs:
            content = str(content).format(**kwargs)
        return content


def is_valid(path) -> bool:
    return os.path.isfile(path)


@app.route('/add.html', methods=['POST'])
def add_data():
    data: ImmutableMultiDict = request.form
    print(data)
    # ImmutableMultiDict([('name', '仇白'), ('en_name', 'Qiubai'), ('star', '6'),
    # ('career', '近卫'), ('picture', ''), ('limited', '1')])
    name = data['name']
    if not name:
        return get_file('add.html')
    try:
        o = Operator(name, data['en_name'], int(data['star']), data['career'], in_pool=int(data['in_pool']))
        # if data['get_img'] == '1':  # add img automatically
        #     import get_img
        #     get_img.get_img_url(o)
        #     get_img.get_img(o)
    except ValueError as err:
        print(err)
        return get_file('add.html')
    if name not in operators_dict:
        print("adding operator:", o)
        operators.append(o)
        operators_dict[name] = o
        if o.in_pool == 0:  # not in pool
            with open("not_in_banner.dat", "a") as file:
                file.write(" " + o.name)
        if o.in_pool == 2:  # limited
            with open("limited.dat", "a") as file:
                file.write(" " + o.name)
        if o.in_pool == 3:  # early
            with open("early.dat", "a") as file:
                file.write(" " + o.name)
    else:
        operators_dict[name].update(o)
        print("updating operator:", operators_dict[name])
    json.dump(objjson(operators), open('operators.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    return get_file('add.html')


@app.route('/add_banner.html', methods=['POST'])
def add_banner():
    data: ImmutableMultiDict = request.form
    print(data)
    d: dict[str] = data.to_dict()
    banner_name = d['banner_name']
    if not banner_name:
        return get_file('add_banner.html')
    try:
        limited = int(d['limited'])
        prob_up = {}
        # {6: {'star': 6, 'prob': 0.5, names: [...]}, ...}
        for k, v in d.items():
            if not v: continue  # empty value
            if 'prob' in k:  # probabilities
                if k == 'probq5':  # 5倍概率提升
                    prob_up['*5'] = {'star': 6, 'prob': '*5', 'names': []}
                else:
                    star = int(k.removeprefix('prob'))
                    prob_up[star] = {'star': star, 'prob': float(v), 'names': []}
            if 'up' in k:  # names
                if v not in operators_dict:
                    raise ValueError
                star = operators_dict[v].star
                if 'q5' in k:  # 5倍概率
                    star = '*5'
                prob_up[star]['names'].append(v)
        b = Banner(banner_name, limited, prob_up)
    except ValueError as err:  # invalid value in the form
        print(err)
        return get_file("add_banner.html")
    if banner_name not in banners_dict:
        banners.append(b)
        banners_dict[banner_name] = b
        print("adding banner:", b)
    else:
        banners_dict[banner_name].update(b)
        print("updating banner", banners_dict[banner_name])
    json.dump(objjson(banners), open('banners.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    return get_file('add_banner.html')


if __name__ == '__main__':
    port = 7001
    print(f'server running at localhost:{port}')
    webbrowser.open(f'localhost:{port}')
    app.run('0.0.0.0', port)
