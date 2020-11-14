import base64
import io
import urllib

from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from matplotlib import pyplot as plt


# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the index.")


def plot(request):
    df = pd.read_csv('./api/vacancies_1.csv', parse_dates=['Время публикации'])
    df['day'] = df['Время публикации'].apply(lambda date: date.day)
    df['month'] = df['Время публикации'].apply(lambda date: date.month)
    df['year'] = df['Время публикации'].apply(lambda date: date.year)
    df = df.drop(['Время публикации'], axis=1)
    get_dict = dict(request.GET.items())
    # return HttpResponse("Hello, world. You're at the plot.")
    label = 'Вакансии'
    if get_dict.get('region'):
        df = df[df['Локация'] == get_dict['region']]
        label = " ".join([label, get_dict['region']])
    if get_dict.get('group_by'):
        df = df.groupby([get_dict['group_by']], axis=0).aggregate(['count'])
    context = {"df": df}
    # return render(request, 'df_render.html', context=context)
    plt.clf()
    plt.scatter(df.index.to_numpy(), df[('Наименование', 'count')].to_numpy(), alpha=0.5, label=label)
    plt.legend(loc='best')
    fig = plt.gcf()
    # convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return render(request, 'plot.html', {'data': uri})
    # return HttpResponse(uri)
