import requests
import time
import os
import csv
from lxml import html

headers = {'Accept': '*/*',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}


def getPage(url, headers=None, params=None):
    req = requests.get(url, params, headers=headers)
    content = html.fromstring(req.content)
    req.close()
    return content


def get_companies_vacancy_link(content):
    links = content.xpath('//div[contains(@class, "vacancies_count")]//a/@href')
    company_links = [f'https://career.habr.com{i}' for i in links]
    return company_links


def get_url_archive_vacancies(company_links):
    for link in company_links:
        content = getPage(link, headers)

        names = content.xpath('//div[contains(@class, "vacancy-card__title")]//a/text()')
        # skills = content.xpath('//div[contains(@class, "vacancy-card__skills")]//a/text()')
        id_vacancies = content.xpath('//div[contains(@class, "vacancy-card__inner")]/a/@href')
        skills = []
        for id_ in id_vacancies:
            skill = content.xpath(
                f'//a[contains(@href, "{id_}")]/following-sibling::div[1]/div[contains(@class, "vacancy-card__skills")]//a/text()')
            skills.append(skill)
        # skills = content.xpath('//a[contains(@href, "vacancies/1000063927")]/following-sibling::div[1]/div[contains(@class, "vacancy-card__skills")]//a/text()')

        times = content.xpath('//div[contains(@class, "vacancy-card__date")]//time/@datetime')
        infos = content.xpath('//div[contains(@class, "vacancy-card__meta")]')
        nodes = content.xpath('//div[contains(@class, "vacancy-card__info")]')

        salaries = []
        regions = []

        for node in nodes:
            salary = node.xpath('.//div[contains(@class, "basic-salary")]/text()')
            if salary:
                salaries.append(salary[0])
            else:
                salaries.append('NULL')

        for info in infos:
            region = node.xpath('.//a[contains(@href, "city_id")]/text()')
            if region:
                regions.append(region[0])
            else:
                regions.append('NULL')

        write_vacancies_to_csv(names, skills, salaries, times, regions)
        time.sleep(0.25)


def write_vacancies_to_csv(links, names, salaries, times, regions):
    filename = 'vacancies_active.csv'
    data = zip(links, names, salaries, times, regions)
    with open(filename, mode='a', newline='', encoding='utf-8', ) as csv_file:
        writer = csv.writer(csv_file)
        if os.stat(filename).st_size == 0:
            writer.writerow(['Наименование', 'Навыки', 'Зарплата', 'Время публикации', 'Локация'])
        for row in data:
            writer.writerow(row)


def main():
    next_url = 'https://career.habr.com/companies'
    while next_url:
        params = {'category_root_id': 258822}

        content = getPage(next_url, headers, params)
        company_links = get_companies_vacancy_link(content)
        get_url_archive_vacancies(company_links)

        next_url = content.xpath('//a[contains(@class, "next_page")]/@href')
        if next_url:
            next_url = f'https://career.habr.com{next_url[0]}'
            print(next_url)


if __name__ == '__main__':
    main()