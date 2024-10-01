import json
import requests
import pandas as pd

def get_catalogs_wb():
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json'
    # headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    data_list = []

    for d in data:
        try:
            for child in d['childs']:
                try:
                    category_name = child['name']
                    category_url = child['url']
                    shard = child['shard']
                    query = child['query']
                    data_list.append({
                        'category_name': category_name,
                        'category_url': category_url,
                        'shard': shard,
                        'query': query})
                except:
                    continue
                try:
                    for sub_child in child['childs']:
                        category_name = sub_child['name']
                        category_url = sub_child['url']
                        shard = sub_child['shard']
                        query = sub_child['query']
                        data_list.append({
                            'category_name': category_name,
                            'category_url': category_url,
                            'shard': shard,
                            'query': query})
                except:
                    continue
        except:
            continue
    return data_list

def search_category_in_catalog(url, catalog_list):
    try:
        for catalog in catalog_list:
            if catalog['category_url'] == url.split('https://www.wildberries.ru')[-1]:
                print(f'найдено совпадение: {catalog["category_name"]}')
                name_category = catalog['category_name']
                shard = catalog['shard']
                query = catalog['query']
                return name_category, shard, query
            else:
                # print('нет совпадения')
                pass
    except:
        print('Данный раздел не найден!')

def get_data_from_json(json_file):
    data_list = []

    for data in json_file['data']['products']:
        try:
            element = data['sizes'][0]
            price = int(element['price']['basic'] / 100)
        except:
            price = 0
        data_list.append({
            'Наименование': data['name'],
            'id': data['id'],
            'Цена': price,
            'Цена со скидкой': int(element['price']['total'] / 100),
            'Бренд': data['brand'],
            'id бренда': int(data['brandId']),
            'feedbacks': data['feedbacks'],
            'rating': data['rating'],
            'Ссылка': f'https://www.wildberries.ru/catalog/{data["id"]}/detail.aspx?targetUrl=BP'
        })
    return data_list

def get_content(shard, query, low_price=None, top_price=None):
    # headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}"}

    data_list = []

    for page in range(1, 11):
        print(f'Сбор позиций со страницы {page} из 11')
        url = f'https://catalog.wb.ru/catalog/{shard}/v2/catalog?ab_testing=false&appType=1&{query}' \
              f'&curr=rub&dest=-455203&page={page}&priceU={low_price * 100};{top_price * 100}&' \
              f'sort=popular&spp=30&uclusters=5&uiv=6&uv=JTCwBqs7JiMvsyUwrTQqNjNHq9UoYi2sKMIrFK_XKUettali' \
              f'Mpmt1arOm7eml6BkLsStJqSGKRow-a0greIsUK5CrNooPyRWJCysXSGdKpUw3SgjLFGkHTDZovEqAq2wMgQxnjCmr-6qBLCGK5anubD' \
              f'_sdSvLqzMmjysnTFZqvouL5-qqPcp-jEDojWvhazMp_8t86ikoaitGyz-rJ8wf7AMsbit_LFhJG2lBKg6KTWxly6GKzsqXqtWoHMrKKTv' \
              f'LFYnUCryLYMtVieVL6OspighKROxShM4ql4tWS4yqYiuV6L4m4cqQ6lWLC6oBq47p1svfCajLpsu7KUwpamteg'

        r = requests.get(url, headers=headers)
        data = r.json()
        print(f'Добавлено позиций: {len(get_data_from_json(data))}')

        if len(get_data_from_json(data)) > 0:
            data_list.extend(get_data_from_json(data))
        else:
            print(f'Сбор данных завершен.')
            break
    return data_list

def save_excel(data, filename):
    df = pd.DataFrame(data)
    writer = pd.ExcelWriter(f'{filename}.xlsx')
    df.to_excel(writer, 'data')
    writer._save()
    print(f'Все сохранено в {filename}.xlsx')
    writer.close()

def parser(url, low_price, top_price):
    catalog_list = get_catalogs_wb()

    try:
        name_category, shard, query = search_category_in_catalog(url=url, catalog_list=catalog_list)
        data_list = get_content(shard=shard, query=query, low_price=low_price, top_price=top_price)
        save_excel(data_list, f'{name_category}_from_{low_price}_to_{top_price}')
    except TypeError:
        print('Ошибка! Возможно не верно указан раздел. Удалите все доп фильтры с ссылки')
    except PermissionError:
        print('Ошибка! Вы забыли закрыть созданный ранее excel файл. Закройте и повторите попытку')

