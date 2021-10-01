# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты). Для тех, кто выполнил задание с Росконтролем - напишите запрос для
# поиска продуктов с рейтингом не ниже введенного или качеством не ниже введенного (то есть цифра вводится одна,
# а запрос проверяет оба поля)
import requests
from bs4 import BeautifulSoup as bs
import pymongo
from pprint import pprint

url = 'http://www.cbr.ru/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/93.0.4577.82 Safari/537.36'}

response = requests.get(url, headers=headers)
response_text = response.text
soup = bs(response_text, 'html.parser')
cur_usd = soup.find('div', attrs={'class': 'col-md-2 col-xs-9 _dollar'})
cur_usd = float(cur_usd.parent.contents[3].text.split()[0].replace(',', '.'))
# print(cur_usd)
cur_eur = soup.find('div', attrs={'class': 'col-md-2 col-xs-9 _euro'})
cur_eur = float(cur_eur.parent.contents[3].text.split()[0].replace(',', '.'))
# print(cur_eur)

client = pymongo.MongoClient('localhost', 27017)
db = client['hh_database']
vacancies = db.vacancies
min_value_rub = int(input('Введите минимальное значение зарплаты в рублях:'))  #200000  #
for vacancy in vacancies.find(
        {'$or':
            [
                {'currency': 'руб.',
                 '$and':
                     [
                         {'$or':
                             [
                                 {'min_value': {'$gt': min_value_rub}},
                                 {'min_value': None}
                             ]
                         },
                         {'$or':
                             [
                                 {'max_value': {'$gt': min_value_rub}},
                                 {'max_value': None}
                             ]
                         }
                     ]
                 },
                {'currency': 'USD',
                 '$and':
                     [
                         {'$or':
                             [
                                 {'min_value': {'$gt': min_value_rub / cur_usd}},
                                 {'min_value': None}
                             ]
                         },
                         {'$or':
                             [
                                 {'max_value': {'$gt': min_value_rub / cur_usd}},
                                 {'max_value': None}
                             ]
                         }
                     ]
                 },
                {'currency': 'EUR',
                 '$and':
                     [
                         {'$or':
                             [
                                 {'min_value': {'$gt': min_value_rub / cur_eur}},
                                 {'min_value': None}
                             ]
                         },
                         {'$or':
                             [
                                 {'max_value': {'$gt': min_value_rub / cur_eur}},
                                 {'max_value': None}
                             ]
                         }
                     ]
                 }
            ]
        }, {'_id': False}):
    pprint(vacancy)
