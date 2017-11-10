from urllib.parse import urlencode
import pymongo
import requests
from lxml.etree import XMLSyntaxError
from requests.exceptions import ConnectionError
from pyquery import PyQuery as pq
from config.py import *

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

base_url = 'http://weixin.sogou.com/weixin?'

headers = {
        'Cookie': 'SUV=00141780718C0B7D59455DEE85082481; CXID=1B4E80534D3C11267E64B2D5618624CE; IPLOC=CN3715; SUID=6E66B2772213940A0000000059A571DD; ABTEST=8|1504014815|v1; SNUID=858A599CEBE9BB08502731ABECC94710; weixinIndexVisited=1; sct=2; JSESSIONID=aaaxFGL04BjpOhm8g7i4v; ppinf=5|1504014886|1505224486|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTYlOUYlQjQlRTUlOUUlOUJ8Y3J0OjEwOjE1MDQwMTQ4ODZ8cmVmbmljazoxODolRTYlOUYlQjQlRTUlOUUlOUJ8dXNlcmlkOjQ0Om85dDJsdU83QlUtWEd1Nk0tNWxuOV9ERVBrYzRAd2VpeGluLnNvaHUuY29tfA; pprdig=o0x8_DX619dqni7DQ1KcOQEl1ZuCo0vm7IDAxJqGkcGD5Bi_yYw2EXsmmiUqTbh-0VIlmcdqn57xUWW6kR6lcYpMsvSX3j4_XA0PN_YVbGaxoi47oNTmonUgPbzq1zseZ8ApLAHo7TlcvAY_MjEU5Amx_nqmGPpJ5Ck1MdjEdXs; sgid=29-30506253-AVmlciaYJ0Wbe4q70DsWGhPU; ppmdig=15040148930000008e98e0ebc65516094bf76b49128ae2ff',
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent' :'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
        }

proxy = None


def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def get_html(url, count=1):
    print('Crawing', url)
    print('Trying Count', count)
    global proxy
    if count >= MAX_COUNT:
        print('Tried Too Many Counts')
        return None
    try:
        if proxy:
            proxies = {
                    'http': 'http://' + proxy
            }
            response = requests.get(url, allow_redirects=False, headers=headers, proxies=proxies)
        else:
            response = requests.get(url, allow_redirects=False, headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            #Need Proxy
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using Proxy', proxy)
                return get_html(url)
            else:
                print('Get Proxy Failed')
                return None
    except ConnectionError as e:
        print('Error Occurred', e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url, count)

def get_index(keyword, page):
    data = {
            'query': keyword,
            'type': 2,
            'page': page
        }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html

def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')

def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def parse_detail(html):
    try:
        doc = pq(html)
        title = doc('.rich_media_title').text()
        content = doc('.rich_media_content').text()
        date = doc('#post-date').text()
        nickname = doc('#js_profile_qrcode > div > strong').text()
        wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        return {
            'title': title,
            'content': content,
            'date': date,
            'nickname': nickname,
            'wechat': wechat
        }
    except XMLSyntaxError:
        return None

def save_to_mongo(data):
    if db['articles'].update({'title': date['title']}, {'$set': data}, True):
        print('Saved to Mongo', data['title'])
    else:
        print('Saved to Mongo Failed', data['title'])

def main():
    for page in range(1, 101):
        html = get_index(KEYWORD, page)
        if html:
            article_urls = page_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    print(article_data)
                    if article_data:
                        save_to_mongo(article_data)



if __name__ == '__main__':
    main()







