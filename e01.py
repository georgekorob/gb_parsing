# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем
# должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц
# сайта (также вводим через input или аргументы).
#
# Получившийся список должен содержать в себе минимум:
# 1. Наименование вакансии.
# 2. Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# 3. Ссылку на саму вакансию.
# 4. Сайт, откуда собрана вакансия.
#
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
# одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
# Сохраните в json либо csv.

import requests
from bs4 import BeautifulSoup as bs
from pandas import DataFrame
import os

url = 'https://hh.ru/search/vacancy'
params = {'area': 1,
          'text': input('Введите должность: '),  # 'python',
          'fromSearchLine': 'true',
          'st': 'searchVacancy',
          'page': 0}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}

count = int(input('Введите количество страниц для анализа: '))
vacancies = []
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
                            'link': vac_link['href'] if vac_link else None}
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
            vacancies.append(vacancy_data)
    else:
        break
    if params['page'] >= count:
        break
    params['page'] += 1

dataframe = DataFrame(vacancies)
print(dataframe)
dataframe.to_csv(os.getcwd() + '/data_vacancy.csv', sep=';', encoding='ansi')
