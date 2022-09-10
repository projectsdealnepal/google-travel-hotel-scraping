import re
import pymysql
import json
from requests.auth import HTTPBasicAuth
import requests
import time
import urllib.parse
from datetime import datetime


def get_info_of_hotel(entity_id=''):
    connect = pymysql.connect(host='50.116.50.244',
                              user='root',
                              port=3306,
                              password='',
                              database='Hotel',
                              charset='utf8mb4',
                              autocommit=True,
                              cursorclass=pymysql.cursors.DictCursor
                              )
    cursor = connect.cursor()
    query = '''
    select * from `hotel_info` where `entity_id`='%s'
    ''' % entity_id
    cursor.execute(query)
    result = cursor.fetchone()
    state = True
    missing = []
    if result:
        # name = result['name']
        # hotel_type = result['hotel_type']
        # certified = result['certified']
        # rating = result['rating']
        # review_count = result['count']
        # status = result['status']
        # features = result['features']
        # address = result['address']
        # phone = result['phone']
        top_things = json.loads(result['top_things'])
        # checkin = result['checkin']
        # checkout = result['checkout']
        # website = result['website']
        desc = result['desc']
        # keyword = result['keyword']
        photos = json.loads(result['photos'])
        # featured_options = json.loads(result['featured_options'])
        # all_options = json.loads(result['all_options'])
        reviews = json.loads(result['reviews'])

        if 'Check-in time' in desc:
            check_in = re.findall('Check-in time:(.*)Check', desc)
            if check_in:
                check_in = ''.join(check_in)
                desc = desc.replace('Check-in time:%s' % check_in, '')
            else:
                check_in = re.findall('Check-in time:(.*)', desc)
                check_in = ''.join(check_in)
                desc = desc.replace('Check-in time:%s' % check_in, '')

        if 'Check-out time' in desc:
            check_out = re.findall('Check-out time:(.*)', desc)
            check_out = ''.join(check_out)
            desc = desc.replace('Check-out time:%s' % check_out, '')

        if not desc:
            state = False
            missing.append('About Missing.')

        if not photos:
            state = False
            missing.append('Photos Missing.')

        if not reviews:
            state = False
            missing.append('Reviews Missing.')
        else:
            count = 0
            for rev in reviews:
                if rev.get('text'):
                    count += 1
            if count == 0:
                state = False

        if not top_things:
            state = False
            missing.append('Top things Missing.')


    return {
        'state': state,
        'missing': missing,
        'data': result
    }


def get_related_links(keyword='', city='', state=''):
    year = datetime.now().year
    connect = pymysql.connect(host='50.116.50.244',
                              user='root',
                              port=3306,
                              password='',
                              database='Hotel',
                              charset='utf8mb4',
                              autocommit=True,
                              cursorclass=pymysql.cursors.DictCursor
                              )
    cursor = connect.cursor()
    query = '''
        select * from `keywords` where replace(`index`, "'", '')='%s'
        ''' % (keyword)
    cursor.execute(query)
    row = cursor.fetchone()
    related_links = []
    if row:
        # city = row['city']
        query = '''
        select * from `keywords` where replace(`city`, "'", '')='%s' and `country_code`='%s'
        ''' % (city, state)
        cursor.execute(query)
        cities = cursor.fetchall()
        for i, c in enumerate(cities):
            entity_ids = c['entity_id']
            keys = c['index'].split(',')
            index = keys[0].split(' ') + [keys[-1].strip()]
            mylist = list(dict.fromkeys(index))
            count = 0
            if entity_ids:
                for entity in entity_ids.split(','):
                    res = get_info_of_hotel(entity_id=entity.strip())
                    if res.get('state'):
                        count += 1
            # print('%d. = %d' % (i, count))
            if count > 0:
                related_links.append(
                    ('-'.join([x.lower() for x in mylist]), "%s (%d)" % (' '.join(mylist), year), count))
    return related_links


