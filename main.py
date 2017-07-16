#-*-coding:utf8-*-
import re

import requests
from gevent import pool as gpool
from gevent import monkey
from bs4 import BeautifulSoup as Bs

WORKERS = 12
http = requests.Session()
ISLANDS = {}


def load_html(url):
    response = http.get(url)
    return response.content


def get_basic_info(url):
    print "parser %s .." % url
    content = load_html(url)
    bs = Bs(content, "html.parser")

    for item in bs.find_all(class_="property-listing-simple"):
        island = {}
        island['title'] = item.find(class_="entry-title").text

        # address: e.g. Dhigali, Raa 环礁, 马尔代夫
        address = item.find(class_="property-address").text

        if u',' in address:
            addresses = address.split(',')
        elif u'\uff0c' in address:
            addresses = address.split(u'\uff0c')

        if len(addresses) == 3:
            island['add1'] = addresses[0].strip()
            island['add2'] = addresses[1].strip()
            island['add3'] = addresses[2].strip()
        elif len(addresses) == 2:
            island['add1'] = addresses[0].strip()
            island['add2'] = ''
            island['add3'] = addresses[1].strip()
        else:  # == 1
            island['add1'] = address.replace(',', ';')
            island['add2'] = ''
            island['add3'] = ''

        # Get detail from items, because the only way to find detail
        # is from the `icon-class`.
        area = item.find(class_='icon-area')
        if area is not None:
            island['area'] = area.find_next_sibling().find(class_='meta-item-value').text.replace(u'公里', '')
        else:
            island['area'] = '0'

        for key in ['bed', 'bath', 'garage', 'ptype', 'tag']:
            detail = item.find(class_='icon-%s' % key)
            if detail is not None:
                island[key] = detail.find_next_sibling().find(class_='meta-item-value').text.replace(',', ';')
            else:
                island[key] = '0'

        island['link'] = item.find(class_='btn-default').attrs['href']
        ISLANDS[island['title']] = island


def get_detail(island):
    island_url = island['link']
    body = load_html(island_url)
    print 'parse detail: %s ..' % island_url

    bs = Bs(body, "html.parser")
    # Extract text like "197USD/人/往返; 12岁以下儿童半价; 未满2周岁免费"
    price_tag = bs.find(class_="property-additional-details-list"). \
            find('dd', string=re.compile(".*USD/.*"))
    if price_tag:
        island['price'] = price_tag.text
    else:
        island['price'] = '-'


def dump_to_csv(datas):
    """
    A dict of island information, key is name of island, value is island info.
    """
    output = 'maldiveschina.csv'
    with open(output, 'w') as f:
        f.write('#, 名字, 消费等级, 沙屋, 水屋, 上岛费用, 上岛交通, 岛, 环礁, 距马累（公里）, 餐厅+酒吧, 链接\n')
        for i, island in enumerate(sorted(datas.values())):
            row = ','.join([
                str(i + 1),
                island['title'],
                island['ptype'],  # price level
                island['bed'],   # beach villa
                island['bath'],  # water villa
                island['price'],  # transform price
                island['tag'],   # transform
                island['add1'],
                island['add2'],
                island['area'],  # for from male
                island['garage'],  # bars
                island['link']   # href
            ])
            f.write(row.encode('utf8'))
            f.write('\n')
    print 'written to %s' % output


def main():
    monkey.patch_all()
    urls = [
        'http://www.maldiveschina.com/property-city/northern-atoll',
        'http://www.maldiveschina.com/property-city/southern-atoll',
        'http://www.maldiveschina.com/property-city/north-male-atoll',
        'http://www.maldiveschina.com/property-city/south-male-atoll',
        'http://www.maldiveschina.com/property-city/ari-atoll',
    ]
    pool = gpool.Pool(WORKERS)

    print 'Get overall island lists.'
    for url in urls:
        pool.spawn(get_basic_info, url)
    pool.join()

    print 'Get islands detail...'
    for island in ISLANDS.values():
        pool.spawn(get_detail, island)
    pool.join()

    dump_to_csv(ISLANDS)


if __name__ == '__main__':
    main()
