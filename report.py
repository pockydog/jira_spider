from jira import JIRA
from tqdm import tqdm
import pandas as pd
from Tool.week_tool import TimeTool


class Jira:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'Vicky.C'
    password = '1Q2W3E4R!!!'
    is_this_week = False
    file = '/Users/user/Desktop/jira_spider/JIRA_'
    mapping_file_name = '.xlsx'

    @classmethod
    def get_person_info(cls, this_week):
        """
        Main content
        取得相關所需資料
        """
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        info_list = list()

        start, end = TimeTool.new_parse_week(this_week=this_week)
        # 下條件式, 利用JQL
        issues = jira.search_issues(f'updated >= {start} AND updated <= now()', maxResults=0)
        # 取得資料 解析
        for issue in tqdm(issues):
            worklogs = jira.worklogs(issue)
            time_list = Jira.get_worklog_info(worklogs=worklogs, this_week=this_week)
            if time_list is []:
                continue
            status = issue.fields.status.name
            link = issue.permalink()
            user_list = Jira.get_worklog_info(time=False, worklogs=worklogs, this_week=this_week)
            summary = issue.fields.summary
            project_list = issue.fields.project.name
            result = {
                'project': project_list,
                'summary': summary,
                'time': time_list,
                'user': user_list,
                'status': status,
                'link': link
            }
            user_values = result['user']
            time_values = result['time']

            for user, time in zip(user_values, time_values):
                dictionary = {
                    'project': result['project'],
                    'summary': result['summary'],
                    'user': user,
                    'time': f'={Jira.compute_cost(sp_time=time)}',
                    'status': result['status'],
                    'link': result['link']
                }
                info_list.append(dictionary)
        Jira.to_excel(info=info_list, this_week=this_week)

    @classmethod
    def get_worklog_info(cls, worklogs, this_week, time=True):
        """
            取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        week = TimeTool.parse_week_(this_week=this_week, rule=True)
        info_ = list()

        for work in worklogs:
            parse = work.started[:10]
            if parse in week:
                if time is True:
                    info_ += [f'{work.timeSpent}']
                else:
                    info_ += [f'{work.author.name}']
        return info_

    @classmethod
    def compute_cost(cls, sp_time):
        cost = sp_time.replace('d', '*8').replace('h', '*1').replace('m', '/60').replace(' ', '+'). \
            replace('w', '*40').replace('s', '/3600')
        return cost

    @classmethod
    def to_excel(cls, info, this_week):
        start, end = TimeTool.new_parse_week(this_week=this_week)
        file_name = f'{Jira.file}{end}{Jira.is_this_week}{Jira.mapping_file_name}'
        df = pd.DataFrame(info)
        df.dropna(axis=0, how='any', inplace=True)
        df.to_excel(f'{file_name}', index=False)


if __name__ == '__main__':
    Jira.get_person_info(this_week=Jira.is_this_week)


