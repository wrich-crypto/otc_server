import json
from flask import Flask, request
from flask_cors import CORS
from product import Otc

app = Flask(__name__)
CORS(app)


@app.route('/login', methods=['POST'])
def login():
    #todo 用address查库返回用户名
    _data = json.loads(request.data)
    _address = _data['address']
    data = {
        'name':'jason'
    }
    return json.dumps(data)

@app.route('/initOptions', methods=['POST'])
def initOption():
    # todo 参考option_list给前台传参
    option_list = []
    option_list.append({
        "name":"eths"
    })
    option_list.append({
        "name":"terc-20"
    })

    return json.dumps(option_list)

@app.route('/add', methods=['POST'])
def add():
    _data = json.loads(request.data)
    _name,_type,_count = _data['name'],_data['type'],_data['count']
    #todo 新增一条挂单数据
    #todo 最后返回成功失败


@app.route('/search', methods=['POST'])
def search():
    _data = json.loads(request.data)
    _s_name = _data['name']
    _s_type = _data['type']
    #todo 用这俩参数去查数据然后传list给前端，参考buyList
    buyList = []
    for i in range(1,20):
        buyList.append(Otc(name='search', price=5, quantity=3, op="sale"))
        buyList.append(Otc(name='search', price=4, quantity=10, op="buy"))
        buyList.append(Otc(name='search', price=3, quantity=5, op="buy"))
    sortedlist = sorted(buyList, key=lambda p: p.price)
    res = []
    for item in sortedlist:
        res.append(item.__dict__)
    return json.dumps(res)

@app.route('/buylist')
def buyList():
    buyList = []
    buyList.append(Otc(name='eths', price=5, quantity=3, op="buy"))
    buyList.append(Otc(name='eths', price=4, quantity=10, op="buy"))
    buyList.append(Otc(name='eths', price=3, quantity=5, op="buy"))
    sortedlist = sorted(buyList, key=lambda p: p.price)
    res = []
    for item in sortedlist:
        res.append(item.__dict__)
    return json.dumps(res)
    # return 1


@app.route('/confirm', methods=['POST'])
def confirm():
    _data = json.loads(request.data)
    # param1 = request.form.get('name')
    # 存到库里的逻辑补下

    # 返回成功或者失败


if __name__ == "__main__":
    app.run(debug=True)
