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
    is_this_week = False
    next = True

    file = '/Users/user/Desktop/jira_spider/JIRA_'
    mapping_file_name = '.xlsx'

    # 排除不需要顯示的狀態列表
    Status_list = ['本週完成項目', '本週未完成項目', '下週目標']

    sprint_num = 2
    error_list = ['龍商家管理']

    @classmethod
    def get_project_info(cls, jira):
        """
       Get project name to query
        """
        projects = jira.projects()
        name_list = [project.name for project in projects if project.name not in Jira.error_list]
        id_list = [project.id for project in projects]

        return name_list, id_list

    @classmethod
    def test_(cls):
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        boards = jira.boards()
        # for board in boards:
        #     print(f"Board ID: {board.id}, Name: {board.name}")
        sprint = jira.sprint(93)
        print(sprint)

        # jql_query = 'Sprint is not EMPTY'
        # issues = jira.search_issues(jql_query)
        # print(issues)
        #  不可以用因為沒有開啟衝刺

    @classmethod
    def parse_query_info(cls):
        project_list = list()
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        # project_name, project_id = Jira.get_project_info(jira=jira)
        query = f'project="3D 輪盤" and sprint="{Jira.sprint_num}"'

        # Jira.get_info(jira=jira, query=query, next=Jira.next)
        sprint_items = jira.search_issues(query)
        for issue in sprint_items:
            if issue.fields.status.name == 'Done':
                result = {
                    '本週完成項目': issue.fields.summary,
                }
                project_list.append(result)
            if issue.fields.status.name == 'TO DO':
                result = {
                    '進行中未完成項目': issue.fields.summary,
                }
                project_list.append(result)

        query = f'project="3D 輪盤" and sprint="{Jira.sprint_num+1}"'
        sprint_items = jira.search_issues(query)
        for issue in sprint_items:
            result = {
                '下週預計完成項目': issue.fields.summary,
            }
            project_list.append(result)

        df = pd.DataFrame(project_list)
        df.to_excel(f'3D輪盤.xlsx', f'sprint{Jira.sprint_num}', index=False)

        return project_list

    @classmethod
    def parse_info(cls):
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        project_name, project_id = Jira.get_project_info(jira=jira)
        for project in project_name:
            project_list = list()
            query = f'project="{project}" and sprint="{Jira.sprint_num}"'
            try:
                sprint_items = jira.search_issues(query)
            except Exception:
                continue
            for issue in sprint_items:
                if issue.fields.status.name == 'Done':
                    result = {
                        'name': project,
                        '本週完成項目': issue.fields.summary,
                     }
                    project_list.append(result)
                if issue.fields.status.name == 'TO DO':
                    result = {
                        'name': project,
                        '進行中未完成項目': issue.fields.summary,
                    }
                    project_list.append(result)

            for issue in sprint_items:
                result = {
                    'name': project,
                    '下週預計完成項目': issue.fields.summary,
                }
                project_list.append(result)

                df = pd.DataFrame(project_list)

                df.to_excel(f'{project}.xlsx', 'test', index=False)


if __name__ == '__main__':
    Jira.parse_query_info()
