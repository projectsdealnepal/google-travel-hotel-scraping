import requests
import logging
from lxml import html
from bs4 import BeautifulSoup
import re
import csv
import os
import shutil
# import config
from scrape_landing_page import hotel_scraper
from multiprocessing import Pool, Lock, Process

'''
fields: 
keyword, name, url, status
'''

proxy = None


def return_total_links(text=''):
    # soup = BeautifulSoup(text, 'html.parser')
    tree = html.fromstring(text)
    links = tree.xpath('//*/c-wiz/div/a/@data-href')
    all = [l for l in links if 'entity' in l]
    return (len(list(set(all))))


def hotel_details(params=[]):
    url = params[0]
    keyword = params[1]
    url = f'https://www.google.com/travel/hotels{url}/overview'.format(url)
    print('Processing for url %s' % url)
    # url = 'https://www.google.com/travel/hotels/entity/CgsIgeKwo5bWior1ARABGnxBRkUyQUt3cUF0dnEyT3lxcHhqRUdNWEhNdmlPbEhCeGg3cHJyMHJKUTNrVHk3d3VyMlF4SnA0RklaVHduMFNRSjRsVERpTkNVQjM3RWR4OTdXb1p2S1lBUjBqNmFvRkpxTnBnTS02ekpWVV9jZ0JVTEtubVNmOGlJOEU5/overview?utm_campaign=sharing&utm_medium=link&utm_source=htls&ts=CAESABogCgIaABIaEhQKBwjmDxAIGAoSBwjmDxAIGAsYATICEAAqCQoFOgNOUFIaAA'
    folder_name = "images"
    details = {
        'keyword': keyword,
        'id': url,
        'basic_info': {
            'name': '',
            'type': '',
            'certify': ''
        },
        'reviews': {
            'rating': '',
            'count': '',
            'status': ''
        },
        'features': '',
        'address': '',
        'phone': '',
        'top_things': [],
        'about': {
            'checkin': '',
            'checkout': '',
            'desc': '',
        },
        'website': '',
        'featured_options':
            {
                'booking_com': ''
            }
        ,
        'photos': [],
        'folder_name': '',
        'success': 0
    }
    ses = requests.Session()
    try:
        response = ses.get(url=url, proxies=proxy)
        details['success'] = 1
    except Exception as e:
        details['success'] = 0
    if details['success'] == 1:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            search_text = re.findall(r'[0-9] top things to know', response.text)
            search_text = ''.join(search_text[0])
            find_a = soup.find('a', id='entity-info').previous_element
            things_to_know = soup.find('h2', text=search_text)
            if things_to_know:
                things_to_know = things_to_know.nextSibling
                tree = html.fromstring(str(things_to_know))
                get_things = tree.xpath("//div[1]/div")
                for things in get_things:
                    text = ''.join([t for t in things.xpath('./div/div[2]//text()') if t != ''])
                    if text:
                        details['top_things'].append(text)

            section = find_a.find_all('section')
            tree = html.fromstring(str(section))
            name = tree.xpath('//section[1]/div[1]/div[1]/div[1]/h1/text()')
            if name:
                name = ''.join(name)
                details['basic_info']['name'] = name
                details['folder_name'] = re.sub(r'[^A-Za-z0-9\s]', '', name)

            # tree = html.fromstring(str(section[0]))
            hotel_type = tree.xpath('//section[1]/div[1]/div[1]/div[2]/span/text()')
            website = tree.xpath('//section[1]/div[2]/span[1]/div/div/a/@href')
            if website:
                details['website'] = ''.join(website)

            locations = tree.xpath('//section[1]/div[1]/div[1]/div[2]/div')
            if locations:
                address = locations[-1].xpath('./span/text()')
                if address:
                    details['address'] = address[0]

                if len(address) > 2:
                    details['phone'] = address[-1]

            if len(locations) > 1:
                certify = locations[0].xpath('./span//text()')
                if certify:
                    details['basic_info']['certify'] = ''.join(certify)

            if hotel_type:
                details['basic_info']['type'] = hotel_type[0]

            '''
            bottom section
            '''
            rating = tree.xpath('//section[2]/div/div[1]/div/div[2]/div[1]/div[1]/text()')

            if rating:
                details['reviews']['rating'] = ''.join(rating)
            review_section = tree.xpath('//section[2]/div/div[1]/div/div[2]/div[2]//text()')
            if review_section:
                details['reviews']['status'] = review_section[0]

            if len(review_section) > 2:
                details['reviews']['count'] = review_section[-1]

            features = tree.xpath('//section[2]/div/div[2]/text()')
            if features:
                details['features'] = ''.join(features)
            about_this_hotel = soup.find_all('h2', text='About this hotel')
            about_this_hotel = about_this_hotel[1].parent
            if about_this_hotel:
                tree = html.fromstring(str(about_this_hotel))
                section = tree.xpath('//section/div/div[1]/div[1]/*//text()')
                about = []
                for sec in section:
                    remove = re.findall(r'[A-Za-z0-9]', sec)
                    if remove and not 'Read more' in sec:
                        about.append(sec)

                if about:
                    details['about']['desc'] = ''.join(about)
                check_in = tree.xpath('//section/div/div[1]/div[2]/div[1]/span/text()')
                if check_in:
                    details['about']['checkin'] = ''.join(check_in)
                check_out = tree.xpath('//section/div/div[1]/div[2]/div[2]/span/text()')
                if check_out:
                    details['about']['checkout'] = ''.join(check_out)

            bookings = re.findall('https://www.booking.com/(.*)\" data-ved', response.text)
            if bookings:
                booking_com = 'https://www.booking.com/%s' % bookings[0]
                details['featured_options']['booking_com'] = booking_com

            photos = soup.find_all('div', {'aria-label': 'Photos'})
            if photos:
                if len(photos) > 1:
                    folder = os.path.join(folder_name, details['folder_name'])
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    all_images = photos[1].find_all('img')
                    count = 0
                    for image in all_images:
                        data_src = image['data-src']
                        if 'maps.googleapis' not in data_src:
                            count += 1
                            filename = os.path.join(folder, 'image%d.jpg' % count)
                            res = requests.get(data_src, stream=True, proxies=proxy)
                            with open(filename, 'wb') as f:
                                shutil.copyfileobj(res.raw, f)
                            details['photos'].append(data_src)
        else:
            details['success'] = 0

    return details


