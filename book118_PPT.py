from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

import base64
import time
import sys
import os
import shutil
from tqdm import trange
from img2pdf import conpdf
from PIL import Image


def download(url, callback):
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('log-level=3')
    driver = webdriver.Chrome(chrome_options=option)

    title = "output"
    try:
        driver.set_page_load_timeout(15)
        driver.get(url)
        title = driver.title
    except:
        return False, "下载失败，超时"

    print(f'原创力: 《{title}》')
    if os.path.exists(f'./output/{title}.pdf'):
        return True, title
    time.sleep(5)

    try:
        # 展开全部
        elem_cont_button = driver.find_element_by_id("agree_full")
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", elem_cont_button)
        actions = ActionChains(driver)
        actions.move_to_element(elem_cont_button).perform()
        time.sleep(0.5)
        elem_cont_button.click()
        # time.sleep(10)
    except NoSuchElementException:
        pass

    try:
        frame = driver.find_element_by_id('layer_view_iframe')
        src = frame.get_attribute('src')
        print(src)

        driver.get(src)
        time.sleep(5)

        if os.path.exists(f'./temp/{title}'):
            shutil.rmtree(f'./temp/{title}')
        os.makedirs(f'./temp/{title}')

        pageCount = int(driver.find_element_by_id(
            'PageCount').get_attribute('innerHTML'))
        for i in trange(pageCount):
            callback(i, pageCount, "正在下载：%s" % title)
            driver.save_screenshot(f'temp/{title}/capture.png')
            page = driver.find_element_by_id('ppt')

            left = page.location['x']
            top = page.location['y']
            right = left + page.size['width']
            bottom = top + page.size['height'] - 35

            im = Image.open(f'temp/{title}/capture.png')
            im = im.crop((left, top, right, bottom))  # 元素裁剪
            im.save(f'temp/{title}/{i}.png')  # 元素截图
            driver.find_element_by_id('pageNext').click()
            time.sleep(1)  # 防止还没加载出来
        os.remove(f'./temp/{title}/capture.png')
        driver.quit()
        callback(99, 100, "正在转码")
        print('下载完毕，正在转码')
        conpdf(f'output/{title}.pdf', f'temp/{title}', '.png')
        return True, title
    except Exception as e:
        return False, e

if __name__ == '__main__':
    download("https://max.book118.com/html/2019/1002/8052020057002053.shtm")
