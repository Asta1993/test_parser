from urllib.request import urlopen, Request
import json
import requests
from bs4 import BeautifulSoup


URL = 'https://monomax.by/map'
URL_API_RESTAURANTS = 'https://www.kfc.ru/api/restaurants/'
URL_LOCALIZATOR = 'https://www.ziko.pl/api/lokalizator/'


def parse_site(url):
    res = urlopen(url).read()
    soup = BeautifulSoup(res, "html.parser")

    result = []
    for shop_data in soup.find_all('div', 'all-shops'):
        for data in shop_data.find_all('div', 'shop'):
            shop_address = data.find('p', 'name').string
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            shop_phone = data.find('p', 'phone')
            data_shop = {
                "address": shop_address,
                "latlon": [latitude, longitude],
                "name": 'Monomax',
                "phones": [shop_phone],
            }
            result.append(data_shop)

    return result


def get_restaurants_id(url_api_restaurants):
    res = requests.get(url_api_restaurants)
    data_restaurants = res.json()

    restaurants_id = []
    for data_restaurant in data_restaurants:
        restaurant_id = data_restaurant['restaurantId']
        restaurants_id.append(restaurant_id)

    return restaurants_id


def get_pharmacies_id(url_api_pharmacies):
    res = requests.get(url_api_pharmacies)
    data_pharmacies = res.json()

    pharmacies_id = []
    for data_pharmacy in data_pharmacies:
        pharmacy_id = data_pharmacy['pharmacyId']
        pharmacies_id.append(pharmacy_id)

    return pharmacies_id


days_of_week_data = [{'json_key': 'workdays', 'ru_abbreviation': 'пн-пт'},
                     {'json_key': 'saturday', 'ru_abbreviation': 'сб'},
                     {'json_key': 'sunday', 'ru_abbreviation': 'вс'},
                     {'json_key': 'weekends', 'ru_abbreviation': 'сб-вс'},
                     ]


def get_working_hours(kfc_data, working_item):
    working_data = get_working_data(kfc_data, working_item['json_key'])
    abreviation = working_item['ru_abbreviation']
    if working_data['isDayOff']:
        return f'{abreviation}: выходной'
    if working_data['TemporarilyClosed']:
        return f'{abreviation}: закрыто'
    start_work = working_data['startStr']
    end_work = working_data['endStr']
    return f'{abreviation}: {start_work}-{end_work}'


def get_working_hours_ziko(ziko_data, working_item):
    working_data = get_working_data(ziko_data, working_item['json_key'])
    abreviation = working_item['ru_abbreviation']
    if working_data['isDayOff']:
        return f'{abreviation}: выходной'
    start_work = working_data['startStr']
    end_work = working_data['endStr']
    return f'{abreviation}: {start_work}-{end_work}'


def get_working_data(kfc_data, day_of_week_key):
    return kfc_data['hoursOfOperation'][day_of_week_key]


def get_working_data_ziko(ziko_data, day_of_week_key):
    return ziko_data['hoursOfOperation'][day_of_week_key]


def get_data_kfc(restaurants_id):
    result_data = []
    for restaurant_id in restaurants_id:
        url_api_kfc = f'https://www.kfc.ru/api/restaurants/list/?restaurantId={restaurant_id}'
        res = requests.get(url_api_kfc)
        data = res.json()
        for kfc_data in data:
            address = kfc_data['address']
            latlon = [kfc_data['latitude'], kfc_data['longitude']]
            kfc_name = kfc_data['name']
            first_phone = kfc_data['phones'][0]['phone']
            phones = [first_phone]
            if len(kfc_data['phones']) == 2:
                second_phone = kfc_data['phones'][1]['phone']
                phones.append(second_phone)

            working_hours = []
            for days_of_week_item in days_of_week_data:
                working_hours.append(get_working_hours(kfc_data, days_of_week_item))

            data_kfc = {
                "address": address,
                "latlon": latlon,
                "name": kfc_name,
                "phones": phones,
                "working_hours": working_hours
            }
            result_data.append(data_kfc)

    return result_data


def get_data_ziko(pharmacies_id):
    result_data = []
    for pharmacy_id in pharmacies_id:
        url_api_ziko = f'https://www.ziko.pl/api/lokalizator/list/?pharmacyId={pharmacy_id}'
        res = requests.get(url_api_ziko)
        data = res.json()
        for ziko_data in data:
            address = ziko_data['address']
            latlon = [ziko_data['latitude'], ziko_data['longitude']]
            ziko_name = ziko_data['name']
            first_phone = ziko_data['phones'][0]['phone']
            phones = [first_phone]
            if len(ziko_data['phones']) == 2:
                second_phone = ziko_data['phones'][1]['phone']
                phones.append(second_phone)

            working_hours = []
            for days_of_week_item in days_of_week_data:
                working_hours.append(get_working_hours(ziko_data, days_of_week_item))

            data_ziko = {
                "address": address,
                "latlon": latlon,
                "name": ziko_name,
                "phones": phones,
                "working_hours": working_hours
            }
            result_data.append(data_ziko)

    return result_data


def write_json(filename, data):
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


def output_json(filename):
    with open(filename) as f:
        data = json.load (f)
    print(f'***{filename}', data)


# -------------site1(MONOMAX)---

data_parser = parse_site(URL)
write_json('site1.json', data_parser)
# output_json('site1.json')

# ------------site2(KFC)---

restaurants_id = get_restaurants_id(URL_API_RESTAURANTS)
data_kfc = get_data_kfc(restaurants_id)
write_json('site2.json', data_kfc)
# output_json('site2.json')


# ------------site3(ZIKO)----

pharmacies_id = get_pharmacies_id(URL_LOCALIZATOR)
data_ziko = get_data_ziko(pharmacies_id)
write_json('site2.json', data_ziko)
# output_json('site2.json')
