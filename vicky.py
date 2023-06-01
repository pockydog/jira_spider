from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import requests
import json


import time
from selenium.webdriver.common.by import By

# class TestVicky:
#
#     @classmethod
#     def get_page(cls):
#         options = webdriver.ChromeOptions()
#         options.add_experimental_option('detach', True)
#         driver = webdriver.Chrome(options=options)
#         driver.get("https://www.google.com")
# url ='https://m.pgsoft-games.com/74/index.html?l=zh&btt=1&ot=1568a96385dff502c465b940728ce' \
#      '67b&ops=ed8cedd81640e66da2acbf2ed23d6d6e&__refer=m.pg-redirect.net&or=static.pgsoft-games.com&__hv=1fccefd3'

#
options = webdriver.ChromeOptions()
options.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=options)
driver.get(
    'https://m.pgsoft-games.com/74/index.html?l=zh&btt=1&ot=1568a96385dff502c465b940728ce'
    '67b&ops=ed8cedd81640e66da2acbf2ed23d6d6e&__refer=m.pg-redirect.net&or=static.pgsoft-games.com&__hv=1fccefd3')
driver.implicitly_wait(20)
driver.find_element('id', 'ca-button-0').click()
driver.implicitly_wait(20)

driver.find_element('id', '__startedButton').click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
page_source = driver.page_source
soup = BeautifulSoup(page_source)
print(soup.prettify())


