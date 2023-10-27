import time

from jira import JIRA
import xlwt

import pandas as pd
import time

import re

"""
給 oscar 針對項目的sprint 進度條
"""


class Jira:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'VickyChen'
    password = '1Q2W3E4R!!!'
    is_this_week = False
    next = True
    Round = 10
    project_name = '3D 輪盤'
    file = f'//'
    mapping_file_name = '.xlsx'
    type_ = '子任务'


    @classmethod
    def parse_query_info(cls):
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        sprints = Jira.Round
        summary = list()
        position = list()
        status = list()
        sprint_list = list()
        test_list =list()

        # boards = jira.boards(98)
        # print(boards)

        for sprint in range(sprints + 1):
            query = f'project="{Jira.project_name}" and sprint = "{sprint}"'
            sprint_items = jira.search_issues(query, maxResults=0)
            for i in sprint_items:
                if i.fields.issuetype.name == Jira.type_:
                    continue
                position += [Jira.parse_issue(summary=i.fields.summary)]
                summary += [Jira.parse_issues(summary=i.fields.summary)]
                status += [i.fields.status.name]
                sprint_list += [int(sprint)]
                test_list += [i.fields.issuetype.name]

        return summary, sprint_list, status, position

    @classmethod
    def test_info(cls):
        summary, sprint_list, status, position = Jira.parse_query_info()
        info_list = list()
        for i in range(len(summary)):
            result = {
                'position': position[i],
                'sprint': sprint_list[i],
                'status': status[i]
            }
            info_list.append(result)

        return info_list

    @classmethod
    def calculate_result(cls):
        result = list()
        sprint_list = list()
        dictionary = Jira.test_info()
        for value in dictionary:
            position, sprint, status = value['position'], value['sprint'], value['status']
            existing_dict = next((item for item in result if item['position'] == position and item['sprint'] == sprint),
                                 None)
            sprint_list.append(sprint)

            if existing_dict:
                existing_dict[status] = existing_dict.get(status, 0) + 1
            else:
                new_dict = {'position': position, 'sprint': sprint, 'DONE': 0, 'TO DO': 0, '处理中': 0}
                new_dict[status] = 1
                result.append(new_dict)
            for entry in result:
                total = entry['DONE'] + entry['TO DO'] + entry['处理中']
                entry['total'] = total

        df = pd.DataFrame(result)
        df.to_excel(f'Trevi_{Jira.project_name}_calculate_result{Jira.mapping_file_name}', 'counter1', index=False,
                    startrow=1)

    @classmethod
    def parse_issues(cls, summary):
        pattern = r'\【(.*?)\】'
        result = re.sub(pattern, '', summary)
        return result

    @classmethod
    def parse_issue(cls, summary):
        """
        :param text:
        :return:【原畫】
        """
        pattern = r'【(.*?)】'
        matches = re.search(pattern, summary)
        if not matches:
            return '會議'
        return matches.group(0)

    @classmethod
    def export_excel(cls):
        """
        匯出 且 存入 excel
        """
        summary, sprint_list, status, position = Jira.parse_query_info()
        file = xlwt.Workbook('encoding = utf-8')
        sheet = file.add_sheet(f'{Jira.project_name}')
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'position')
        sheet.write(0, 2, 'summary')
        sheet.write(0, 3, 'sprint')
        sheet.write(0, 6, 'status')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, position[i])
            sheet.write(i + 1, 2, summary[i])
            sheet.write(i + 1, 3, sprint_list[i])
            sheet.write(i + 1, 6, status[i])

        file.save(f'Trevi_{Jira.project_name}{Jira.mapping_file_name}')

    @classmethod
    def exec(cls):
        # Jira.export_excel()
        Jira.calculate_result()


if __name__ == '__main__':
    Jira.exec()
