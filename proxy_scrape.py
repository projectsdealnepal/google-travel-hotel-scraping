from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.keys import Keys
import re
from lxml import html
from datetime import datetime


def read_from_file():
    text = open('search1.txt', 'r').read()
    tree = html.fromstring(text)
    links = tree.xpath('//*/c-wiz/div/a/@data-href')
    all = [l for l in links if 'entity' in l]
    return (len(list(set(all))))


class hotel_scraper():
    def __init__(self, ratings=4, keyword=''):
        start_time = datetime.now()
        input_params = {
            'driver_path': 'C:\\chromedriver.exe',
            'firefox_path': 'geckodriver.exe',
            'phantom_path': 'C:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe',
            'url': 'https://spys.one/free-proxy-list/US/',
        }
        Firefox = True
        Phantom = False
        Chrome = False
        self.links = []
        url = 'https://spys.one/free-proxy-list/US/'
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
            self.driver = webdriver.Firefox(executable_path=input_params.get('firefox_path'), proxy=proxy)

        if Chrome:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("user-agent=Hi")
            options.add_argument("--disable-notifications")
            self.driver = webdriver.Chrome(executable_path=input_params['driver_path'])

        if Phantom:
            self.driver = webdriver.PhantomJS(executable_path=input_params['phantom_path'])
        self.driver.get(input_params.get('url'))
        time.sleep(1)
        content = self.driver.page_source
        with open('proxy.txt', 'w', encoding="utf-8") as f:
            f.write((content))
        self.driver.close()

    def return_total_links(self, text=''):
        tree = html.fromstring(text)
        links = tree.xpath('//*/c-wiz/div/a/@data-href')
        all = [l for l in links if 'entity' in l]
        return list(set(all))


# hotel_scraper()