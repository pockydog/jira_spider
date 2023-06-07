from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time

options = webdriver.ChromeOptions()
options.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=options)
driver.get(
    'https://jira.trevi.cc/login.jsp')
driver.implicitly_wait(20)
name = driver.find_element('id', 'login-form-username')
name.send_keys('vickychen')
password = driver.find_element('id', 'login-form-password')
password.send_keys('1Q2W3E4R!!!')
driver.implicitly_wait(20)
login = driver.find_element('id', 'login-form-submit').click()
driver.implicitly_wait(30)
log = driver.find_element('id', 'find_link').click()
driver.implicitly_wait(20)
search = driver.find_element('id', 'issues_new_search_link_lnk').click()
driver.implicitly_wait(20)
condition = driver.find_element('id', 'advanced-search')
condition.send_keys('updated >= 2023-05-29 AND updated <= 2023-07-03')
driver.implicitly_wait(20)
driver.find_element('xpath', '//*[@id="main"]/div/div[1]/form/div[1]/div[1]/div[1]/div[2]/button').click()

