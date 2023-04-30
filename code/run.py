# run.py
from flask import Flask, request
from flask_restful import Api, Resource
from marshmallow import Schema, ValidationError, fields


class PredictSchema(Schema):
    age = fields.Integer(missing = 23)
    gender = fields.String(required=True)
    seniority = fields.Integer(missing = 11)
    segment = fields.String(required=True)
    relationship_type = fields.String(required=True)
    income = fields.Float(missing = 30000)
    nationality = fields.String(missing= 'spanish')
    activity = fields.String(required=True)


app = Flask(__name__)
api = Api(app)


class Predict(Resource):
    def post(self):
        data = request.get_json()

        schema = PredictSchema()
        try:
            # Validate request body against schema data types
            result = schema.load(data)
        except ValidationError as err:
            # Return a error message if validation fails
            return {'error': err.messages}, 400

        return {'data': result}


api.add_resource(Predict, '/predict')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
