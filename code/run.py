# run.py

from flask import Flask, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class Predict(Resource):
    def post(self):
        data = request.get_json()
        parameter = data.get('parameter')  
        
        return {'hello': 'world', 'parameter': parameter}

api.add_resource(Predict, '/predict')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)