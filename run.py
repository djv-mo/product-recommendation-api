# run.py

from flask import Flask
from flask_redoc import Redoc
from flask_restful import Api

from products.products import ProductsPredict

# from model2.foods import FoodPredict

# init app
app = Flask(__name__)
api = Api(app)

# redoc
redoc = Redoc(app, 'PredictApi.yml')


api.add_resource(ProductsPredict, '/products/predict')
# api.add_resource(FoodPredict, '/foods/predict')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
