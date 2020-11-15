# from pyramid.arima import auto_arima   # pyramid-arima
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import os

def predict_arima(dt):

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

def read_data(path='/content/gdrive/My Drive/Colab Notebooks/sber-hack/result_data.csv'):
    data = pd.read_csv(path)

    return data


def arima_vacancies(data, vacancy, region=None):
    test_data = data[['created_at', 'vacancy']][(data['vacancy'] == vacancy) & (data['area'] == region)]

    test_data['created_at'] = pd.to_datetime(test_data.created_at).apply(lambda date: date.strftime('%Y-%m'))
    test_data['created_year'] = pd.to_datetime(test_data.created_at).apply(lambda date: date.strftime('%Y'))
    test_data['created_month'] = pd.to_datetime(test_data.created_at).apply(lambda date: date.strftime('%m'))
    test_data.head()

    dt = test_data['vacancy'].groupby(test_data['created_at']).agg(['count'])

    dt.index = pd.to_datetime(dt.index)

    test, future_forecast = predict_arima(dt)
    return test, future_forecast


def arima_skills(data, vacancy, region=None):
    test_data = data[['created_at', 'key_skills']][data['key_skills'] == 'JavaScript']
    test_data['created_at'] = pd.to_datetime(test_data.created_at).apply(lambda date: date.strftime('%Y-%m'))
    dt = test_data['key_skills'].groupby(test_data['created_at']).agg(['count'])
    dt.index = pd.to_datetime(dt.index)

    test, future_forecast = predict_arima(dt)
    return test, future_forecast


def main():
    data = read_data()
    test, future_forecast = arima_skills(data, 'Разработчик', region=None)








