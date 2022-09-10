import requests
from splinter import Browser
from lxml import html
from bs4 import BeautifulSoup
import re
import time
import glob
import os
import pymysql
from multiprocessing import Pool, Value
from selenium.webdriver import ChromeOptions
import sys
import json
import logging
from datetime import datetime
import random

# sys.setrecursionlimit(100)

'''
                      fields:
keyword, name, url, status
# '''
#
# # proxy = None
con = pymysql.connect(host='50.116.50.244',
                      user='root',
                      port=3306,
                      password='Warandgal@12',
                      database='Hotel',
                      charset='utf8mb4',
                      autocommit=True,
                      cursorclass=pymysql.cursors.DictCursor
                      )
cursor = con.cursor()
# global_count = Value(0)
query = '''
    insert into `hotel_info` (`entity_id`, `name`, `hotel_type`, `certified`, `rating`, `count`, `status`, `features`, `address`, `phone`, `top_things`,
    `checkin`, `checkout`, `desc`, `website`, `featured_options`, `all_options`, `photos`, `flag`, `keyword`, `reviews`)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    '''


def check_db(entity_id=''):
    con = pymysql.connect(host='50.116.50.244',
                          user='root',
                          port=3306,
                          password='Warandgal@12',
                          database='Hotel',
                          charset='utf8mb4',
                          autocommit=True,
                          cursorclass=pymysql.cursors.DictCursor
                          )
    cursor = con.cursor()
    check = '''
        select * from `hotel_info` where `entity_id`=%s
        '''
    # print(entity_id)
    cursor.execute(check, entity_id)
    row = cursor.fetchone()
    if row:
        if int(row['flag']) == 0:
            return (0, 'U')
        else:
            return (1, 'S')
    else:
        return (0, 'I')


def get_reviews(url='', windows=False):
    # url = 'https://www.google.com/travel/hotels/entity/{}/reviews'.format('CgkI2OvjrMjquk4QAQ')
    otp = '93128%d' % random.randint(0,10)
    proxy = 'http://%s:%s@us-1m.geosurf.io:8000' % ('630037+US+630037-%s' % otp, '8135be349')
    profile = {
        'network.proxy.http': proxy,
        # 'network.proxy.http_port': proxy,
        # 'network.proxy.ssl': proxy,
        # 'network.proxy.ssl_port': proxy,
        'network.proxy.type': 1
    }
    if not windows:
        executable_path = {'executable_path': r'/usr/local/bin/chromedriver'}
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        brw = Browser('chrome', headless=True, **executable_path, options=options)
    else:
        brw = Browser('chrome', headless=True, profile_preferences=profile)

    brw.visit(url)
    time.sleep(3)
    soup = BeautifulSoup(brw.html, 'html.parser')
    review = soup.find('h2', text='Reviews')
    reviews = []
    count = 0
    if review:
        next_element = review.parent
        tree = html.fromstring(str(next_element.nextSibling))
        path = "//div/c-wiz/div[1]/div[1]/div[1]/div"
        for i, div in enumerate(tree.xpath(path)):
            if count < 5:
                reviewer = div.xpath('./div[1]/div[1]/div/span/a/text()')
                text = div.xpath('./div[2]/div[1]/div[2]/div/div[1]/div/span/text()')
                # service = div.xpath('./div[2]/div[1]/div[2]/div/div[2]/div/div/span//text()')
                # x = {
                #     'Rooms': 'N/A',
                #     'Service': 'N/A',
                #     'Location': 'N/A'
                # }
                # if service:
                #     try:
                #         rooms = service[1]
                #     except:
                #         rooms = 'N/A'
                #
                #     try:
                #         service_ = service[3]
                #     except:
                #         service_ = 'N/A'
                #
                #     tr
                #     x = {
                #         'Rooms': service[1],
                #         'Service': service[3],
                #         'Location': service[5]
                #     }
                if text:
                    count += 1
                    reviews.append({
                        'reviewer': ''.join(reviewer) if reviewer else '',
                        'text': ''.join(text) if text else '',
                        # 'features': x
                    })
    brw.quit()

    return reviews


