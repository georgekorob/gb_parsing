# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию. Добавить в решение со
# сбором вакансий(продуктов) функцию, которая будет добавлять только новые вакансии/продукты в вашу базу.
import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import pymongo
import hashlib

url = 'https://hh.ru/search/vacancy'
params = {'area': 1,
          'text': 'python',  # input('Введите должность: '),
          'fromSearchLine': 'true',
          'st': 'searchVacancy',
          'page': 0}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/93.0.4577.82 Safari/537.36'}

count = 40  # int(input('Введите количество страниц для анализа: '))
client = pymongo.MongoClient('localhost', 27017)
db = client['hh_database']
vacancies = db.vacancies
while True:
    response = requests.get(url, params=params, headers=headers)
    response_text = response.text
    soup = bs(response_text, 'html.parser')
    vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
    if vacancy_list and response.ok:
        for vacancy in vacancy_list:
            # Необходимые элементы по классу
            vac_name = vacancy.find('a', attrs={'class': 'bloko-link'})
            vac_comp = vacancy.find('a', attrs={'class': 'bloko-link bloko-link_secondary'})
            vac_place = vacancy.find('span', attrs={'class': 'vacancy-serp-item__meta-info'})
            vac_link = vacancy.find('a', attrs={'class': 'bloko-link'})
            # Обработка значений None
            vacancy_data = {'name': vac_name.text if vac_name else None,
                            'company': ' '.join(vac_comp.text.split('\xa0')) if vac_comp else None,
                            'link': vac_link['href'] if vac_link else None,
                            'city': None, 'place': None, 'currency': None,
                            'min_value': None, 'max_value': None, '_id': None}
            # Если есть город
            if vac_place:
                places = vac_place.text.split(', ')
                vacancy_data['city'] = places[0]
                # Если есть метро
                if len(places) > 1:
                    vacancy_data['place'] = places[1]
            # Значения зарплат
            vacancy_values = vacancy.find('div', attrs={'class': 'vacancy-serp-item__sidebar'})
            if vacancy_values and not vacancy_values.text == '':
                vacancy_values = vacancy_values.text
                values = vacancy_values.split(' ')
                # Валюта
                vacancy_data['currency'] = values.pop()
                if values[0] == 'до':
                    vacancy_data['max_value'] = int(''.join(values[1].split('\u202f')))
                elif values[0] == 'от':
                    vacancy_data['min_value'] = int(''.join(values[1].split('\u202f')))
                elif '–' in values:
                    vacancy_data['min_value'] = int(''.join(values[0].split('\u202f')))
                    vacancy_data['max_value'] = int(''.join(values[2].split('\u202f')))
                else:
                    print('Error!')
            vacancy_data['_id'] = hashlib.sha1(str(vacancy_data).encode()).hexdigest()
            try:
                vacancies.insert_one(vacancy_data)
            except pymongo.errors.DuplicateKeyError:
                print('Такая вакансия уже существует!')
            # vacancies.append(vacancy_data)
    else:
        break
    if params['page'] >= count:
        break
    params['page'] += 1

for vacancy in vacancies.find({}, {'_id': False}):
    pprint(vacancy)
