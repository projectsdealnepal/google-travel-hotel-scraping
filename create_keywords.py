import pandas as pd
import csv
import pymysql


def insert_into_db(values=[]):
    con = pymysql.connect(host='50.116.50.244',
                          user='root',
                          port=3306,
                          password='',
                          database='Hotel',
                          charset='utf8mb4',
                          autocommit=True,
                          cursorclass=pymysql.cursors.DictCursor
                          )
    # print(values)
    if con:
        cursor = con.cursor()
        query = '''insert into `keywords` (`index`, `key`, `city`, `country_code`, `url`, `entity_id`, `flag`) values 
        (%s, %s, %s, %s, %s, %s, %s) '''
        cursor.executemany(query, values)
        print('%d rows inserted.' % cursor.rowcount)
        con.commit()

    else:
        print('Connection Error.')


def get_list_of_urls():
    with open('temp.txt', 'a') as f:
        f.write('Hello \n')


def create_list_of_keywords():
    keywords = []
    list_of_us_cities = []
    with open('hotel keywords.txt', 'r') as f:
        d = f.readlines()
        for line in d:
            keywords.append(line.strip())

    output = []

    with open('US Cities (top 4000).xlsx - Sheet1.csv', 'r') as f:
        data = csv.reader(f)
        for d in data:
            for k in keywords:
                output.append(['%s in %s, %s' % (k, d[1], d[2]), k, d[1], d[2], '', '', 0])
                # output.append({
                #     'index': '%s in %s, %s' % (k, d[1], d[2]),
                #     'key': k,
                #     'city': d[1],
                #     'country_code': d[2],
                #     'url': '',
                #     'entity_id': '',
                #     'flag': 0,
                #
                # })

    # pd.DataFrame(output).to_csv('keywords1.csv', index=None)
    # print(len(output))
    return output


values = create_list_of_keywords()
insert_into_db(values=values)
