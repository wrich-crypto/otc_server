import json
from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
import logging
# Set up logging
log_directory = "log"
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_directory, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Load configurations from config.json
with open('config.json') as config_file:
    config_data = json.load(config_file)

app = Flask(__name__)
app.config.update(config_data["flask"])  # Assuming you have a 'flask' key in your config.json

CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    contact = db.Column(db.String(128), nullable=True) # New field for contact
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # New field for created_at
    role = db.Column(db.Integer, default=1) # New field for role (1 for user, 2 for admin, 3 for blacklisted)
    status = db.Column(db.Integer, default=1) # New field for status (1 for active, 2 for deleted)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # New field for created_at
    status = db.Column(db.Integer, default=1) # New field for status (1 for active, 2 for deleted)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'count': self.count,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'status': self.status
        }

@app.route('/login', methods=['POST'])
def login():
    _data = json.loads(request.data)
    _address = _data['address']
    logging.info(f'Received login request for address: {_address}')  # Log the received request

    try:
        user = User.query.filter_by(address=_address).first()
        if user:
            logging.info(f'User found for address: {_address}')  # Log when a user is found
            return json.dumps({'name': user.name}), 200
        else:
            logging.error(f'User not found for address: {_address}')  # Log when a user is not found
            return json.dumps({'error': 'User not found'}), 404
    except Exception as e:
        logging.error(f'Exception occurred during login: {str(e)}')  # Log when an exception occurs
        return json.dumps({'error': str(e)}), 500


@app.route('/initOptions', methods=['POST'])
def initOption():
    logging.info('Received request for initial options')
    option_list = [{"name":"eths"},{"name":"terc-20"}]
    return json.dumps(option_list), 200

@app.route('/add', methods=['POST'])
def add():
    _data = json.loads(request.data)
    if not all(key in _data for key in ('name', 'type', 'count', 'user_id')):
        logging.error('Invalid request received for add transaction')
        return json.dumps({'error': 'Invalid request'}), 400
    _name, _type, _count, _user_id = _data['name'], _data['type'], _data['count'], _data['user_id']
    logging.info(f'Received request to add transaction for user_id: {_user_id}, name: {_name}, type: {_type}, count: {_count}')

    try:
        new_transaction = Transaction(name=_name, type=_type, count=_count, user_id=_user_id)
        db.session.add(new_transaction)
        db.session.commit()
        return json.dumps({'message': 'Transaction added successfully'}), 201
    except Exception as e:
        logging.error(f'Exception occurred during add transaction: {str(e)}')
        return json.dumps({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    _data = json.loads(request.data)
    if not all(key in _data for key in ('name', 'type')):
        logging.error('Invalid request received for search')
        return json.dumps({'error': 'Invalid request'}), 400
    _s_name, _s_type = _data['name'], _data['type']
    logging.info(f'Received request to search transactions for name: {_s_name}, type: {_s_type}')

    try:
        transactions = Transaction.query.filter_by(name=_s_name, type=_s_type).all()
        transaction_list = [transaction.to_dict() for transaction in transactions]
        return json.dumps(transaction_list), 200
    except Exception as e:
        logging.error(f'Exception occurred during search: {str(e)}')
        return json.dumps({'error': str(e)}), 500

@app.route('/buylist', methods=['GET'])
def buyList():
    logging.info('Received request for buy list')

    try:
        transactions = Transaction.query.filter_by(type='buy').all()
        transaction_list = [transaction.to_dict() for transaction in transactions]
        return json.dumps(transaction_list), 200
    except Exception as e:
        logging.error(f'Exception occurred during buy list: {str(e)}')
        return json.dumps({'error': str(e)}), 500

@app.route('/confirm', methods=['POST'])
def confirm():
    _data = json.loads(request.data)
    if 'transaction_id' not in _data:
        logging.error('Invalid request received for confirm')
        return json.dumps({'error': 'Invalid request'}), 400
    _transaction_id = _data['transaction_id']
    logging.info(f'Received request to confirm transaction id: {_transaction_id}')

    try:
        transaction = Transaction.query.get(_transaction_id)
        if transaction:
            # Add logic to handle the confirmation process
            return json.dumps({'message': 'Transaction confirmed'}), 200
        else:
            logging.error(f'Transaction not found for id: {_transaction_id}')
            return json.dumps({'error': 'Transaction not found'}), 404
    except Exception as e:
        logging.error(f'Exception occurred during confirm: {str(e)}')
        return json.dumps({'error': str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=app.config["DEBUG"])
