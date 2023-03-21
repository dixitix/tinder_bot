import requests
from bs4 import BeautifulSoup
from json import loads


def parsing(data):
    resp = requests.post('https://geocult.ru/swetest/app/form/fetch/fetch_data.php', data={'city_id' : data[5]})
    page = resp.content.decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')
    city_data = loads(soup.prettify())
    url = f'https://geocult.ru/natalnaya-karta-onlayn-raschet?fd={data[0]}&fm={data[1]}&fy={data[2]}&fh={data[3]}fmn={data[4]}&tm={city_data["gmt"]}&lt={city_data["latitude"]}&ln={city_data["longitude"]}&hs=P&sb=1'
    resp = requests.get(url)
    page = resp.content.decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')
    info = []
    for elem1 in soup.find_all(class_='hamburg_v2')[:10]:
        new_obj = []
        for elem2 in elem1.parent.parent:
            new_obj += elem2.text.strip().split() 
        space_obj = new_obj[3]
        space_cords = new_obj[4]
        info += [space_obj, int(space_cords[:2]), int(space_cords[3:5])]
    return info
