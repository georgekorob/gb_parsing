# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.
import requests
import json

USERNAME = 'georgekorob'
url = f'https://api.github.com/users/{USERNAME}/repos'

response = requests.get(url)
j_data = response.json()
print(f'Тип объекта json: {type(j_data)}')
# <class 'list'> получаем тип лист

# Формируем список данных об именах репозиториев
names = [item['name'] for item in j_data]
print(f'Список репозиториев пользователя {USERNAME}: {names}')

with open('e01.json', 'w') as f:
    json.dump(names, f)
