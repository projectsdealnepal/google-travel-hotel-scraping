import pymysql
import json
import re


def update_hotel_info():
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
    select * from `hotel_info` where `flag`=1
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    c = 0
    for result in results:
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

            if not top_things:
                state = False
                missing.append('Top things Missing.')

            if state:
                query = '''
                update `hotel_info` set `success`=1 where `entity_id`='%s'
                ''' % result['entity_id']
                cursor.execute(query)
                c += 1
                print('%d. Update entity id %s' % (c, result['entity_id']))


update_hotel_info()