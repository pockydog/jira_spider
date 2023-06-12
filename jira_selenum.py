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
urls = 'https://jira.trevi.cc/issues/?jql=updated%20%3E%3D%202023-06-01%20AND%20updated%20%3C%3D%202023-06-30'
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
pro = soup.find('li', {'data-id': 'project'}).click()
# condition.send_keys('updated >= 2023-06-01 AND updated <= 2023-06-30')
# driver.implicitly_wait(20)
# driver.find_element('xpath', '//*[@id="main"]/div/div[1]/form/div[1]/div[1]/div[1]/div[2]/button').click()
# driver.get(url=urls)

# page = soup.find('div', {'class': 'pagination'})
# page = page.find_all('a')
# page = [p.get('href') for p in page if p.text != '下一步 >>']
# title_name = list()
# timespend_list = list()
# created_list = list()
# priority_list = list()
# urlss = ['https://jira.trevi.cc' + p for p in page]
# urlss.append(urls)
# print(urlss)
#
#
# for url_ in urlss:
#     driver.get(url=url_)
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     a = soup.find_all('a', {'class': 'issue-link'})
#     test = soup.find_all('a', {'class': 'issue-link'})
#
#
#     # pattern = r'[A-Z]{2}-[0-9]{3}'
#     # pattern_two = r'[A-Z]{2}-[0-9]{2}'
#     # pattern_three = r'G11SLOT001'
#     # pattern_four = r'BAIJIA'
#     # pattern_five = r'QT-[0-9]{2}'
#     # for i in a:
#     #     if i.text == '':
#     #         continue
#     #     if re.match(pattern, i.text):
#     #         continue
#     #     else:
#     #         title_name.append(i.text)
#     b = soup.find_all('td', {'class': 'timespent'})
#     timespend_list += [i.text for i in b]
#     c = soup.find_all('td', {'class': 'created'})
#     created_list += [i.text for i in c]
#     d = soup.find_all('td', {'class': 'priority'})
#
#
# # print(len(title_name))
# # print(len(timespend_list))
# file = xlwt.Workbook('encoding = utf-8')
# sheet = file.add_sheet(f'selenum', cell_overwrite_ok=True)
# sheet.write(0, 0, '')
# sheet.write(0, 1, 'task')
# sheet.write(0, 2, 'timespent')
# sheet.write(0, 3, 'created')
#
# for i in range(len(timespend_list)):
#     sheet.write(i + 1, 0, i)
#     sheet.write(i + 1, 1, timespend_list[i])
#     sheet.write(i + 1, 2, title_name[i])
#     sheet.write(i + 1, 3, created_list[i])
# file.save(f'JIRA_selenum.xls')