def google_search(keyword=''):
    # for i in range(10):
    url = 'https://www.google.com/travel/hotels/search?q=hotels%20with%20pools%20in%20sacramento&hl=en&ie=UTF-8&tbs=lf%3A1%2Clf_ui%3A6&rlst=f&rflfq=1&num=200&rlha=1&sa=X&ved=0CAAQ5JsGahcKEwjQ-LmFyLb5AhUAAAAAHQAAAAAQBA&utm_campaign=sharing&utm_medium=link&utm_source=htls&ts=CAESCgoCCAMKAggDEAAaLgoQEgw6ClNhY3JhbWVudG8aABIaEhQKBwjmDxAIGAkSBwjmDxAIGAoYATICEAAqCwoHKAE6A05QUhoA&rp=OAE&ap=EgNDQXcwAw'
    params = {
        'q': keyword
    }
    response = requests.get(url)
    with open('search%s.html', 'wb') as f:
        f.write(response.content)


# def hotel_scraper(keyword=''):
#     params = {
#         'q': keyword,
#         'hl': 'en',
#         'utm_campaign': 'sharing',
#         'utm_medium': 'link',
#         'utm_source': 'htls',
#         'ved': '0CAAQ5JsGahcKEwjgqaOr5Lb5AhUAAAAAHQAAAAAQBA',
#         'ts': 'CAESABouChASDDoKU2FjcmFtZW50bxoAEhoSFAoHCOYPEAgYCRIHCOYPEAgYChgBMgIQACoLCgcoAToDTlBSGgA',
#         'rp': 'OAE'
#     }
#     url = 'https://www.google.com/travel/hotels/search'
#     resp = requests.get(url, params=params)
#     print(resp.url)
#     with open('search.html', 'wb') as f:
#         f.write(resp.content)
#     soup = BeautifulSoup(resp.text, 'html.parser')
#
#     results = soup.find('div', {'aria-label': 'Beginning of results'})
#     siblings = results.nextSibling
#
#     tree = html.fromstring(str(siblings))
#     links = tree.xpath('//div/c-wiz/c-wiz/div/a/@href')
#     return links


# links = hotel_scraper(keyword='hotels with pools in sacramento')
# hotel_details(url=links[0])
# hotel_details(keyword='hotels with pools in sacramento')
# google_search()
# request_html(keyword='hotels with pools in sacramento')
def read_from_file():
    text = open('search1.txt', 'r').read()
    tree = html.fromstring(text)
    links = tree.xpath('//*/c-wiz/div/a/@data-href')
    all = [l for l in links if 'entity' in l]
    return list(set(all))


if __name__ == '__main__':
    rating = 4
    keyword = 'hotels with pools in sacramento'
    output = []
    logging.basicConfig(format='%(asctime)s : %(levelname)s', level=logging.INFO, filename='status.log')
    logging.info('Processing Started for keyword %s' % keyword)
    # try:
    #     scrape = hotel_scraper(ratings=rating, keyword=keyword)
    #     list_of_links = scrape.links
    # except Exception as e:
    #     list_of_links = []
    #     logging.error('Scraper Failed for %s' % keyword)
    max_limit = 20
    list_of_links = read_from_file()
    if list_of_links:
        list_of_links = list_of_links[:max_limit]
        repeat_keywords = [keyword] * len(list_of_links)
        inputs = list(zip(list_of_links, repeat_keywords))
        if list_of_links:
            with Pool(5) as p:
                output = p.map(hotel_details, inputs)
        else:
            logging.error('List of links for %s 0' % keyword)
    logging.info('Processing Complete for keyword. %d Hotels pulled. %s' % (keyword, len(list_of_links)))

    print(output)
