from jira import JIRA
import xlwt

import pandas as pd

from openpyxl import load_workbook


import re


class Jira:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'VickyChen'
    password = '1Q2W3E4R!!!'
    is_this_week = False
    next = True
    Round = 10
    name = 'Trevi_3D輪盤'
    file = f'/Users/user/Desktop/jira_spider/'
    mapping_file_name = '.xlsx'

    # 排除不需要顯示的狀態列表

    sprint_num = 2

    @classmethod
    def parse_query_info(cls):
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        sprints = Jira.Round
        summary = list()
        position = list()
        status = list()
        sprint_list = list()
        for sprint in range(sprints+1):
            query = f'project="3D 輪盤" and sprint = "{sprint}"'
            sprint_items = jira.search_issues(query, maxResults=0)
            for i in sprint_items:
                position += [Jira.parse_issue(summary=i.fields.summary)]
                summary += [Jira.parse_issues(summary=i.fields.summary)]
                status += [i.fields.status.name]
                sprint_list += [str(sprint)]

        query = f'project = "3D 輪盤"'
        sprint_items = jira.search_issues(query, maxResults=0)
        for issue in sprint_items:
            if issue.fields.summary in summary:
                continue
            else:
                position.append(Jira.parse_issue(summary=issue.fields.summary))
                summary.append(Jira.parse_issues(summary=issue.fields.summary))
                status.append(issue.fields.status.name)
                sprint_list.append('BackLog')

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
        result = []
        dictionary = Jira.test_info()
        for value in dictionary:
            position, sprint, status = value['position'], value['sprint'], value['status']
            existing_dict = next((item for item in result if item['position'] == position and item['sprint'] == sprint),
                                 None)

            if existing_dict:
                existing_dict[status] = existing_dict.get(status, 0) + 1
            else:
                new_dict = {'position': position, 'sprint': sprint, 'DONE': 0, 'TO DO': 0, '处理中': 0}
                new_dict[status] = 1
                result.append(new_dict)
            for entry in result:
                total = entry['DONE'] + entry['TO DO'] + entry['处理中']
                entry['total'] = total
        # df = pd.read_excel('Trevi_3D輪盤.xlsx')
        # with pd.ExcelWriter('Trevi_3D輪盤.xlsx') as writer:
        #     df.to_excel(writer, sheet_name='Sheet1', index=False, header=True)

        writer = pd.ExcelWriter('Trevi_3D輪盤.xlsx')
        df = pd.DataFrame(result)
        # df.to_excel(writer, f'Trevi_3D輪盤.xlsx', 'counter1', index=False)
        df.to_excel(writer, 'counter1', index=False, startrow=1)
        writer.close()

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
        sheet = file.add_sheet(f'3D輪盤')
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'position')
        sheet.write(0, 2, 'summary')
        sheet.write(0, 3, 'sprint')
        sheet.write(0, 4, 'status')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, position[i])
            sheet.write(i + 1, 2, summary[i])
            sheet.write(i + 1, 3, sprint_list[i])
            sheet.write(i + 1, 4, status[i])

        file.save(f'Trevi_3D輪盤.xlsx')

    @classmethod
    def export(cls):
        Jira.export_excel()
        Jira.calculate_result()


if __name__ == '__main__':
    Jira.export()
