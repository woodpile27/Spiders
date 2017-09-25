import json
import requests
import re
import os
from requests.exceptions import ConnectionError
from urllib.parse import urlencode
from json.decoder import JSONDecodeError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
from config import *

browser = webdriver.Firefox()
wait = WebDriverWait(browser, 10)


def get_album_href():
    try:        
        browser.get('https://y.qq.com/')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.mod_header > div > div.mod_top_search > div.mod_search_input > input")))
        input.clear()
        input.send_keys(SINGER_NAME)
        input.send_keys(Keys.ENTER)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#zhida_singer > div > div.mod_intro__base > h2 > a"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.main > div.mod_data > div > ul > li:nth-child(2) > a"))).click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#album_box > li:nth-child(1) > div > div.playlist__cover.mod_cover > a > img")))
        html = browser.page_source
        doc = pq(html)
        items = doc("#album_box .playlist__item .playlist__item_box").items()
        for item in items:
            yield item.find(".playlist__title a").attr('href')
    except TimeoutException:
        return get_album()


def get_song_href(url):
    try:
        doc = pq(url)
        album_title = doc(".data__name_txt").text()
        os.makedirs(os.path.join("/home/cd/spider/QQmusic/jay_chou", album_title))
        os.chdir("/home/cd/spider/QQmusic/jay_chou/"+album_title)
        print(album_title)
        items = doc(".songlist__list li").items()
        for item in items:
            yield item.find(".songlist__item .songlist__songname_txt a").attr('href')
    except TimeoutException:
        return get_song_href(url)


def get_id(url):
    html = requests.get(url).text
    id_pattern = re.compile(r'var g_SongData = {"songid":(\d+),"songmid', re.S)
    result = re.search(id_pattern, html)
    return result.group(1)


def get_lyric(id):
    data = {
        'nobase64': 1,
        'musicid': id,
        'callback': 'jsonp1',
        'g_tk': 5381,
        'jsonpCallback': 'jsonp1',
        'loginUin': 0,
        'hostUin': 0,
        'format': 'jsonp',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': 0,
        'platform': 'yqq',
        'needNewCode': 0
        }
    params = urlencode(data)
    base = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric.fcg?'
    url = base + params
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.8',
        'cookie': 'pgv_pvi=2039389184; pgv_si=s4352544768; ts_last=y.qq.com/n/yqq/song/003OUlho2HcRHC.html; ts_uid=7915915062',
        'referer': 'https://y.qq.com/n/yqq/song/003OUlho2HcRHC.html',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text[7:-1]
        return None
    except ConnectionError:
        return None


def parse_lyric(text):
    try:
        data = json.loads(text)
        if data and 'lyric' in data.keys():
            lyric = data.get('lyric')
    except JSONDecodeError:
        pass
    pattern = re.compile('(\[.*?])', re.S)
    lyric = re.sub(pattern, '', lyric)
    pattern2 = re.compile(r'(&#\d+;)', re.S)
    lyric = re.sub(pattern2, '\n', lyric)
    return lyric.strip()


def write_to_file(text):
    title = text[:text.find('\n')]
    print('写入中', title)
    with open(title + '.txt', 'w') as f:
        f.write(text)


def main():
    album_urls = get_album_href()
    for url in album_urls:
        song_urls = get_song_href(url)
        for url in song_urls:
            if url:
                url = 'https:' + url
                song_id = get_id(url)
                data = get_lyric(song_id)
                lyric = parse_lyric(data)
                write_to_file(lyric)
            else:
                pass


if __name__ == '__main__':
    main()
