from pyramid.arima import auto_arima   # pyramid-arima
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import os


def read_data(path='/content/gdrive/My Drive/Colab Notebooks/sber-hack/result_data.csv'):
    data = pd.read_csv(path)

    return data


def prepare_data(data, vacancy, region=None):
    test_data = data[['created_at', 'vacancy']][(data['vacancy'] == vacancy) & (data['area'] == region)]

    test_data['created_at'] = pd.to_datetime(test_data.created_at).apply(lambda date: date.strftime('%Y-%m'))
    test_data.head()

    dt = test_data['vacancy'].groupby(test_data['created_at']).agg(['count'])
    dt.head()

    dt.index = pd.to_datetime(dt.index)

    return dt


def predict_arima(data, vacancy, region=None):
    dt = prepare_data(data, vacancy, region=None)

    stepwise_model = auto_arima(dt, start_p=1, start_q=1,
                                max_p=3, max_q=3, m=12,
                                start_P=0, seasonal=True,
                                d=1, D=1, trace=True,
                                error_action='ignore',
                                suppress_warnings=True,
                                stepwise=True)

    train = dt[0: int(0.8 * len(dt))]
    test = dt[int(0.8 * len(dt)):]

    stepwise_model.fit(train)
    future_forecast = stepwise_model.predict(n_periods=len(test))
    future_forecast = pd.DataFrame(future_forecast, index=test.index, columns=['Prediction'])

    return test, future_forecast







