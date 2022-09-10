import pymysql
import re


def update_checkin_time():
    con = pymysql.connect(host='50.116.50.244',
                          user='root',
                          port=3306,
                          password='',
                          database='Hotel',
                          charset='utf8mb4',
                          autocommit=True,
                          cursorclass=pymysql.cursors.DictCursor
                          )
    cursor = con.cursor()
    query = '''
            select * from `hotel_info` where `checkin`=''
            '''
    cursor.execute(query)
    rows = cursor.fetchall()
    query = '''
    update `hotel_info` set `checkin`=%s, `checkout`=%s where `entity_id`=%s
    '''
    for r in rows:
        if r['desc']:
            checkin = ''
            if 'Check-in time' in r['desc']:
                checkin = re.findall(r'Check-in time: (.*)Check-out', r['desc'])
                if checkin:
                    checkin = ''.join(checkin).strip()
                else:
                    checkin = re.findall(r'Check-in time: (.*)', r['desc'])
                    checkin = ''.join(checkin).strip()

            checkout = ''
            if 'Check-out time' in r['desc']:
                checkout = re.findall(r'Check-out time: (.*)', r['desc'])
                if checkout:
                    checkout = ''.join(checkout).strip()

            if checkin or checkout:
                cursor.execute(query, (checkin, checkout, r['entity_id']))
                con.commit()
                print('Entity ID : %s updated' % r['entity_id'])


update_checkin_time()
