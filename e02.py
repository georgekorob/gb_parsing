# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к
# нему, пройдя авторизацию. Ответ сервера записать в файл.
import requests
import json
import webbrowser
import os

my_params = {
    'api_key': '22n0RcLRSNLV8tm3fb3XYXqKaQ70GyOdJYaQhWE9',
    'sol': 1000
}
url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'

response = requests.get(url, params=my_params)
if response.ok:
    j_data = response.json()
    print(j_data)
    with open('e02.json', 'w') as f:
        json.dump(j_data, f)  # Сохранить ответ от сервера
    img_src = j_data['photos'][0]['img_src']  # Ссылка на фото
    print(img_src)
    webbrowser.open(img_src, new=2)  # Открыть в браузере
    name_photo = img_src.split('/')[-1]
    req_photo = requests.get(img_src)
    with open(os.getcwd() + '/' + name_photo, 'wb') as f:
        f.write(req_photo.content)  # Сохранить фото в файле
