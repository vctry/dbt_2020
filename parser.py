from datetime import datetime

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
    url = "https://api.hh.ru/vacancies/"
    params = {"text": keyword, "area": "113", "per_page": "100", "page": 0, "currency": "RUR",
              "date_from": "2010-01-01", "responses_count_enabled": True}
    items = []
    while True:
        request = requests.get(url, params)
        request.raise_for_status()
        data = request.json()
        items.extend(data['items'])
        page = int(params['page']) + 1
        if page >= data['pages']:
            break
        params['page'] = str(page)
    items = remove_duplicates(items)
    for i, item in enumerate(items):
        item['key_skills'] = get_key_skills(item['id'])
        if (i + 1) % 50 == 0 and visible:
            print(f'[{datetime.now()}] done {i + 1} queries')
    # similar = [get_similar(item['id'], 5) for item in items]
    # items.extend(similar)
    # items = remove_duplicates(items)
    return items


start = datetime.now()
items = vacancies_search('python')
for item in items:
    date = datetime.strptime(item['published_at'].split('T')[0], '%Y-%m-%d')
    item['published_at_year'], item['published_at_month'], item['published_at_day'] = date.year, date.month, date.day
    date = datetime.strptime(item['created_at'].split('T')[0], '%Y-%m-%d')
    item['created_at_year'], item['created_at_month'], item['created_at_day'] = date.year, date.month, date.day
    item['area'] = item['area']['name']
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

features = ['name', 'area', 'key_skills', 'published_at_day', 'published_at_month', 'published_at_year',
            'created_at_day', 'created_at_month', 'created_at_year', 'salary_from', 'salary_to']
df = pd.DataFrame(items)
df = df[features]
df.to_csv('data.csv', index=False)
print(df.describe())