def return_total_links(text=''):
    # soup = BeautifulSoup(text, 'html.parser')
    tree = html.fromstring(text)
    links = tree.xpath('//*/c-wiz/div/a/@data-href')
    all = [l for l in links if 'entity' in l]
    return (len(list(set(all))))


def hotel_details(params=[]):
    start = datetime.now()
    retry = 5
    entity = params[0]
    state = check_db(entity_id=entity)
    if not state[0]:
        keyword = params[1]
        # otp = '93128%d' % random.randint(0, 10)
        # global_count.va
        url = f'https://www.google.com/travel/hotels/entity/{entity}/overview'.format(entity)
        print('Processing for url %s' % url)
        # gs_proxy_addr = 'http://%s:%s@us-1m.geosurf.io:8000' % ('630037+US+630037-%s' % otp, '8135be349')

        # proxy = {
        #     'http': gs_proxy_addr,
        #     'https': gs_proxy_addr
        # }
        details = {

            'keyword': keyword,
            'entity_id': entity,
            'basic_info': {
                'name': '',
                'type': '',
                'certify': ''
            },
            'reviews': [],
            'rating': '',
            'count': '',
            'status': '',
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
            'featured_options': [],
            'all_options': [],
            'photos': [],
            'success': 0
        }
        ses = requests.Session()
        n_retries = 0
        # while True:
        #     try:
        response = None
        while True:
            try:
                url = f'https://www.google.com/travel/hotels/entity/{entity}/overview'.format(entity)
                print('Processing for url %s' % url)
                gs_proxy_addr = 'http://%s:%s@us-1m.geosurf.io:8000' % ('630037+US+630037-%s' % otp, '8135be349')

                proxy = {
                    'http': gs_proxy_addr,
                    'https': gs_proxy_addr
                }
                response = ses.get(url=url, timeout=15, proxies=proxy)
                break
            except requests.exceptions.ReadTimeout as e:
                print(str(e))
                n_retries += 1
            except requests.exceptions.ProxyError as e:
                print(str(e))
                n_retries += 1
            except:
                otp = '93128%d' % random.randint(0, 10)
            if n_retries > retry:
                break
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            # search_text = re.findall(r'[0-9] top things to know', response.text)
            find_a = soup.find('a', {'id':'entity-info'})
            if find_a:
                find_a = find_a.previous_element
                details['success'] = 1
            else:
                details['success'] = 0
                    # break
                # except Exception as e:
                #     print(str(e))
                #     n_retries += 1
                #     details['success'] = 0
                # if n_retries > retry:
                #     details['success'] = 0
                #     break

            if details['success'] == 1:
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    search_text = re.findall(r'[0-9] top things to know', response.text)
                    find_a = soup.find('a', {'id':'entity-info'}).previous_element
                    # print(search_text, url)
                    if search_text:
                        search_text = ''.join(search_text[0])
                        things_to_know = soup.find('h2', text=search_text)
                        if things_to_know:
                            things_to_know_check = things_to_know.nextSibling
                            if things_to_know_check:
                                tree = html.fromstring(str(things_to_know_check))
                                get_things = tree.xpath("//div[1]/div")
                                if not get_things:
                                    things_to_know_check = things_to_know.nextSibling.nextSibling
                                    tree = html.fromstring(str(things_to_know_check))
                                    get_things = tree.xpath("//div[1]/div")
                                for things in get_things:
                                    text = ''.join([t for t in things.xpath('./div/div[2]//text()') if t != ''])
                                    if text:
                                        details['top_things'].append(text)

                    check_for_featured_options = soup.find('span', text='Featured options')
                    if check_for_featured_options:
                        section_option = check_for_featured_options.parent.parent.parent.next_sibling

                        tree = html.fromstring(str(section_option))
                        featured_path = tree.xpath('//div/span/div')
                        featured_options = []
                        for featured in featured_path:
                            site = featured.xpath('./div/div/div/div/a/@href')
                            if site:
                                site = 'https://www.google.com%s' % ''.join(site)
                            name = featured.xpath('./div/div/div/div/a/div/div[1]/div/span[1]/span/text()')
                            site_name = ''
                            if name:
                                site_name = ''.join(name)
                            featured_options.append({
                                'site': site,
                                'name': site_name
                            })
                        details['featured_options'] = featured_options

                    check_for_all_options = soup.find('span', text='All options')
                    if check_for_all_options:
                        section_option = check_for_all_options.parent.parent.parent.next_sibling
                        tree = html.fromstring(str(section_option))
                        all_path = tree.xpath('//div/span/div')
                        all_options = []
                        for featured in all_path:
                            site = featured.xpath('./div/div/div/div/a/@href')
                            if site:
                                site = ''.join(site)
                                if 'http' not in site[:4]:
                                    site = 'https://www.google.com%s' % ''.join(site)
                            name = featured.xpath('./div/div/div/div/a/div/div[1]/div/span[1]/span/text()')
                            site_name = ''
                            if name:
                                site_name = ''.join(name)
                            all_options.append({
                                'site': site,
                                'name': site_name
                            })
                        details['all_options'] = all_options

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
                            details['basic_info']['certify'] = certify[0]

                    if hotel_type:
                        details['basic_info']['type'] = hotel_type[0]

                    '''
                    bottom section
                    '''
                    rating = tree.xpath('//section[2]/div/div[1]/div/div[2]/div[1]/div[1]/text()')

                    if rating:
                        details['rating'] = ''.join(rating)
                    review_section = tree.xpath('//section[2]/div/div[1]/div/div[2]/div[2]//text()')
                    if review_section:
                        details['status'] = review_section[0]

                    if len(review_section) > 2:
                        details['count'] = review_section[-1]

                    features = tree.xpath('//section[2]/div/div[2]/text()')
                    if features:
                        details['features'] = ''.join(features)
                    about_this_hotel = soup.find_all('h2', text='About this hotel')
                    # print(about_this_hotel, url)
                    if about_this_hotel:
                        n_ = len(about_this_hotel) - 1
                        about_this_hotel1 = about_this_hotel[n_].parent
                        tree = html.fromstring(str(about_this_hotel1))
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

                    photos = soup.find_all('div', {'data-tab': 'photos'})
                    if photos:
                        c = 0
                        for ph in photos:
                            try:
                                c += 1
                                # print(ph.next_element['src'])
                                if c < 15:
                                    details['photos'].append(ph.next_element['src'])
                                else:
                                    break
                            except:
                                pass

                    url = f'https://www.google.com/travel/hotels/entity/{entity}/reviews'.format(entity)
                    # print(url)
                    reviews = get_reviews(url=url)
                    # print(reviews)
                    if reviews:
                        details['reviews'] = reviews

                # with open("sample.txt", "w") as f:
                #     f.write(str(details))
                #
                endtime = datetime.now()  #
                total_time = (endtime - start).total_seconds()
                print('Total time = %0.2f sec.' % total_time)
                '''
                 # if photos:
                    #     if len(photos) > 1:
                    #         folder = os.path.join(folder_name, details['folder_name'])
                    #         if not os.path.exists(folder):
                    #             os.makedirs(folder)
                    #         all_images = photos[1].find_all('img')
                    #         count = 0
                    #         for image in all_images:
                    #             data_src = image['data-src']
                    #             if 'maps.googleapis' not in data_src:
                    #                 count += 1
                    #                 filename = os.path.join(folder, 'image%d.jpg' % count)
                    #                 res = requests.get(data_src, stream=True, proxies=proxy)
                    #                 with open(filename, 'wb') as f:
                    #                     shutil.copyfileobj(res.raw, f)
                    #                 details['photos'].append(data_src)
                '''

            else:
                details['success'] = 0

            result = process_results(details)
            if state[1] == 'I':
                try:
                    cursor.execute(query, result)
                    con.commit()
                except pymysql.IntegrityError:
                    print('Already Exists.')
            if state[1] == 'U':
                update_query = '''
                update `hotel_info` set `name`=%s, `hotel_type`=%s, `certified`=%s,`rating`=%s,`count`=%s, `status`=%s,
                `features`=%s,`address`=%s,`phone`=%s,`top_things`=%s,`checkin`=%s,`checkout`=%s,`desc`=%s,`website`=%s,`featured_options`=%s,
                `all_options`=%s,`photos`=%s,`flag`=%s,`reviews`=%s where `entity_id`=%s
                '''
                # result = (entity_id, name, hotel_type, certified, rating, count, status, features, address, phone,
                #           top_things, checkin, checkout, desc, website, featured_options, all_options, photos, flag,
                #           keyword,
                #           reviews)
                values = (result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8],
                          result[9], result[10], result[11], result[12], result[13], result[14], result[15], result[16],
                          result[17], result[18],
                          result[20], entity)
                cursor.execute(update_query, values)
                print('%s Updated' % entity)

    else:
        details = {}

    return details


