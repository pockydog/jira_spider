from jira import JIRA
import xlwt
import re
from tqdm import tqdm
import datetime


class Jira:
    domain = 'http://jira.trevi.cc/'
    account = 'VickyChen'
    password = '1Q2W3E4R!!!'
    block_list = [
        'DebbyChen', 'SashaLin', 'gitlab', 'hanklin',
        'cedric', 'billji', 'PeggyHuang', 'ahrizhou', 'MarsLi'
    ]
    skip_ = ['Planning', '待办', 'Pending']
    block_project_list = [
        'CCUattele', 'CKDT', 'Core', 'Block Chain', 'Lucky Hash',
        'QA-Automation-Group', 'Online Casino Management System', 'release',
        'WT', 'WT-NIU', 'WT_role_integration', 'WT_好路推薦', 'WT_後台顯示各項占成交收',
        'WT_百家樂']
    END_TIME = ' 18:00'

    @classmethod
    def get_member_list(cls, jira):
        members = jira.group_members('TREVI')
        members_list = [member for member in members if member not in Jira.block_list]
        return members_list

    @classmethod
    def by_username(cls, user_worklogs):
        for worklog in user_worklogs:
            a = worklog.timeSpent
            return a

    @classmethod
    def parse_week(cls):
        today = datetime.datetime.today()
        weekday = today.weekday()
        days_to_monday = datetime.timedelta(days=weekday)
        monday = today - days_to_monday
        start = monday.strftime('%Y-%m-%d')
        end = today.strftime('%Y-%m-%d')
        return start, end

    @classmethod
    def get_person_info(cls):
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        members_list = Jira.get_member_list(jira=jira)
        summary = list()
        str_creatd = list()
        link = list()
        priority = list()
        project = list()
        spent_time = list()
        status_list = list()
        user_list = list()
        start, end = Jira.parse_week()
        for user in tqdm(members_list):
            issues = jira.search_issues(
                f'updated > {start} '
                f'AND updated < now()'
                f'AND assignee was {user} OR reporter = {user}'
            )
            for issue in issues:
                status = issue.fields.status.name
                if status not in Jira.skip_:
                    status_list.append(status)
                else:
                    continue
                user_list += [user]
                summary += [issue.fields.summary]
                project += [issue.fields.project.name]

                created = issue.fields.created
                created = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", created)
                str_creatd += ["".join(created)]

                link += [issue.permalink()]
                priority += [issue.fields.priority.name]
                worklogs = jira.worklogs(issue)
                user_worklogs = [worklog for worklog in worklogs if worklog.author.name == user]
                worklogs_ = Jira.by_username(user_worklogs=user_worklogs)
                spent_time.append(worklogs_)

        return summary, user_list, project, priority, str_creatd, status_list, spent_time, link

    @classmethod
    def export_excel(cls):
        summary, user_list, project, priority, str_creatd, status_list, spent_time, link = Jira.get_person_info()
        file = xlwt.Workbook('encoding = utf-8')
        sheet = file.add_sheet(f'jira_', cell_overwrite_ok=True)
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'user_name')
        sheet.write(0, 2, 'project')
        sheet.write(0, 3, 'summary')
        sheet.write(0, 4, 'priority')
        sheet.write(0, 5, 'created')
        sheet.write(0, 6, 'status')
        sheet.write(0, 7, 'user_timespent')
        sheet.write(0, 8, 'link')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, user_list[i])
            sheet.write(i + 1, 2, project[i])
            sheet.write(i + 1, 3, summary[i])
            sheet.write(i + 1, 4, priority[i])
            sheet.write(i + 1, 5, str_creatd[i])
            sheet.write(i + 1, 6, status_list[i])
            sheet.write(i + 1, 7, spent_time[i])
            sheet.write(i + 1, 8, link[i])
        file.save(f'pocky_friday.xls')


if __name__ == '__main__':
    Jira.export_excel()