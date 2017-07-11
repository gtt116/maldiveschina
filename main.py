#-*-coding:utf8-*-
import requests
from bs4 import BeautifulSoup as Bs

http = requests.Session()


def load_html(url):
    print 'Loading %s' % url
    response = http.get(url)
    return response.content


def get_info(content):
    print "parser it..."
    bs = Bs(content, "html.parser")

    islands = []
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
        islands.append(island)

    return islands


def dump_to_csv(datas):
    with open('maldiveschina.csv', 'w') as f:
        f.write('title, add1, add2, add3, area, beach_villa, water_villa, bars, level, transport, link\n')
        for island in datas:
            row = ','.join([island['title'], island['add1'], island['add2'], island['add3'], island['area'],
                            island['bed'], island['bath'], island['garage'], island['ptype'], island['tag'], island['link']])
            f.write(row.encode('gbk'))
            f.write('\n')


def main():
    urls = [
        'http://www.maldiveschina.com/property-city/northern-atoll',
        'http://www.maldiveschina.com/property-city/southern-atoll',
        'http://www.maldiveschina.com/property-city/north-male-atoll',
        'http://www.maldiveschina.com/property-city/south-male-atoll',
        'http://www.maldiveschina.com/property-city/ari-atoll',
    ]
    total_islands = []
    for url in urls:
        html = load_html(url)
        total_islands.extend(get_info(html))

    dump_to_csv(total_islands)


if __name__ == '__main__':
    main()
