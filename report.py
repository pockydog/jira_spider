from jira import JIRA
from tqdm import tqdm
import pandas as pd
from Tool.week_tool import TimeTool
from Tool.count_tool import CountTool


class Jira:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'Vicky.C'
    password = '1Q2W3E4R!!!'
    is_this_week = False
    file = '/Users/user/Desktop/jira_spider/JIRA_'
    mapping_file_name = '.xlsx'
    group = ['QA', 'PM', 'Server', 'FE-RD', 'BE-RD', 'Design']

    @classmethod
    def get_group(cls):
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        member_list = list()
        for group in Jira.group:
            group_members = jira.group_members(group)
            for member in group_members:
                member_ = {
                    'group': group,
                    'name': member
                }
                member_list.append(member_)
        return member_list

    @classmethod
    def get_person_info(cls, this_week):
        """
        Main content
        取得相關所需資料
        """
        group_times = {}
        jira = JIRA(server=Jira.domain, basic_auth=(Jira.account, Jira.password))
        info_list = list()

        start, end = TimeTool.new_parse_week(this_week=this_week)
        # 下條件式, 利用JQL
        issues = jira.search_issues(f'updated >= {start} AND updated <= now()', maxResults=0)
        # 取得資料 解析
        a = cls.get_group()
        for issue in tqdm(issues):
            worklogs = jira.worklogs(issue)
            time_list = Jira.get_worklog_info(worklogs=worklogs, this_week=this_week)
            if time_list == []:
                continue
            user_list = Jira.get_worklog_info(time=False, worklogs=worklogs, this_week=this_week)

            status = issue.fields.status.name
            link = issue.permalink()

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
                for i in a:
                    if user == i['name']:
                        # dictionary = {
                        #     'project': result['project'],
                        #     'summary': result['summary'],
                        #     'user': user,
                        #     'group': i['group'],
                        #     'time': f'{round(eval(Jira.compute_cost(sp_time=time)), 2)}',
                        #     'status': result['status'],
                        #     'link': result['link']
                        # }
                        test = {
                            'group': i['group'],
                            'time': f'{round(eval(Jira.compute_cost(sp_time=time)), 2)}'
                        }

                        # info_list.append(dictionary)
                        info_list.append(test)

        for item in info_list:
            group = item['group']
            time = float(item['time'])
            if group in group_times:
                group_times[group] += time
            else:
                group_times[group] = time

            result = [{'group': group, 'time': str(time)} for group, time in group_times.items()]

            print(result)

    # Jira.to_excel(info=info_list, this_week=this_week)

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
                    info_ += [f'{round(eval(Jira.compute_cost(sp_time=work.timeSpent)), 2)}']
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
    Jira.get_group()
