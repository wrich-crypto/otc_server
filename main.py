import sys
print(sys.executable)
print(sys.path)
from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
import datetime
import hashlib


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://otc_db:otc_db123@127.0.0.1:3306/otc_db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    phone = db.Column(db.String(128))
    wechat = db.Column(db.String(128))
    password = db.Column(db.String(128))
    token = db.Column(db.String(256))
    create_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(256))
    amount = db.Column(db.Float)
    money = db.Column(db.Float)
    unit = db.Column(db.String(128), default="USDT")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_time = db.Column(db.DateTime)
    transaction_type = db.Column(db.Integer, default=1)
    status = db.Column(db.Integer, default=1)

def create_tables():
    db.create_all()

@app.before_request
def before_request():
    token = request.headers.get('Authorization')
    if not token:
        return {"error": "No token provided"}, 401
    user = User.query.filter_by(token=token).first()
    if not user:
        return {"error": "Invalid token"}, 401
    g.user = user

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(name=data['account'], password=data['password']).first()
    if not user:
        return {"error": "Invalid account or password"}, 401
    return {"token": user.token}

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    token = hashlib.sha256((data['account'] + data['password']).encode()).hexdigest()
    user = User(name=data['account'], password=data['password'], phone=data['phone'], wechat=data['wechat'], token=token)
    db.session.add(user)
    db.session.commit()
    return {"id": user.id, "token": user.token}, 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return {"error": "User not found"}, 404
    return {
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "wechat": user.wechat,
        "create_time": user.create_time,
    }

@app.route('/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()
    transaction = Transaction(
        content=data['content'],
        amount=data['amount'],
        money=data['money'],
        unit=data.get('unit', 'USDT'),
        user_id=g.user.id,
        contact=data['contact'],
        end_time=data['end_time'],
        transaction_type=data.get('transaction_type', 1),
        status=data.get('status', 1),
    )
    db.session.add(transaction)
    db.session.commit()
    return {"id": transaction.id}, 201

@app.route('/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if transaction is None:
        return {"error": "Transaction not found"}, 404
    return {
        "id": transaction.id,
        "content": transaction.content,
        "amount": transaction.amount,
        "money": transaction.money,
        "unit": transaction.unit,
        "user_id": transaction.user_id,
        "contact": transaction.contact,
        "created_at": transaction.created_at,
        "end_time": transaction.end_time,
        "transaction_type": transaction.transaction_type,
        "status": transaction.status,
    }

if __name__ == "__main__":
    with app.app_context():
        create_tables()
    app.run(debug=True)
