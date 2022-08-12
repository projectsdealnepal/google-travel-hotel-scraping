import csv
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
import time
from selenium.webdriver.common.keys import Keys
import re
from lxml import html
from datetime import datetime
import os
import threading


def read_from_file(ratings=4, keyword=''):
    start_time = datetime.now()
    input_params = {
        'driver_path': 'C:\\chromedriver.exe',
        'firefox_path': 'geckodriver.exe',
        'phantom_path': 'C:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe',
        'url': 'https://www.google.com/travel/hotels/search?q=%s' % keyword,
    }
    Firefox = True
    Phantom = False
    Chrome = False
    links = []
    username = 'anand_scraper'
    password = 'Warandgal@12'
    entry = ('http://customer-%s-cc:%s@pr.oxylabs.io:7777' %
             (username, password))
    proxy = {
        'http': entry,
        'https': entry,
    }
    if Firefox:
        options = Options()
        # profile = webdriver.FirefoxProfile()
        options.add_argument("--headless")
        options.add_argument("--disable-notifications")
        # self.driver = webdriver.Firefox(executable_path=input_params['firefox_path'])
        driver = webdriver.Firefox(executable_path=input_params.get('firefox_path'), options=options, proxy=proxy)

    if Chrome:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("user-agent=Hi")
        options.add_argument("--disable-notifications")
        driver = webdriver.Chrome(executable_path=input_params['driver_path'])

    # input_full_xpath = '/html/body/c-wiz[3]/div/div[2]/div/c-wiz/div[2]/div[1]/div/div/div[1]/div/div[1]/div[1]/div/c-wiz/div/div/div/div[2]/div[2]/div/div[2]/input'
    if Phantom:
        driver = webdriver.PhantomJS(executable_path=input_params['phantom_path'])
    driver.get(input_params.get('url'))
    time.sleep(1)
    if ratings:
        rating_path = '/html/body/c-wiz[2]/div/div[2]/div/c-wiz/div[2]/div[1]/div/div/div[1]/div/div[2]/div/div/div/div[2]/div[1]/div/div[3]/span/button'
        rating_button = WebDriverWait(driver, 10).until(
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
        input_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@aria-label="Guest rating"]/div[%d]' % index)))
        input_button.click()
        time.sleep(2)
    try:
        number = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//h1[@id="wKdiD"]')))
    except:
        number = None
    total_hotels = 0
    if number:
        total = re.findall(r'\d+', number.text)
        if total:
            total_hotels = int(''.join(total))
    max_limit = 20
    count = 0
    if total_hotels > 10:
        i = 0
        while True:
            check_date = datetime.now()
            diff_time = (check_date - start_time).total_seconds() / 60  # if greater than 5 mins break
            if diff_time < 5 or count > 5:
                i += 1
                if i < 10:
                    body = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, '//body')))
                    for i in range(3):
                        body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(5)
                    content = driver.page_source
                    links = return_total_links(text=content)
                    n_l = len(links)
                    if n_l > max_limit:
                        break
                    print('Total number of iteration = %d' % i)
                else:
                    driver.refresh()
                    i = 0
                    count += 1
            else:
                break

    filename = os.path.join('data', '%s.txt' % keyword)
    with open(filename, 'w', encoding="utf-8") as f:
        f.write(content)
    driver.close()
    print('Processing keyword %s completed.' % keyword)


def return_total_links(text=''):
    # text = open('search1.txt', 'r').read()
    tree = html.fromstring(text)
    links = tree.xpath('//*/c-wiz/div/a')
    all = []
    for l in links:
        div = l.getparent().get('data-is-promoted')
        if not div:
            href = l.get('data-href')
            if 'entity' in href:
                all.append(href)

    return list(set(all))


class hotel_scraper():
    def __init__(self, ratings=4, keyword='', city='', code=''):
        input_string = '%s, %s, %s' % (keyword, city, code)
        start_time = datetime.now()
        input_params = {
            'driver_path': 'C:\\chromedriver.exe',
            'firefox_path': 'geckodriver.exe',
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
            options = Options()
            # profile = webdriver.FirefoxProfile()
            options.add_argument("--headless")
            options.add_argument("--disable-notifications")
            # self.driver = webdriver.Firefox(executable_path=input_params['firefox_path'])
            self.driver = webdriver.Firefox(executable_path=input_params.get('firefox_path'), options=options, proxy=proxy)

        if Chrome:
            options = Options()
            options.add_argument("--headless")
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

        try:
            number = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//h1[@id="wKdiD"]')))
        except:
            number = None

            # self.driver.refresh()
        total_hotels = 0
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
                    if i < 5:
                        body = WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located((By.XPATH, '//body')))
                        for i in range(3):
                            body.send_keys(Keys.PAGE_DOWN)
                        time.sleep(5)
                        content = self.driver.page_source
                        self.links = self.return_total_links(text=content)
                        n_l = len(self.links)
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

        filename = os.path.join('data', '%s.txt' % input_string)
        with open(filename, 'a', encoding='utf-8') as f:
            for l in self.links:
                f.write('%s, %s\n' % (input_string, l))
            f.close()
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
                if 'entity' in href:
                    all.append(href)

        return list(set(all))


files = os.listdir('data')
n = len(files)
df = pd.read_csv('keywords.csv')
for i in range(len(df)):
    if i > n:
        input_val = df.iloc[i]
        city = input_val['City']
        code = input_val['Code']
        keyword = input_val['Keyword']
        status = input_val['Flag']
        if status == 0:
            key = '%s, %s, %s' % (keyword, city, code)
            print(key)
            # logging.info('Processing Started for keyword %s' % key)
            hot = hotel_scraper(keyword=keyword, city=city, code=code)
            total_links = len(hot.links)
            # logging.info('Total %d links found for %s.' % (total_links, key))
