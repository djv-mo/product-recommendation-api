# run.py
import pycountry
from flask import Flask, request
from flask_restful import Api, Resource
from marshmallow import Schema, ValidationError, fields


class PredictSchema(Schema):
    age = fields.Integer(missing=23)
    gender = fields.String(required=True)
    seniority = fields.Integer(missing=11)
    segment = fields.String(required=True)
    relationship_type = fields.String(required=True)
    income = fields.Float(missing=30000.0)
    nationality = fields.String(missing='ES')
    activity = fields.String(required=True)


app = Flask(__name__)
api = Api(app)


class Predict(Resource):
    def post(self):
        data = request.get_json()

        schema = PredictSchema()
        # Mapping dictionaries
        gender_mapping = {'male': 'V', 'female': 'H'}
        segment_mapping = {'vip': '01 - TOP', 'student': '03 - UNIVERSITARIO'}
        relationship_mapping = {
            'inactive': 'I', 'former customer': 'P', 'former co-owner': 'N', 'potential': 'R'}
        activity_mapping = {'inactive': 0, 'active': 1}
        try:
            # Validate request body against schema data types
            result = schema.load(data)
            # Validate gender to mapping dict
            result['gender'] = gender_mapping.get(
                result['gender'].lower(), 'H')

            # Validate segment to mapping dict
            result['segment'] = segment_mapping.get(
                result['segment'].lower(), '02 - PARTICULARES')

            # Validate relationship_type to mapping dict
            result['relationship_type'] = relationship_mapping.get(
                result['relationship_type'].lower(), 'A')

            # Validate nationality to mapping dict using ISO 3166-1 alpha-2 standard
            if result['nationality']:
                try:
                    country = pycountry.countries.search_fuzzy(
                        result['nationality'])[0]
                    result['nationality'] = country.alpha_2 if country else 'ES'
                except LookupError:
                    result['nationality'] = 'ES'

            # Validate activity to mapping dict
            result['activity'] = activity_mapping.get(
                result['activity'].lower(), 1 if result['activity'].lower() != 'inactive' else 0)

        except ValidationError as err:
            # Return a error message if validation fails
            return {'error': err.messages}, 400

        return {'data': result}


api.add_resource(Predict, '/predict')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
