from flask import Flask
from flask import request
from flask_restful import inputs, reqparse, Resource, Api
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError
from datetime import datetime as dt
from decouple import config

# If MONGODB_URL hasn't been setted in ENVIROMENT, use localhost (mongodb://localhost:27017/producers_db)
APP_URL = config('MONGODB_URL', default="mongodb://localhost:27017/producers_db")

# Configuring App
app = Flask(__name__)
app.config["MONGO_URI"] = APP_URL
mongo = PyMongo(app, config_prefix='MONGO')

# Parse only arguments below:
parser = reqparse.RequestParser()
parser.add_argument('email', required=True, help="Email cannot be blank!")
parser.add_argument('name', required=True, help="Name cannot be blank")
parser.add_argument('is_company', type=inputs.boolean)


class Producer(Resource):
    now = dt.now().isoformat()

    def post(self):
        data = parser.parse_args()
        data['ip'] = request.headers.get('X-Forwarded-For', request.remote_addr)
        data['created_at'] = self.now
        try:
            mongo.db.producers.insert(data)
            content = {"message": "A new producer has been registered!", "status_code": 200}
        except DuplicateKeyError:
            content = {"message": "Oh no! This e-mail already have registered", "dup_item": data['email'],
                       "status_code": 400}
        return content, content['status_code']


api = Api(app)
api.add_resource(Producer, "/api", endpoint="producers")

if __name__ == '__main__':
    app.run(debug=True)
