from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq

browser = webdriver.Firefox()
wait = WebDriverWait(browser, 60)


def search():
    try:
        browser.get('http://www.dangdang.com/20170822_cloths')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#key_S")))
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#form_search_new > input.button")))
        input.send_keys('python')
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="12810"]/div[5]/div[2]/div/ul/li[9]/a')))
        get_products()
        return total.text
    except TimeoutException:
        return search()


def next_page(page_number):
    print('正在翻页', page_number)
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#t__cp")))
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#click_get_page")))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, "current"), str(page_number)))
        get_products()
    except TimeoutException:
        next_page(page_number)


def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search_nature_rg .bigimg li")))
    html = browser.page_source
    doc = pq(html)
    items = doc("#search_nature_rg .bigimg li").items()
    for item in items:
        product = {
                'image': item.find('.pic img').attr('data-original'),
                'title': item.find('.name a').attr('title'),
                'price': item.find('.price .search_now_price').text(),
                'author': item.find('.search_book_author span a').attr('title'),
                'data': item.find('.search_book_author span:nth-child(2)').text(),
                'think': item.find('.search_star_line .search_comment_num').text()
                }
        print(product)


def main():
    try:
        total = int(search())
        for i in range(2, total + 1):
            next_page(i)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
