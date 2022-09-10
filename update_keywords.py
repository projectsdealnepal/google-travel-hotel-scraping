import os
import glob
import pandas as pd
import sys
import re
import pymysql


def read_file(filename=''):
    urls = []
    with open(filename, 'r') as f:
        data = f.readlines()
        count = 0
        for d in data:
            if count < 20:
                count += 1
                string = d.strip().split(',')[-1]

                urls.append(string.replace('/entity/', '').strip())
    return urls


def update_list():
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
        cursor = con.cursor()
        query = '''
                        update `keywords` set `entity_id`=%s, `flag`=1 where `index`=%s and `flag`=0
                '''

        # check = '''
        # select * from `keywords` where `index`=%s and `flag`=0
        # '''

        if len(sys.argv) != 0:
            # df = pd.read_csv('keywords_final.csv')
            folder = sys.argv[1]
            for file in glob.glob('%s/*.txt' % folder):
                kb = os.path.getsize(file)
                if kb != 0:
                    # print(file)
                    filename = ''.join(re.findall(r'%s\\(.*).txt' % folder, file))
                    print(filename)
                    string = filename.split(',')
                    city = string[1].strip()
                    code = string[2].strip()
                    keyword = string[0].strip()
                    key = '%s in %s, %s' % (keyword, city, code)
                    entity_ids = read_file(filename=file)
                    entity_id = ','.join(entity_ids)
                    cursor.execute(query, [entity_id, key])
                    print('Key %s updated' % key)
    else:
        print('Could not connect to database.')


update_list()