if __name__ == '__main__':
    # url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json'
    # headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"} #*/*  любой MIME type
    # response = requests.get(url, headers=headers)
    # data = response.json()
    #
    # with open('wb_catalogs_data.json', 'w', encoding='UTF-8') as file:
    #     json.dump(data, file, indent=2, ensure_ascii=False) # Удаление дубликатов объявлений пространств имен при сериализации. "кранирование ASCII символов.
    #     print(f'Данные сохранены в wb_catalogs_data.json')

    url = 'https://www.wildberries.ru/catalog/obuv/zhenskaya/baletki-i-cheshki'
    low_price = 1000
    top_price = 9000

    parser(url, low_price, top_price)



# url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub&dest=-1075831,-77677,-398551,12358499' \
#               f'&locale=ru&page={page}&priceU={low_price * 100};{top_price * 100}' \
#               f'®ions=64,83,4,38,80,33,70,82,86,30,69,1,48,22,66,31,40&sort=popular&spp=0&{query}'
# https://catalog.wb.ru/catalog/bl_shirts/v6/filters?ab_testing=false&appType=1&cat=8126&curr=rub&dest=-455203&spp=30&uclusters=5
# https://catalog.wb.ru/catalog/beauty26/v6/filters?ab_testing=false&appType=1&cat=8964&curr=rub&dest=-455203&spp=30&uclusters=5
# https://catalog.wb.ru/catalog/beauty26/v6/filters?ab_testing=false&appType=1&cat=8964&curr=rub&dest=-455203&priceU=100000;200000&spp=30&uclusters=5
# https://catalog.wb.ru/catalog/blazers_wamuses/v6/filters?ab_testing=false&appType=1&cat=8136&curr=rub&dest=-455203&priceU=200000;500000&spp=30&uclusters=5
# https://catalog.wb.ru/catalog/blazers_wamuses/v2/catalog?ab_testing=false&appType=1&cat=8136&curr=rub&dest=-455203&page=3&priceU=200000;500000&sort=popular&spp=30&uclusters=5&uiv=6&uv=JTCwBqs7JiMvsyUwrTQqNjNHq9UoYi2sKMIrFK_XKUettaliMpmt1arOm7eml6BkLsStJqSGKRow-a0greIsUK5CrNooPyRWJCysXSGdKpUw3SgjLFGkHTDZovEqAq2wMgQxnjCmr-6qBLCGK5anubD_sdSvLqzMmjysnTFZqvouL5-qqPcp-jEDojWvhazMp_8t86ikoaitGyz-rJ8wf7AMsbit_LFhJG2lBKg6KTWxly6GKzsqXqtWoHMrKKTvLFYnUCryLYMtVieVL6OspighKROxShM4ql4tWS4yqYiuV6L4m4cqQ6lWLC6oBq47p1svfCajLpsu7KUwpamteg
# https://catalog.wb.ru/catalog/men_clothes2/v2/catalog?ab_testing=false&appType=1&cat=8148&curr=rub&dest=-455203&page=1&priceU=100000;300000&sort=popular&spp=30&uclusters=5&uiv=6&uv=JTCwBqs7JiMvsyUwrTQqNjNHq9UoYi2sKMIrFK_XKUettaliMpmt1arOm7eml6BkLsStJqSGKRow-a0greIsUK5CrNooPyRWJCysXSGdKpUw3SgjLFGkHTDZovEqAq2wMgQxnjCmr-6qBLCGK5anubD_sdSvLqzMmjysnTFZqvouL5-qqPcp-jEDojWvhazMp_8t86ikoaitGyz-rJ8wf7AMsbit_LFhJG2lBKg6KTWxly6GKzsqXqtWoHMrKKTvLFYnUCryLYMtVieVL6OspighKROxShM4ql4tWS4yqYiuV6L4m4cqQ6lWLC6oBq47p1svfCajLpsu7KUwpamteg
# url = f'https://catalog.wb.ru/catalog/{shard}/v2/catalog?ab_testing=false&appType=1&{query}&curr=rub&dest=-455203&page={page}&priceU={low_price * 100};{top_price * 100}&sort=popular&spp=30&uclusters=5&uiv=6&uv=JTCwBqs7JiMvsyUwrTQqNjNHq9UoYi2sKMIrFK_XKUettaliMpmt1arOm7eml6BkLsStJqSGKRow-a0greIsUK5CrNooPyRWJCysXSGdKpUw3SgjLFGkHTDZovEqAq2wMgQxnjCmr-6qBLCGK5anubD_sdSvLqzMmjysnTFZqvouL5-qqPcp-jEDojWvhazMp_8t86ikoaitGyz-rJ8wf7AMsbit_LFhJG2lBKg6KTWxly6GKzsqXqtWoHMrKKTvLFYnUCryLYMtVieVL6OspighKROxShM4ql4tWS4yqYiuV6L4m4cqQ6lWLC6oBq47p1svfCajLpsu7KUwpamteg'
