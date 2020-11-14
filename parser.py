import time
from datetime import datetime, timedelta

import pandas as pd
import requests


def remove_duplicates(array):
    return list({v['id']: v for v in array}.values())


def get_key_skills(vacancy_id):
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    request = requests.get(url)
    request.raise_for_status()
    data = request.json()
    if data.get('key_skills'):
        return ','.join([skill['name'] for skill in data['key_skills']])
    return None


def get_similar(vacancy_id, k):
    url = f"https://api.hh.ru/vacancies/{vacancy_id}/similar_vacancies"
    params = {"area": "113", "per_page": "100", "page": 0}
    items = []
    while True:
        request = requests.get(url, params)
        request.raise_for_status()
        data = request.json()
        items.extend(data['items'])
        page = int(params['page']) + 1
        if page >= data['pages'] or len(items) == k:
            break
        params['page'] = str(page)
    return items


def vacancies_search(keyword, visible=False):
    now = datetime.now()
    date_from = now - timedelta(days=35)
    delta = timedelta(7)
    date_to = date_from + delta
    url = "https://api.hh.ru/vacancies/"
    params = {"text": keyword, "area": "113", "per_page": "100", "page": 0, "currency": "RUR",
              "date_from": date_from.strftime('%Y-%m-%d'), "date_to": date_to.strftime('%Y-%m-%d'),
              "responses_count_enabled": True}
    items = []
    while date_to < now + delta:
        while True:
            request = requests.get(url, params)
            request.raise_for_status()
            data = request.json()
            items.extend(data['items'])
            page = int(params['page']) + 1
            if page >= data['pages']:
                break
            params['page'] = str(page)
            time.sleep(1)
        if visible:
            print('[{}-{}] {} {}'.format(date_from.strftime("%Y.%m.%d"),
                                         date_to.strftime("%Y.%m.%d"),
                                         data["pages"],
                                         len(items)))

        date_from = date_to
        date_to = date_from + delta
        params["date_from"] = date_from.strftime('%Y-%m-%d')
        params["date_to"] = date_to.strftime('%Y-%m-%d')
        time.sleep(1)
    # items = remove_duplicates(items)
    for i, item in enumerate(items):
        item['key_skills'] = get_key_skills(item['id'])
        if (i + 1) % 50 == 0 and visible:
            print(f'[{datetime.now()}] done {i + 1} queries')
    # similar = [get_similar(item['id'], 5) for item in items]
    # items.extend(similar)
    # items = remove_duplicates(items)
    return items


start = datetime.now()
items = vacancies_search('python', True)
for item in items:
    item['published_at'] = datetime.strptime(item['published_at'].split('T')[0], '%Y-%m-%d')
    item['created_at'] = datetime.strptime(item['created_at'].split('T')[0], '%Y-%m-%d')
    item['area'] = item['area']['name']
    item['counters'] = item['counters']['responses']
    if item['salary']:
        if item['salary']['from']:
            item['salary_from'] = str(item['salary']['from']) + ' ' + item['salary']['currency']
        else:
            item['salary_from'] = None
        if item['salary']['to']:
            item['salary_to'] = str(item['salary']['to']) + ' ' + item['salary']['currency']
        else:
            item['salary_to'] = None
    else:
        item['salary_to'] = None
        item['salary_from'] = None

features = ['name', 'area', 'counters', 'key_skills', 'published_at', 'created_at', 'salary_from', 'salary_to']
df = pd.DataFrame(items)
df = df[features]
df.to_csv('data.csv', index=False)
print(df.describe())