def post_data_to_wp(result={}):
    state = True
    text = ''
    if result:
        name = result['name']
        hotel_type = result['hotel_type']
        certified = result['certified']
        if certified:
            certified =certified.split(' ')[0]
        else:
            certified = ''

        rating = result['rating']
        review_count = result['count']
        status = result['status']
        features = result['features']
        address = result['address']
        phone = result['phone']
        top_things = json.loads(result['top_things'])
        checkin = result['checkin']
        checkout = result['checkout']
        website = result['website']
        desc = result['desc']
        # keyword = result['keyword']
        photos = json.loads(result['photos'])
        featured_options = json.loads(result['featured_options'])
        all_options = json.loads(result['all_options'])
        reviews = json.loads(result['reviews'])
        missing = []
        # url = 'https://www.google.com/travel/hotels/entity/{}'.format(entity_id)
        hotel_type = '(%s)' % hotel_type if hotel_type else ''
        hotel_name = name
        name = '%s %s' % (name, hotel_type)

        if address:
            url = 'https://www.google.com/maps/place/%s' % address
            address = '<li><strong>Address</strong>: <a href="%s" target="_blank">%s</a></li>' % (url, address)

        if phone:
            phone = '<li><strong>Phone</strong>: %s</li>' % phone

        rating = '<li><strong>Ratings</strong>: {} ({} reviews) {} {}</li>'.format(rating, review_count, status, certified)
        if website:
            website = '<li><strong>Website</strong> : <a href="{}">{}</a></li>'.format(website, hotel_name)

        if checkin:
            checkin = '<li class="Py1Pk"><strong>Check-in time: </strong><span class="rJ3U9c">{}</span></li>'.format(
                checkin)
        if checkout:
            checkout = '<li class="Py1Pk"><strong>Check-out time: </strong><span class="rJ3U9c">{}</span></li>'.format(
                checkout)
        if features:
            features = '<li><strong>Quick Summary</strong>: {} </li>'.format(features)

        details = '<ul>%s%s%s%s%s%s%s</ul>' % (
            address, phone, rating, website, checkin, checkout, features)

        if 'Check-in time' in desc:
            check_in = re.findall('Check-in time:(.*)Check', desc)
            if check_in:
                check_in = ''.join(check_in)
                desc = desc.replace('Check-in time:%s' % check_in, '')
            else:
                check_in = re.findall('Check-in time:(.*)', desc)
                check_in = ''.join(check_in)
                desc = desc.replace('Check-in time:%s' % check_in, '')

        if 'Check-out time' in desc:
            check_out = re.findall('Check-out time:(.*)', desc)
            check_out = ''.join(check_out)
            desc = desc.replace('Check-out time:%s' % check_out, '')
        if desc:
            about = '<h4 class="ZSxxwc g2m8zc">About this hotel</h4>'
        else:
            about = ''
            state = False
            missing.append('About missing.')
        things_to_know = []
        for things in top_things:
            things_to_know.append('''<li>%s</li>''' % things)
        things_to_know = ''.join(things_to_know)
        if things_to_know:
            things_to_know = '<h4>Things You Need to Know</h4><ul>%s</ul>' % (things_to_know)
        else:
            state = False
            missing.append('Things to know missing')

        all_reviews = []
        n_review = 0
        if reviews:
            for review in reviews:
                if review['text']:
                    n_review += 1
                    if n_review <= 3:
                        split_review = review['text'].split('.')
                        summary = ''.join(split_review[:3])
                        remain = ''.join(split_review[3:])
                        all_reviews.append(
                            '''<div class="fBDixb""><blockquote cite="{}"><u>{}</u>
                            <details>
                            <summary>{}</summary>
                            <p>{}</p>
                            </details>                            
                            
                            </blockquote></div>'''.format(
                                review['reviewer'], review['reviewer'], summary, remain))
                    # all_reviews.append('''
                    # <div class="fBDixb"><div class="su-quote su-quote-style-default su-quote-has-cite"><div class="su-quote-inner su-u-clearfix su-u-trim">%s<span class="su-quote-cite"><a>%s</a></span></div></div></div>''' % (review['text'], review['reviewer']))
        all_reviews = ''.join(all_reviews)
        if all_reviews:
            all_reviews = '''<h4 class="YMlIz">Feedback From Real Customers</h4>%s''' % all_reviews
        else:
            all_reviews = ''
            state = False
            missing.append('Reviews missing')
        # all_reviews += '''<div></div>'''
        # photos = []
        if photos:
            all_photos = []
            total = len(photos)
            count = 0
            for i in range(0, total, 2):
                remain = total - count
                if remain > 1:
                    all_photos.append(
                        '''<tr><td><a href="%s" target="_blank" rel="noopener noreferrer" data-caption="" tabindex="0"><img src="%s"></a></td><td><a href="%s" target="_blank" rel="noopener noreferrer" data-caption="" tabindex="0"><img src="%s"></a></td></tr>''' % (
                            photos[i], photos[i], photos[i + 1], photos[i + 1]))
                    count += 2
                else:
                    count += 1
                    all_photos.append(
                        '''<tr><td  colspan=2><a href="{}" target="_blank" rel="noopener noreferrer"  tabindex="0"><img width="100%" style="display:block;" src="{}"></a></td></tr>'''.format(
                            photos[i], photos[i]))

            all_photos = ''.join(all_photos)
            photos = '''<table><tbody><tr>%s</tr></tbody></table>''' % all_photos
        else:
            photos = ''
            state = False
            missing.append('Photos Missing')

        featured_ = []
        for featured in featured_options:
            # button = '''<p><button url="%s" target="blank" style="flat" background="#4e6663" size="5" center="yes">Visit Site</button></p>''' % \
            #          featured['site']

            furl = re.findall(r'adurl=(.*)', featured['site'])
            if furl:
                furl = urllib.parse.unquote(''.join(furl))
            else:
                furl = urllib.parse.unquote(featured['site'])
            button = '''
            <div class="su-button-center"><a href="%s" class="su-button su-button-style-flat" style="color:#FFFFFF;background-color:#4e6663;border-color:#3f5250;border-radius:7px;-moz-border-radius:7px;-webkit-border-radius:7px" target="_blank" rel="noopener noreferrer nofollow"><span style="color:#FFFFFF;padding:0px 20px;font-size:16px;line-height:32px;border-color:#849492;border-radius:7px;-moz-border-radius:7px;-webkit-border-radius:7px;text-shadow:none;-moz-text-shadow:none;-webkit-text-shadow:none">Visit Site</span></a></div>''' % \
                     furl
            featured_.append(
                '''<tr><td style="width: 300px;" align="left"><a href="%s" >%s</a></td><td style="width: 300px;" align="right">%s</td><tr>''' % (
                    furl, featured['name'], button))
        featured_ = ''.join(featured_)
        if featured_:
            ad_features = '''<table  cellspacing="0" cellpadding="0"><tbody>%s</tbody></table>''' % featured_
            ad_features = '''<h4>Featured Options</h4>%s''' % ad_features
        else:
            ad_features = ''

        alloptions = []
        # button = '''<p><button url="https://www.booking.com/hotel/us/rush.en-gb.html?aid=304142&amp;label=gen173nr-1DCAEoggI46AdIM1gEaKcBiAEBmAEJuAEXyAEM2AED6AEBiAIBqAIDuALX84iUBsACAdICJDQ0ZWMxZThhLTcyNzMtNGE2NS1iYjUwLWI1MThmNTY0MzY0N9gCBOACAQ&amp;sid=f7deca2c8205d45a12d9c86c68705f15&amp;all_sr_blocks=119319612_213825048_0_2_0;checkin=2022-05-17;checkout=2022-05-18;dest_id=1193196;dest_type=hotel;dist=0;group_adults=2;group_children=0;hapos=1;highlighted_blocks=119319612_213825048_0_2_0;hpos=1;matching_block_id=119319612_213825048_0_2_0;no_rooms=1;req_adults=2;req_children=0;room1=A%2CA;sb_price_type=total;show_room=119319612;sr_order=popularity;sr_pri_blocks=119319612_213825048_0_2_0__29900;srepoch=1652708898;srpvid=208c610de79402e7;type=total;ucfs=1" target="blank" style="flat" background="#4e6663" size="5" center="yes">Visit Site</button></p>'''

        for featured in all_options:
            furl = re.findall(r'adurl=(.*)', featured['site'])
            if furl:
                furl = urllib.parse.unquote(''.join(furl))
            else:
                furl = urllib.parse.unquote(featured['site'])
            button = '''<div class="su-button-center"><a href="%s" class="su-button su-button-style-flat" 
            style="color:#FFFFFF;background-color:#4e6663;border-color:#3f5250;border-radius:7px;-moz-border-radius
            :7px;-webkit-border-radius:7px" target="_blank" rel="noopener noreferrer nofollow"><span 
            style="color:#FFFFFF;padding:0px 20px;font-size:16px;line-height:32px;border-color:#849492;border-radius
            :7px;-moz-border-radius:7px;-webkit-border-radius:7px;text-shadow:none;-moz-text-shadow:none;-webkit-text
            -shadow:none">Visit Site</span></a></div>''' % \
                     furl
            alloptions.append(
                '''<tr><td style="width: 300px;" align="left"><a href="%s" >%s</a></td><td style="width: 300px;" align="right">%s</td><tr>''' % (
                    furl, featured['name'], button))
        alloptions = ''.join(alloptions)
        if alloptions:
            ad_options = '''<table  cellspacing="0" cellpadding="0"><tbody>%s</tbody></table>''' % alloptions
            ad_options = '''<h4>All Options</h4>%s''' % ad_options
        else:
            ad_options = ''

        # print(ad_features, ad_options)
        text = '''%s<div class="featured-image  page-header-image-single ">%s</div>%s%s<div class="YOCwW"><div class="U1L8Pd"><div class="D35lie"><p>%s</p></div><div class="D35lie">%s%s<div></div></div></div></div><div></div><div class="YOCwW"><div class="U1L8Pd">%s</div><div class="U1L8Pd">%s</div>'''

    return {
        'status': state,
        'html': text,
        'missing': missing,
        'name': name,
        'photos': photos,
        'details': details,
        'about': about,
        'desc': desc,
        'things': things_to_know,
        'reviews': all_reviews,
        'features': ad_features,
        'options': ad_options
    }


