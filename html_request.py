from requests_html import HTMLSession, HTML
from lxml import html
import re
import csv
import requests
from multiprocessing import Pool, Lock
from proxy_scrape import hotel_scraper

def return_total_links(text=''):
    # soup = BeautifulSoup(text, 'html.parser')
    tree = html.fromstring(text)
    links = tree.xpath('//*/c-wiz/div/a/@data-href')
    all = [l for l in links if 'entity' in l]
    return (len(list(set(all))))


def request_html(keyword=''):
    params = {
        'q': keyword,
        'hl': 'en'
    }
    url = 'https://www.google.com/travel/hotels/search'
    r = HTMLSession()
    resp = r.get(url, params=params)
    count = 0
    htmlx = HTML(html=resp.text)
    found = htmlx.xpath("//h1[@id='wKdiD']")
    no_ = re.findall(r'\d+', found[0].text)
    count = int(''.join(no_))
    text = resp.html.html
    n = return_total_links(text=text)
    print(n)
    iter = 0
    while n <= count:
        resp.html.render(sleep=1, timeout=30, scrolldown=2)
        text = resp.html.html
        n = return_total_links(text=str(text))
        iter += 1
        print('%d iteration. total links % d' % (iter, n))
        if iter > 10:
            break
    with open('search.txt', 'w', encoding='utf-8') as f:
        f.write(str(resp.html.html))
    r.close()



headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'
}


def scrape_proxies_from_spys():
    # json = {
    #     'xx00':'',
    #     'xpp': 5,
    #     'xf1':0,
    #     'xf2': 0,
    #     'xf4': 0,
    #     'xf5':0
    # }
    # response = requests.post(url, proxies=proxy, headers=headers, json=json)
    # print(response.json())
    with open('proxy.txt', 'r') as f:
        data = f.read()
    tree = html.fromstring(data)
    # print(len(tree.xpath(path)))
    path1 = '//*/tr[@class="spy1x"]'
    proxy_ip_list = []
    for p in tree.xpath(path1):
        protocol = []
        for i, td in enumerate(p.xpath('./td')):

            if i == 0:
                ip_add = td.xpath('./font/text()')

            if i == 1:
                protocol = td.xpath('./a/font/text()')

            if i == 3:
                country = td.xpath('./font//text()')

            if i == 5:
                latency = td.xpath('./font/text()')
        protocol = ''.join(protocol)

        if protocol == 'HTTP' or protocol == 'HTTPS':
            proxy_ip_list.append({
                'ip': ''.join(ip_add).strip(),
                'protocol': protocol.strip(),
                'country': ''.join(country).strip(),
                'latency': float(''.join(latency).strip())
            })
    path2 = '//*/tr[@class="spy1xx"]'
    for p in tree.xpath(path2):
        protocol = []
        for i, td in enumerate(p.xpath('./td')):
            if i == 0:
                ip_add = td.xpath('./font/text()')

            if i == 1:
                protocol = td.xpath('./a/font/text()')

            if i == 3:
                country = td.xpath('./font//text()')

            if i == 5:
                latency = td.xpath('./font/text()')
        protocol = ''.join(protocol)
        if protocol == 'HTTP' or protocol == 'HTTPS':
            proxy_ip_list.append({
                'ip': ''.join(ip_add).strip(),
                'protocol': ''.join(protocol).strip(),
                'country': ''.join(country).strip(),
                'latency': float(''.join(latency).strip())
            })

    fieldnames = ['ip', 'protocol', 'country', 'latency']
    with open('proxy_list_us.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(proxy_ip_list)
    print('Completed.')
    # return proxy_ip_list


# hotel_scraper()
# scrape_proxies_from_spys()

