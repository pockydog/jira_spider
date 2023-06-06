from jira import JIRA
import xlwt
import re
from tqdm import tqdm
import datetime


class Jira:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'VickyChen'
    password = '1Q2W3E4R!!!'

    # 排除 Trevi group 不需要登記的人員列表
    block_list = [
        'DebbyChen', 'SashaLin', 'gitlab', 'hanklin',
        'cedric', 'billji', 'PeggyHuang', 'ahrizhou', 'MarsLi'
    ]

    # 排除不需要顯示的狀態列表
    skip_ = ['2', '2']

    @classmethod
    def get_member_list(cls, jira):
        """
        取得所有 Trevi 員工資訊, 並移除'目標範圍外'的員工 --->'block_list'
        """
        members = jira.group_members('TREVI')
        members_list = [member for member in members if member not in Jira.block_list]
        return members_list

    @classmethod
    def parse_week(cls):
        """
        取得本週的起始日期
        """
        today = datetime.datetime.today()
        weekday = today.weekday()
        days_to_monday = datetime.timedelta(days=weekday)
        monday = today - days_to_monday
        start = monday.strftime('%Y-%m-%d')
        end = today.strftime('%Y-%m-%d')
        return start, end

    @classmethod
    def get_person_info(cls):
        """
        Main content
        取得相關所需資料
        """
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        members_list = Jira.get_member_list(jira=jira)
        summary = list()
        str_creatd = list()
        link = list()
        priority = list()
        project = list()
        status_list = list()
        user_list = list()
        worklog_list = list()
        start, end = Jira.parse_week()

        for user in tqdm(members_list):
            # 下條件式, 利用JQL
            issues = jira.search_issues(
                f'updated > {start} '
                f'AND updated < now()'
                f'AND (assignee was {user} OR reporter = {user})'
            )
            # 取得資料 解析
            for issue in issues:
                status = issue.fields.status.name
                if status not in Jira.skip_:
                    status_list.append(status)
                else:
                    continue
                worklogs = jira.worklogs(issue)
                worklog_list += [Jira.get_worklog_info(worklogs=worklogs, user=user)]
                user_list += [user]
                summary += [issue.fields.summary]
                project += [issue.fields.project.name]

                created = issue.fields.created
                created = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", created)
                str_creatd += ["".join(created)]

                link += [issue.permalink()]
                priority += [issue.fields.priority.name]

        return summary, user_list, project, priority, str_creatd, status_list, worklog_list, link

    @classmethod
    def get_worklog_info(cls, worklogs, user):
        """
        取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        worklog_list = list()
        week = Jira.parse_week()
        for work in worklogs:
            started = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", work.started)
            str_started = "".join(started)

            if str_started in week:
                # 須將登記時數人員名稱 與 員工列表 資料媒合 且回傳
                parse = str(work.author.name).lower().replace(' ', '')
                if parse == user.lower():
                    info = [f'Time：{work.timeSpent}', f'Name：{work.author.name}']
                    worklog_list.extend(info)

        return worklog_list

    @classmethod
    def parse_worklog_time(cls, worklog_list):
        for w in worklog_list:
            if 'Time:' in w:
                print(w)

    @classmethod
    def parse_week_(cls):
        """
        取得 一週 的 所有時間
        """
        today = datetime.datetime.today()
        week_day = 5
        week = ['20' + datetime.datetime.strftime(today - datetime.timedelta(today.weekday() - i), '%y-%m-%d') for i in
                range(week_day)]
        return week

    @classmethod
    def export_excel(cls):
        """
        匯出 且 存入 excel
        """
        summary, user_list, project, priority, str_creatd, status_list, worklog_list, link = Jira.get_person_info()
        file = xlwt.Workbook('encoding = utf-8')
        sheet = file.add_sheet(f'jira', cell_overwrite_ok=True)
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'user_name')
        sheet.write(0, 2, 'project')
        sheet.write(0, 3, 'summary')
        sheet.write(0, 4, 'priority')
        sheet.write(0, 5, 'created')
        sheet.write(0, 6, 'status')
        sheet.write(0, 7, 'worklog')
        sheet.write(0, 8, 'link')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, user_list[i])
            sheet.write(i + 1, 2, project[i])
            sheet.write(i + 1, 3, summary[i])
            sheet.write(i + 1, 4, priority[i])
            sheet.write(i + 1, 5, str_creatd[i])
            sheet.write(i + 1, 6, status_list[i])
            sheet.write(i + 1, 7, worklog_list[i])
            sheet.write(i + 1, 8, link[i])
        sheet2 = file.add_sheet(f'project', cell_overwrite_ok=True)
        sheet2.write(0, 4, 'worklog')
        for i in range(len(worklog_list)):
            sheet2.write(i + 1, 1, worklog_list[i])



        # excel 檔案名稱
        start, end = Jira.parse_week()
        file.save(f'JIRA_{end}.xls')


# 執行檔
if __name__ == '__main__':
    Jira.export_excel()