def get_all_keywords_from_db():
    connect = pymysql.connect(host='50.116.50.244',
                              user='root',
                              port=3306,
                              password='',
                              database='Hotel',
                              charset='utf8mb4',
                              autocommit=True,
                              cursorclass=pymysql.cursors.DictCursor
                              )
    cursor = connect.cursor()
    query = '''select * from `keywords` where `flag`=1 and `posted`=0  and `entity_id` <> '' '''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def get_categories():
    connect = pymysql.connect(host='192.81.133.48',
                              user='root',
                              port=3306,
                              password='Warandgal@12',
                              database='hotel',
                              charset='utf8mb4',
                              autocommit=True,
                              cursorclass=pymysql.cursors.DictCursor
                              )

    cursor = connect.cursor()
    query = '''select term_id,name from wp_terms'''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def update_post(index=''):
    connect = pymysql.connect(host='50.116.50.244',
                              user='root',
                              port=3306,
                              password='',
                              database='Hotel',
                              charset='utf8mb4',
                              autocommit=True,
                              cursorclass=pymysql.cursors.DictCursor
                              )

    cursor = connect.cursor()
    query = '''update `keywords` set `posted`=1 where replace(`index`, "'", '')='%s' ''' % index
    cursor.execute(query)
    print('Index %s posted successfully' % index)

