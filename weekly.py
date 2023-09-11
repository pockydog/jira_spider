from jira import JIRA
import xlwt
import re
from tqdm import tqdm
import datetime
from collections import Counter
import pandas as pd


class Jira:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'VickyChen'
    password = '1Q2W3E4R!!!'
    is_this_week = True
    file = '/Users/user/Desktop/jira_spider/JIRA_'
    mapping_file_name = '.xlsx'

    # 排除不需要顯示的狀態列表