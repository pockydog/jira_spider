import requests
from lxml import html
from bs4 import BeautifulSoup as bs


domain = 'http://jira.trevi.cc/'
account = 'VickyChen'
password = '1Q2W3E4R!!!'
session_requests = requests.session()
result = session_requests.get(domain)
tree = html.fromstring(result.text)
authenticity_token = list(set(tree.xpath('//input[@name="csrfmiddlewaretoken"]/@value')))[0]

