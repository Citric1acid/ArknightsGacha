# 模拟寻访系统
# 用flask运行的服务器

from flask import Flask, request, Response, abort
from werkzeug.datastructures import ImmutableMultiDict
import webbrowser
import os
import json

app = Flask(__name__)

operators: list = json.load(open('operators.json', encoding='utf-8'))
operators_dict = {item['name']: item for item in operators}
banners: list = json.load(open('banners.json', encoding='utf-8'))


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
    o = data.to_dict()
    name = o['name']
    if not name:
        return get_file('add.html')
    if not o['star']:
        return get_file('add.html')
    o['star'] = int(o['star'])
    o['limited'] = int(o['limited'])
    if name not in operators_dict:
        print("adding operator:", o)
        operators.append(o)
        operators_dict[name] = o
    else:
        operators_dict[name].update(o)
        print("updating operator:", operators_dict[name])
    json.dump(operators, open('operators.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

    return get_file('add.html')


@app.route('/add_banner.html', methods=['POST'])
def add_banner():
    data: ImmutableMultiDict = request.form
    print(data)
    o: dict[str] = data.to_dict()
    banner_name = o['banner_name']
    if not banner_name:
        return get_file('add_banner.html')
    if o['limited'] == '1':
        limited = True
    else:
        limited = False
    try:
        prob_up = []
        for k, v in o.items():
            if 'up' in k:
                if not v: continue  # empty name
                if v not in operators_dict:
                    raise ValueError
                star = operators_dict[v]['star']
                if 'q5' in k:  # 5倍概率
                    p = '*5'
                else:
                    p = float(o['prob' + str(star)])
                prob_up.append({
                    'name': v,
                    'star': star,
                    'prob': p
                })
        b = {
            'banner_name': banner_name,
            'limited': limited,
            'prob_up': prob_up
        }
        print("adding banner:", b)
        banners.append(b)
        json.dump(banners, open('banners.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    except ValueError:  # invalid value in the form
        pass
    return get_file('add_banner.html')


if __name__ == '__main__':
    port = 7001
    print(f'server running at localhost:{port}')
    webbrowser.open(f'localhost:{port}')
    app.run('0.0.0.0', port)
