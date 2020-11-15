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


def plot_change(request):
    df = pd.read_csv('./api/result_data.csv', parse_dates=['created_at'])
    df['created_at'] = df['created_at'].apply(lambda date: date.strftime('%Y-%m'))
    get_dict = dict(request.GET.items())
    label = 'Вакансии'
    if get_dict.get('region') and not get_dict.get('space') and get_dict.get('region') != 'all':
        df = df[df['area'] == get_dict['region']]
        label = " ".join([label, get_dict['region']])

    if get_dict.get('year') and get_dict.get('year') != 'all':
        df = df[df['created_at'].str.contains(get_dict['year'])]
        label = " ".join([label, get_dict['year']])

    if get_dict.get('space') and not get_dict.get('region'):
        df_reg = df.groupby(['area'], axis=0).aggregate('count').sort_values(by=['vacancy'], ascending=False)
        regions = df_reg.index.unique()
        plt.figure(figsize=(20, 10))

        for i, region in enumerate(regions[:10]):
            df_reg = df[df['area'] == str(region)]
            df_reg = df_reg.groupby(['created_at'], axis=0).aggregate('count')
            label_reg = " ".join([label, str(region)])
            plt.bar(df_reg.index.to_numpy(), df_reg['vacancy'].to_numpy(), alpha=0.7, label=label_reg,)
        plt.xticks(rotation=70)
        plt.legend(loc='upper right')
    else:
        df = df.groupby(['created_at'], axis=0).aggregate('count')
        plt.figure(figsize=(20, 10))
        plt.xticks(rotation=70)
        plt.bar(df.index.to_numpy(), df['vacancy'].to_numpy(), alpha=0.7, label=label)
        plt.legend(loc='best')

    fig = plt.gcf()
    # convert graph into string buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.clf()

    # return render(request, 'plot_render.html', {'data': uri})
    return HttpResponse(uri)


def plot(request):
    df = pd.read_csv('./api/result_data.csv', parse_dates=['created_at'])
    regions = df['area'].dropna().sort_values().unique()
    years = sorted(map(int, set(list(pd.DatetimeIndex(df['created_at']).year))))

    return render(request, 'plot.html', {'regions': regions, "years": years})
