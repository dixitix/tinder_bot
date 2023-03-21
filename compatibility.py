import requests
from bs4 import BeautifulSoup
from json import loads


def get_compatibility(person1, person2):

  resp = requests.post(
    'https://geocult.ru/swetest/app/form/fetch/fetch_data.php',
    data={'city_id': person1[5]})
  page = resp.content.decode("utf-8")
  soup = BeautifulSoup(page, 'html.parser')
  city1_data = loads(soup.prettify())

  resp = requests.post(
    'https://geocult.ru/swetest/app/form/fetch/fetch_data.php',
    data={'city_id': person2[5]})
  page = resp.content.decode("utf-8")
  soup = BeautifulSoup(page, 'html.parser')
  city2_data = loads(soup.prettify())

  url = f'https://geocult.ru/synastry-online?fd={person1[0]}&fm={person1[1]}&fy={person1[2]}&fh={person1[3]}&fmn={person1[4]}&tm={city1_data["gmt"]}&lt={city1_data["latitude"]}&ln={city1_data["longitude"]}&fd2={person2[0]}&fm2={person2[1]}&fy2={person2[2]}&fh2={person2[3]}&fmn2={person2[4]}&tz2={city2_data["timezone"].replace("/", "%2F")}&tm2={city2_data["gmt"]}&ttz2=x2&ltp2={city2_data["latitude"]}&lnp2={city2_data["longitude"]}&hs=P&sb=1'
  resp = requests.get(url)
  page = resp.content.decode("utf-8")
  soup = BeautifulSoup(page, 'html.parser')
  return requests.get(soup.find('img', border='0').get('src')).url
