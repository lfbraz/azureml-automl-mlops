# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import pickle
import numpy as np
import pandas as pd
import azureml.train.automl
from sklearn.externals import joblib
from azureml.core.model import Model

from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType
from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType


input_sample = pd.DataFrame({"AGE": pd.Series(["59.0"], dtype="float64"), "SEX": pd.Series(["2.0"], dtype="float64"), "BMI": pd.Series(["32.1"], dtype="float64"), "BP": pd.Series(["101.0"], dtype="float64"), "S1": pd.Series(["157.0"], dtype="float64"), "S2": pd.Series(["93.2"], dtype="float64"), "S3": pd.Series(["38.0"], dtype="float64"), "S4": pd.Series(["4.0"], dtype="float64"), "S5": pd.Series(["4.8598"], dtype="float64"), "S6": pd.Series(["87.0"], dtype="float64")})
output_sample = np.array([0])


def init():
    global model
    # This name is model.id of model that we want to deploy deserialize the model file back
    # into a sklearn model
    model_path = Model.get_model_path(model_name = 'diabetes')
    model = joblib.load(model_path)


@input_schema('data', PandasParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def run(data):
    try:
        result = model.predict(data)
        return json.dumps({"result": result.tolist()})
    except Exception as e:
        result = str(e)
        return json.dumps({"error": result})
