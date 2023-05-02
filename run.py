# run.py
import pickle

import numpy as np
import pandas as pd
import pycountry
import xgboost as xgb
from flask import Flask, request
from flask_redoc import Redoc
from flask_restful import Api, Resource
from marshmallow import Schema, ValidationError, fields

from source_code import processData

# Mapping dictionaries
gender_mapping = {'male': 'V', 'female': 'H'}
segment_mapping = {'vip': '01 - TOP', 'student': '03 - UNIVERSITARIO'}
relationship_mapping = {
    'inactive': 'I', 'former customer': 'P', 'former co-owner': 'N', 'potential': 'R'}
activity_mapping = {'inactive': 0, 'active': 1}


# load trained model
trained_model = open("trained_model.pkl", 'rb')
model = pickle.load(trained_model)

# init app
app = Flask(__name__)
api = Api(app)

# redoc
redoc = Redoc(app, 'PredictApi.yml')


class PredictSchema(Schema):
    age = fields.Integer(missing=23)  # age
    gender = fields.String(required=True)  # sexo
    seniority = fields.Integer(missing=11)  # antiguedad
    segment = fields.String(required=True)  # segmento
    relationship_type = fields.String(required=True)  # tiprel_1mes
    income = fields.Float(missing=30000.0)  # renta
    nationality = fields.String(load_default='ES')  # pais_residencia
    activity = fields.String(required=True)  # ind_actividad_cliente


class Predict(Resource):
    def post(self):

        data = request.get_json()

        schema = PredictSchema()

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
            # Return an error message if validation fails
            error_message = {'error': 'Validation Error',
                             'details': err.messages}
            return error_message, 400

        # Creating predict_request attributes based on test_ver2 dataset
        predict_request = pd.DataFrame([{
            'fecha_dato': "2016-06-28",
            'ncodpers': 15889,
            'ind_empleado': 'F',
            'pais_residencia': result['nationality'],
            'sexo': result['gender'],
            'age': result['age'],
            'fecha_alta': "1995-01-16",
            'ind_nuevo': '0',
            'antiguedad': result['seniority'],
            'indrel': '1',
            'ult_fec_cli_1t': "",
            'indrel_1mes': '1',
            'tiprel_1mes': result['relationship_type'],
            'indresi': "S",
            'indext': "N",
            'conyuemp': "N",
            'canal_entrada': "KAT",
            'indfall': "N",
            'tipodom': 1,
            'cod_prov': 28,
            'nomprov': 'MADRID',
            'ind_actividad_cliente': result['activity'],
            'renta': result['income'],
            'segmento': result['segment']
        }])
        # saving predict request to csv
        predict_request.to_csv('predict_request.csv', index=False)
        # importing predict file to make predictions
        with open("predict_request.csv") as predict_file:
            x_vars_list, y_vars_list, cust_dict = processData(predict_file, {})
        request_array = np.array(x_vars_list)
        # predicting
        request_dmatrix = xgb.DMatrix(request_array)
        predictions = model.predict(request_dmatrix)
        # Getting the top product
        target_cols = ['ind_ahor_fin_ult1', 'ind_aval_fin_ult1', 'ind_cco_fin_ult1', 'ind_cder_fin_ult1', 'ind_cno_fin_ult1', 'ind_ctju_fin_ult1', 'ind_ctma_fin_ult1', 'ind_ctop_fin_ult1', 'ind_ctpp_fin_ult1', 'ind_deco_fin_ult1', 'ind_deme_fin_ult1', 'ind_dela_fin_ult1',
                       'ind_ecue_fin_ult1', 'ind_fond_fin_ult1', 'ind_hip_fin_ult1', 'ind_plan_fin_ult1', 'ind_pres_fin_ult1', 'ind_reca_fin_ult1', 'ind_tjcr_fin_ult1', 'ind_valo_fin_ult1', 'ind_viv_fin_ult1', 'ind_nomina_ult1', 'ind_nom_pens_ult1', 'ind_recibo_ult1']
        target_cols = target_cols[2:]
        target_cols = np.array(target_cols)
        predictions = np.argsort(predictions, axis=1)
        predictions = np.fliplr(predictions)[:, :7]
        final_preds = [" ".join(list(target_cols[pred]))
                       for pred in predictions]
        return {'Recommendations': final_preds}


api.add_resource(Predict, '/predict')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
