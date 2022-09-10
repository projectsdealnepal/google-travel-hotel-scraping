import requests
import pymysql
import json
from multiprocessing import Pool
import os
import shutil
import glob
import random

folder = os.path.join(os.getcwd(), "images")
if not os.path.exists(folder):
    os.makedirs(folder)

MAX = 500000000


def download(params=[]):
    size = 0
    for img in os.listdir(folder):
        name = os.path.join(folder, img)
        size += os.path.getsize(name)
    if True:
        entity_id = params[0]
        count = params[1]
        image_url = params[2]
        otp = params[3]
        print('Processing url %s' % image_url)
        filename = os.path.join(folder, '%s_%d.jpg' % (entity_id, count))
        gs_proxy_addr = 'http://%s:%s@us-1m.geosurf.io:8000' % ('630037+US+630037-%s' % otp, '8135be349')

        proxy = {
            'http': gs_proxy_addr,
            'https': gs_proxy_addr
        }
        count = 0
        while True:
            try:
                res = requests.get(image_url, stream=True, proxies=proxy, timeout=10)
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(res.raw, f)
                break
            except:
                print('Retrying count = %d' % count)
                otp = '93128%d' % random.randint(0, 10)
                gs_proxy_addr = 'http://%s:%s@us-1m.geosurf.io:8000' % ('630037+US+630037-%s' % otp, '8135be349')

                proxy = {
                    'http': gs_proxy_addr,
                    'https': gs_proxy_addr
                }
                count += 1
            if count > 5:
                break
        print('%s image download completed.' % image_url)
        return 1
    else:
        print('Bandwidth Full Utilized.')
        return 0


def pull_images():
    con = pymysql.connect(host='50.116.50.244',
                          user='rmindcambricarox',
                          port=28137,
                          password='WgOfr3G6pF!%7vWy',
                          database='Hotel',
                          charset='utf8mb4',
                          autocommit=True,
                          cursorclass=pymysql.cursors.DictCursor
                          )
    cursor = con.cursor()
    query = '''
            select * from `hotel_info` where `flag`=1 and `img`=0
            '''
    cursor.execute(query)
    result = cursor.fetchall()
    for res in result:
        entity_id = res['entity_id']
        photos = json.loads(res['photos'])
        if photos:
            # fields = []
            count = 0
            for ph in photos:
                count += 1
                otp = '93128%d' % count
                state = download(params=[entity_id, count, ph, otp])
                if state:
                    cursor.execute('''
                    update `hotel_info` set `img`=1 where `entity_id`='%s'
                    ''' % entity_id)

            # with Pool(2) as p:
            #     p.map(download, fields)


pull_images()
