import csv
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
import time
import pymysql
from selenium.webdriver.common.keys import Keys
import re
from lxml import html
from datetime import datetime
import os
import threading
import random


class hotel_scraper():
    def __init__(self, ratings=4, keyword='', city='', code='', windows=True):
        input_string = '%s, %s, %s' % (keyword, city, code)
        start_time = datetime.now()
        # path = os.path.join(os.getcwd(), 'geckodriver.exe')
        input_params = {
            'driver_path': r'/usr/local/bin/chromedriver' if not windows else 'chromedriver.exe',
            'firefox_path': r'/usr/local/bin/geckodriver' if not windows else 'geckodriver.exe',
            'phantom_path': 'C:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe',
            'url': 'https://www.google.com/travel/hotels/search?q=%s' % input_string,
        }
        Firefox = True
        Phantom = False
        Chrome = False
        self.links = []
        username = 'anand_scraper'
        password = 'Warandgal@12'
        entry = ('http://customer-%s-cc:%s@pr.oxylabs.io:7777' %
                 (username, password))
        proxy = {
            'http': entry,
            'https': entry,
        }
        if Firefox:
            # binary = FirefoxBinary(input_params.get('firefox_path'))
            options = Options()
            # profile = webdriver.FirefoxProfile()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            # self.driver = webdriver.Firefox(firefox_binary=binary, options=options)
            self.driver = webdriver.Firefox(executable_path=input_params.get('firefox_path'), options=options)

        if Chrome:
            options = Options()
            options.add_argument("--headless")
            options.add_argument('--no-sandbox')
            options.add_argument("user-agent=Hi")
            options.add_argument("--disable-notifications")
            self.driver = webdriver.Chrome(executable_path=input_params['driver_path'])

        input_full_xpath = '/html/body/c-wiz[3]/div/div[2]/div/c-wiz/div[2]/div[1]/div/div/div[1]/div/div[1]/div[1]/div/c-wiz/div/div/div/div[2]/div[2]/div/div[2]/input'
        if Phantom:
            self.driver = webdriver.PhantomJS(executable_path=input_params['phantom_path'])
        self.driver.get(input_params.get('url'))
        time.sleep(1)
        if ratings:
            rating_path = '/html/body/c-wiz[2]/div/div[2]/div/c-wiz/div[2]/div[1]/div/div/div[1]/div/div[2]/div/div/div/div[2]/div[1]/div/div[3]/span/button'
            rating_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, rating_path)))
            rating_button.click()
            time.sleep(1)
            if ratings == 3:
                index = 2
            elif ratings == 4:
                index = 3
            elif ratings == 5:
                index = 4
            else:
                index = 1
            input_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@aria-label="Guest rating"]/div[%d]' % index)))
            input_button.click()
            time.sleep(3)

        total_hotels = 20
        try:
            number = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//h1[@id="wKdiD"]')))
        except:
            number = None

            # self.driver.refresh()

        if number:
            total = re.findall(r'\d+', number.text)
            if total:
                total_hotels = int(''.join(total))
        max_limit = 20
        count = 0
        if total_hotels > 10:
            i = 0
            while True:
                # check_date = datetime.now()
                # diff_time = (check_date - start_time).total_seconds() / 60  # if greater than 5 mins break
                # if diff_time < 5:
                i += 1
                # print(i)
                if i < 5:
                    body = WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, '//body')))
                    for k in range(3):
                        body.send_keys(Keys.PAGE_DOWN)
                        time.sleep(1)
                    time.sleep(4)
                    content = self.driver.page_source
                    # print(content)
                    self.links = self.return_total_links(text=content)
                    n_l = len(self.links)
                    print(n_l)
                    if n_l > max_limit or n_l >= total_hotels:
                        break
                    print('Total number of iteration = %d' % i)
                else:
                    break
                    # self.driver.refresh()
                    # i = 0
                    # count += 1
            # else:
            #     break

        # filename = os.path.join('data1', '%s.txt' % input_string)
        # with open(filename, 'a', encoding='utf-8') as f:
        #     for l in self.links:
        #         f.write('%s, %s\n' % (input_string, l))
        #     f.close()
        # with open(filename, 'w', encoding="utf-8") as f:
        #     f.write(content)
        self.driver.close()

    def return_total_links(self, text=''):
        tree = html.fromstring(text)
        links = tree.xpath('//*/c-wiz/div/a')
        all = []
        for l in links:
            div = l.getparent().get('data-is-promoted')
            if not div:
                href = l.get('data-href')
                if href:
                    if 'entity' in href:
                        all.append(href)

        return list(set(all))


def pull_from_csv():
    files = os.listdir('data1')
    n = len(files)
    df = pd.read_csv('keywords1.csv')
    for i in range(len(df)):
        if i > n:
            input_val = df.iloc[i]
            city = input_val['City']
            code = input_val['Code']
            keyword = input_val['Keyword']
            status = input_val['Flag']
            if status == 0:
                key = '%s in %s, %s' % (keyword, city, code)
                print('%d. %s' % (i, key))
                # logging.info('Processing Started for keyword %s' % key)

                for retry in range(5):
                    try:
                        hot = hotel_scraper(keyword=keyword, city=city, code=code)
                        total_links = len(hot.links)

                        break
                    # logging.info('Total %d links found for %s.' % (total_links, key))
                    except Exception as e:
                        print(str(e))
                        time.sleep(5)


def pull_from_database():
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
    query = '''
    select * from `keywords` where `flag`=0 and `run_from`=2
    '''
    cursor.execute(query)
    results = cursor.fetchall()

    i = 0
    print(len(results))
    for res in results:
        i += 1
        city = res['city']
        code = res['country_code']
        keyword = res['key']
        key = '%s in %s, %s' % (keyword, city, code)
        print('%d. %s' % (i, key))

        # logging.info('Processing Started for keyword %s' % key)
        for retry in range(5):
            try:
                hot = hotel_scraper(keyword=keyword, city=city, code=code)
                total_links = len(hot.links)
                all_links = []
                for link in hot.links[:20]:
                    all_links.append(link.replace('/entity/', '').strip())
                hotel_link = all_links
                all_links = ','.join(all_links)
                # ran_from = random.randint(1,7)
                insert_query = '''
                update `keywords` set `entity_id`=%s, `flag`=1 where `index`=%s
                '''
                insert_into_hotel = '''
                insert into `hotel_info` (`entity_id`, `flag`, `keyword`) values (%s,%s,%s)
                '''
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
                cursor.execute(insert_query, [all_links, key])
                con.commit()
                print('%s updated.' % key)
                for link in hotel_link:
                    try:
                        cursor.execute(insert_into_hotel, (link, 0, key))
                    except:
                        pass
                break
            # logging.info('Total %d links found for %s.' % (total_links, key))
            except Exception as e:
                print(str(e))
                time.sleep(5)

    #


pull_from_database()