def post_in_wp():
    categories = get_categories()
    keywords = get_all_keywords_from_db()
    # domain = 'http://127.0.0.1/wordpress/'
    domain = 'https://www.oregoncaveschateau.com/'
    # url = 'http://127.0.0.1/wordpress/wp-json/wp/v2/posts'
    url = 'https://www.oregoncaveschateau.com/wp-json/wp/v2/posts'
    # url = 'https://www.oregoncaveschateau.com/wp-json/wp/v2/categories'
    # wp_request = requests.get(url, auth=HTTPBasicAuth('greedisgood', 'aOgb vf2u iLzt 9hBR GMN7 CCyk'))
    # print(wp_request.json())
    current_year = datetime.now().year

    for keys in keywords:
        index = keys['index'].replace("\'", '')
        key = keys['key']
        category = key.lower().replace('hotels', '')
        entity_ids = keys['entity_id']
        if entity_ids:
            related_links = get_related_links(keyword=index, city=keys['city'].replace("\'", ''), state=keys['country_code'])
            print('Posting keyword: %s' % index)
            entity_ids = entity_ids.split(',')
            x1 = index.split(',')
            cap = x1[-1].upper()
            join_ = '%s,%s' % (x1[0], cap)
            index = join_.split(' ')
            mylist = list(dict.fromkeys(index))
            keyword = ' '.join(mylist)
            html_body = ['<h2>%s</h2>' % keyword]
            # post_count = len(entity_ids)
            count = 0
            for i, entity_id in enumerate(entity_ids):
                result = get_info_of_hotel(entity_id=entity_id)
                # print(result.get('missing'))
                if result.get('state'):
                    print('Processing entity id: %s' % entity_id)
                    text = post_data_to_wp(result=result['data'])
                    # if text.get('state'):
                    count += 1
                    name = '''<h3>%d. %s </h3>''' % (count, text.get('name'))
                    photos = text.get('photos')
                    details = text.get('details')
                    about = text.get('about')
                    desc = text.get('desc')
                    things_to_know = text.get('things')
                    all_reviews = text.get('reviews')
                    ad_features = text.get('features')
                    ad_options = text.get('options')
                    html_text = text.get('html') % (
                        name, photos, details, about, desc, things_to_know, all_reviews, ad_features, ad_options)
                    html_body.append(html_text)

            like = []
            for links in related_links:
                like.append(
                    '''<li><a href="%s">%d Best %s</a></li>''' % ('%s%s' % (domain, links[0]), links[2], links[1]))
            likes = ''.join(like)
            you_may_also_like = '''<h4>You May Also Like</h4><ul>%s</ul>''' % likes
            html_body = ''.join(
                html_body) + '%s<hr class="wp-block-separator has-alpha-channel-opacity"/>' % you_may_also_like
            if count > 0:
                post_title = "%d Best %s (%d)" % (count, keyword, current_year)
                for cat in categories:
                    if cat['name'].lower() == 'hotel':
                        parent = cat['term_id']
                    if cat['name'].lower() in category and cat['name'].lower() != 'hotel':
                        cat_id = cat['term_id']
                        break
                    else:
                        cat_id = 1
                # print(cat_id)
                post = {'title': post_title,
                        'status': 'publish',
                        'content': html_body,
                        'author': '1',
                        'format': 'standard',
                        'categories': cat_id,
                        'slug': keyword,

                        }
                cc = 0
                while True:
                    try:
                        wp_request = requests.post(url, auth=HTTPBasicAuth('greedisgood', 'aOgb vf2u iLzt 9hBR GMN7 CCyk'),
                                                   json=post)
                        # print(wp_request.json()['id'])
                        if wp_request.status_code == 201:
                            # id_ = wp_request.json()['id']
                            # url = 'https://www.oregoncaveschateau.com/wp-json/wp/v2/categories/{}'.format(id_)
                            # data = {
                            #     'parent': parent
                            # }
                            # wp_request = requests.post(url, auth=HTTPBasicAuth('greedisgood', 'aOgb vf2u iLzt 9hBR GMN7 CCyk'),
                            #                            json=data)
                            # print('Categories Updated.')
                            update_post(index=keys['index'].replace("\'", ''))
                            break
                        else:
                            cc += 1
                            time.sleep(1)
                            print('%s failed to post.' % keyword)
                    except:
                        print('Failed to Post.')
                        break

                    if cc > 5:
                        break
    '''
     #
    # wp_request = requests.post(url, auth=HTTPBasicAuth('anand', '9SQW jcQU ANlV edpu 7RJm qOLg'), json=post)
    # wp_request = requests.get(url, auth=HTTPBasicAuth('anand', '9SQW jcQU ANlV edpu 7RJm qOLg'))
    # print(wp_request)

    '''


if __name__ == "__main__":
    post_in_wp()