def get_entity_from_db():
    query_db = '''
    select * from `hotel_info` join `keywords` on hotel_info.keyword = keywords.index where hotel_info.flag=0 and keywords.run_from=1
    '''
    cursor.execute(query_db)
    result = cursor.fetchall()
    inputs = []
    for res in result:
        inputs.append([res['entity_id'], res['keyword']])
    return inputs


def return_all_txt_files(folder=''):
    filenames = []
    for file in glob.glob('%s/*.txt' % folder):
        kb = os.path.getsize(file)
        if kb != 0:
            filenames.append(file)

    return filenames


def read_from_file():
    urls = []
    max_limit = 20
    with open(filename, 'r') as f:
        data = f.readlines()
        count = 0
        for d in data:
            if count < max_limit:
                count += 1
                string = d.strip().split(',')[-1]

                urls.append(string.replace('/entity/', '').strip())
    return urls


def write_into_db(values=[]):
    con = pymysql.connect(host='50.116.50.244',
                          user='root',
                          port=3306,
                          password='Warandgal@12',
                          database='Hotel',
                          charset='utf8mb4',
                          autocommit=True,
                          cursorclass=pymysql.cursors.DictCursor
                          )
    if con:
        pass


def get_all_url_from_db():
    query = '''
        select * from `hotel_info` where `flag`=0
    '''
    cursor.execute(query)
    result = cursor.fetchall()
    inputs = []
    for res in result:
        keyword = res['keyword']
        entity_id = res['entity_id']
        inputs.append((entity_id, keyword))
    return inputs


