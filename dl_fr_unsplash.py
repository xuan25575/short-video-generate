#!/usr/bin/env python
# _*_ coding utf-8 _*_
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import os
from selenium.webdriver.common.keys import Keys    # 模仿键盘,操作下拉框的
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time


def get_browser():
    url = 'https://unsplash.com/t/nature'
    root_path = os.path.abspath(os.path.dirname(__file__))
    # chrome_driver_path = os.path.join(root_path, 'chromedriver.exe')
    # https://registry.npmmirror.com/binary.html?path=chromedriver/
    #chrome_driver_path = os.path.join(root_path, 'chromedriver')  # for mac
    #browser = webdriver.Chrome(executable_path=chrome_driver_path)
    # 尝试传参
    s = Service("/Users/code/py/CreateShortVideo/utils/chromedriver")
    browser = webdriver.Chrome(service=s)
    browser.maximize_window()  # 将页面最大化
    browser.get(url)
    scroll_to_bottom(browser)
    #browser.find_element(By.XPATH, '//input[@class="readerImg"]').send_keys(Keys.DOWN)

    soup = BeautifulSoup(browser.page_source, 'lxml')
    img_class = soup.find_all('div', {"class": "VQW0y Jl9NH"})
    print(img_class)
    i = 0
    for img_list in img_class:
        imgs = img_list.find_all('img')
        for img in imgs:
            src = img['src']
            r = requests.get(src, stream=True)
            image_name = 'unsplash_' + str(i) + '.jpg'
            i += 1
            with open('.././source/img/%s' % image_name, 'wb') as file:
                for chunk in r.iter_content(chunk_size=1024):
                    file.write(chunk)
    return browser


def scroll_to_bottom(driver):
    """控制浏览器自动拉倒底部"""

    js = "return action=document.body.scrollHeight"
    # 初始化现在滚动条所在高度为0
    height = 0
    # 当前窗口总高度
    new_height = driver.execute_script(js)

    index = 0
    while height < new_height:
        # 将滚动条调整至页面底部
        for i in range(height, new_height, 100):
            driver.execute_script('window.scrollTo(0, {})'.format(i))
            time.sleep(0.2)
        height = new_height
        time.sleep(0.1)
        new_height = driver.execute_script(js)
        index += 1
        print(i)
        if index == 100:
            break




def dlimg_from_unsplash(url='https://unsplash.com/t/nature'):
    """
        爬取 https://unsplash.com/t/nature 的图片
    :param url:  地址
    :return: 写出结果
    """
    i = 0
    ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    header = {"User-Agent": ua}
    html = requests.get(url, headers=header)
    soup = BeautifulSoup(html.text, 'lxml')
    img_class = soup.find_all('div', {"class": "VQW0y Jl9NH"})
    print(img_class)
    for img_list in img_class:
        imgs = img_list.find_all('img')
        for img in imgs:
            src = img['src']
            r = requests.get(src, stream=True)
            image_name = 'unsplash_' + str(i) + '.jpg'
            i += 1
            with open('.././source/img/%s' % image_name, 'wb') as file:
                for chunk in r.iter_content(chunk_size=1024):
                    file.write(chunk)

    return


if __name__ == "__main__":
    get_browser()
    #dlimg_from_unsplash()
