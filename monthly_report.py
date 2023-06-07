from jira import JIRA
import xlwt
import re
from tqdm import tqdm
import calendar
import datetime
from datetime import timedelta


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

    # @classmethod
    # def parse_month(cls):
    #     now = datetime.datetime.now()
    #     print(now.month)
    #     start = datetime.datetime(now.year, now.month, 1)
    #     end = datetime.datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1])
    #     return start, end

    @classmethod
    def get_person_info(cls):
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        project_list = Jira.get_product_name(jira=jira)
        time_list = list()
        summary = list()
        str_creatd = list()
        link = list()
        priority = list()
        status = list()
        name_list = list()
        for project in tqdm(project_list):
            issues = jira.search_issues(
                f'project = {project} AND updated >= 2023-05-01 AND updated <= 2023-05-31'
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
            info = [f'Time：{work.timeSpent}']
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
        sheet.write(0, 1, 'summary')
        sheet.write(0, 2, 'priority')
        sheet.write(0, 3, 'created')
        sheet.write(0, 5, 'worklog')
        sheet.write(0, 6, 'link')
        sheet.write(0, 7, 'name')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, summary[i])
            sheet.write(i + 1, 2, priority[i])
            sheet.write(i + 1, 3, str_creatd[i])
            sheet.write(i + 1, 4, time_list[i])
            sheet.write(i + 1, 5, link[i])
            sheet.write(i + 1, 6, name_list[i])
        # excel 檔案名稱
        file.save(f'Month_.xls')


if __name__ == '__main__':
    print(Jira.export_excel())
    # print(Jira.export_excel())
