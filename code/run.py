# run.py
import pycountry
from flask import Flask, request
from flask_restful import Api, Resource
from marshmallow import Schema, ValidationError, fields


class PredictSchema(Schema):
    age = fields.Integer(missing = 23)
    gender = fields.String(required=True)
    seniority = fields.Integer(missing = 11)
    segment = fields.String(required=True)
    relationship_type = fields.String(required=True)
    income = fields.Float(missing = 30000.0)
    nationality = fields.String(missing= 'ES')
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
            # Validate gender to mapping dict
            if result['gender'].lower() == 'male':
                result['gender'] = 'V'
            else:
                result['gender'] = 'H'
            # Validate segment to mapping dict
            if result['segment'].lower() == 'vip':
                result['segment'] = '01 - TOP'
            elif result['segment'].lower() == 'student':
                result['segment'] = '03 - UNIVERSITARIO'
            else:
                result['segment'] = '02 - PARTICULARES'
            # Validate relationship_type to mapping dict
            if result['relationship_type'].lower() == 'inactive':
                result['relationship_type'] = 'I'
            elif result['relationship_type'].lower() == 'former customer':
                result['relationship_type'] = 'P'
            elif result['relationship_type'].lower() == 'former co-owner':
                result['relationship_type'] = 'N'
            elif result['relationship_type'].lower() == 'potential':
                result['relationship_type'] = 'R'
            else:
                result['relationship_type'] = 'A'
            # Validate nationality to mapping dict using ISO 3166-1 alpha-2 standard
            if result['nationality']:
                try:
                    country = pycountry.countries.search_fuzzy(result['nationality'])[0]
                    if country:
                        result['nationality'] = country.alpha_2
                except LookupError:
                    result['nationality'] = 'ES'
            # Validate activity to mapping dict
            if result['activity'].lower() == 'inactive':
                result['activity'] = 0
            else:
                result['activity'] = 1
            

            
            
        except ValidationError as err:
            # Return a error message if validation fails
            return {'error': err.messages}, 400

        return {'data': result}


api.add_resource(Predict, '/predict')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
