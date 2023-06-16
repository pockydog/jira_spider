from selenium import webdriver
import time
import requests
import xlwt
import re


from bs4 import BeautifulSoup


options = webdriver.ChromeOptions()
options.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=options)
url = 'https://jira.trevi.cc/login.jsp'
urls = 'https://jira.trevi.cc/issues/?jql=updated%20%3E%3D%202023-06-12%20AND%20updated%20%3C%3D%20now()'
url_list = ['&startIndex=50', '&startIndex=100', '&startIndex=150', '&startIndex=200', '&startIndex=250']
driver.get(url=url)
driver.implicitly_wait(20)
name = driver.find_element('id', 'login-form-username')
name.send_keys('vickychen')
password = driver.find_element('id', 'login-form-password')
driver.implicitly_wait(20)

password.send_keys('1Q2W3E4R!!!')
driver.implicitly_wait(20)
login = driver.find_element('id', 'login-form-submit').click()
driver.implicitly_wait(30)
log = driver.find_element('id', 'find_link').click()
driver.implicitly_wait(20)
search = driver.find_element('id', 'issues_new_search_link_lnk').click()
driver.implicitly_wait(20)
condition = driver.find_element('id', 'advanced-search')
driver.implicitly_wait(20)
soup = BeautifulSoup(driver.page_source, 'html.parser')
condition.send_keys('updated >= 2023-06-12 AND updated <= now()')
driver.implicitly_wait(20)
driver.find_element('xpath', '//*[@id="main"]/div/div[1]/form/div[1]/div[1]/div[1]/div[2]/button').click()
driver.get(url=urls)
driver.implicitly_wait(20)
a = soup.find_all('a', {'class': 'issue-link'})
print(a)







