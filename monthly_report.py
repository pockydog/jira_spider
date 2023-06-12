from jira import JIRA
import xlwt
import re
from tqdm import tqdm
import calendar
import datetime
from datetime import date, timedelta, datetime
import re


class Jira:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'VickyChen'
    password = '1Q2W3E4R!!!'
    black_list = ['UT', 'WTROLE', 'LH', 'OCMS']

    @classmethod
    def get_product_name(cls, jira):
        info = jira.projects()
        info_list = list()
        for i in info:
            if i.key in Jira.black_list:
                continue
            else:
                info_list.append(i.key)
        return info_list

    @classmethod
    def parse_month(cls):
        today = date.today()
        day = calendar.monthrange(today.year, today.month)[1]
        last_day = today.replace(day=day)
        month = f'0{today.month}'
        year = today.year
        return year, month, last_day

    @classmethod
    def get_all_month(cls):
        month = datetime.now().month
        year = datetime.now().year
        number_of_days = calendar.monthrange(year, month)[1]
        first_date = date(year, month, 1)
        last_date = date(year, month, number_of_days)
        delta = last_date - first_date

        return [(first_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]

    @classmethod
    def get_person_info(cls):
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        project_list = Jira.get_product_name(jira=jira)
        year, month, last_day = Jira.parse_month()
        time_list = list()
        summary = list()
        str_creatd = list()
        link = list()
        priority = list()
        status = list()
        name_list = list()
        for project in tqdm(project_list):
            issues = jira.search_issues(
                f'project = {project} AND updated >= 2023-06-01 AND updated <= 2023-06-30'
                # f'project = {project}'
                # f'AND updated >= 2023-06-01 '
                # f'AND updated <= 2023-06-30'
            )
            # 取得資料 解析
            for issue in issues:
                name_list += [project]
                status += [issue.fields.status]
                summary += [issue.fields.summary]
                created = issue.fields.created
                created = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", created)
                str_creatd += ["".join(created)]
                link += [issue.permalink()]
                priority += [issue.fields.priority.name]

                worklogs = jira.worklogs(issue)
                time_list += [Jira.get_worklog_info(worklogs=worklogs)]
        return name_list, summary, priority, str_creatd, time_list, link

    @classmethod
    def get_worklog_info(cls, worklogs):
        worklog_list = list()
        for work in worklogs:
            if work.timeSpent in Jira.get_all_month():
                info = [f'Time：{work.timeSpent}']
            else:
                continue
            worklog_list.extend(info)

        return worklog_list

    @classmethod
    def export_excel(cls):
        """
        匯出 且 存入 excel
        """
        name_list, summary, priority, str_creatd, time_list, link = Jira.get_person_info()
        file = xlwt.Workbook('encoding = utf-8')
        sheet = file.add_sheet(f'jira_M', cell_overwrite_ok=True)
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'name')
        sheet.write(0, 2, 'summary')
        sheet.write(0, 3, 'priority')
        sheet.write(0, 4, 'created')
        sheet.write(0, 5, 'worklog')
        sheet.write(0, 6, 'link')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, name_list[i])
            sheet.write(i + 1, 2, summary[i])
            sheet.write(i + 1, 3, priority[i])
            sheet.write(i + 1, 4, str_creatd[i])
            sheet.write(i + 1, 5, time_list[i])
            sheet.write(i + 1, 6, link[i])
        # excel 檔案名稱
        file.save(f'Month_.xls')


if __name__ == '__main__':
    Jira.export_excel()