def get_entity_ids_from_db():

        query = '''
            select * from `keywords` where `flag`=1 and `run_from`=2
        '''
        cursor.execute(query)
        result = cursor.fetchall()
        inputs = []

        for res in result:
            keyword = '%s in %s, %s' % (res['key'], res['city'], res['country_code'])
            entity_id = res['entity_id']
            if entity_id:
                list_of_links = entity_id.split(',')
                placeholder = ','.join(['%s'] * len(list_of_links))
                query_find = '''
                    select `entity_id` from `hotel_info` where `entity_id` in ({})
                    '''.format(placeholder)

                cursor.execute(query_find, list_of_links)
                rows = cursor.fetchall()
                entitys = [r['entity_id'] for r in rows]
                values = list(set(list_of_links) - set(entitys))
                # print(values)
                if values:
                    repeat_keywords = [keyword] * len(values)
                    inputs += list(zip(values, repeat_keywords))
        return inputs

def process_results(res=''):
    result = []
    n_count = re.findall(r'\d+', res['count'])
    if not n_count:
        count = 0
    else:
        count = ''.join(n_count)
    entity_id = res['entity_id']
    keyword = res['keyword']
    name = res['basic_info']['name']
    hotel_type = res['basic_info']['type']
    certified = res['basic_info']['certify']
    reviews = json.dumps(res['reviews'])
    rating = res['rating']
    # count = ''.join()
    status = res['status']
    features = res['features']
    address = res['address']
    phone = res['phone']
    top_things = json.dumps(res['top_things'])
    checkin = res['about']['checkin']
    checkout = res['about']['checkout']
    desc = res['about']['desc']
    website = res['website']
    featured_options = json.dumps(res['featured_options'])
    all_options = json.dumps(res['all_options'])
    photos = json.dumps(res['photos'])
    flag = res['success']
    result = (entity_id, name, hotel_type, certified, rating, count, status, features, address, phone,
              top_things, checkin, checkout, desc, website, featured_options, all_options, photos, flag, keyword,
              reviews)
    return result


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, filename='status.log')
    txt_files = get_all_url_from_db()[6000:]
    # txt_files = get_entity_from_db()
    print('Total files = %d' % len(txt_files))
    with Pool(2) as p:
        p.map(hotel_details, txt_files)
