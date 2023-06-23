# Description: This script downloads car data from QatarSale.com and saves it to gcp bigquery
import numpy as np
import pandas as pd
import pickle

from flask import Flask, request, jsonify


# Initialize the Flask application
app = Flask(__name__)

#Load the model
with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

#Define the predict route with a POST method
@app.route("/predict", methods=["POST"])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force=True)

    # Make prediction using model loaded from disk as per the data.
    prediction = model.predict([np.array(list(data.values()))])

    # Take the first value of prediction
    output = prediction.tolist()[0]
    return jsonify(output)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    

