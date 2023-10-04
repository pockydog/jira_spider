from jira import JIRA
from tqdm import tqdm
from Tool.week_tool import TimeTool
from Tool.count_tool import CountTool
import re


class Jira_:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'Vicky.C'
    password = '1Q2W3E4R!!!'
    is_this_week = False
    file = '/Users/user/Desktop/jira_spider/JIRA_'
    mapping_file_name = '.xlsx'
    group = ['QA', 'PM', 'Server', 'FE-RD', 'BE-RD', 'Design']

    @classmethod
    def get_group(cls, group_list):
        jira = JIRA(server=Jira_.domain, basic_auth=(Jira_.account, Jira_.password))
        member_list = list()
        member_set = dict()
        result = None

        for group in Jira_.group:
            group_members = jira.group_members(group)
            for member in group_members:
                if group_list is True:
                    result = Jira_.get_group_info(group=group, member=member, member_list=member_list)
                else:
                    result = Jira_.counter_for_group(group=group, member_set=member_set)
        return result

    @classmethod
    def get_group_info(cls, group, member, member_list):
        member_ = {
            'group': group,
            'name': str(re.sub(r'[^a-zA-Z,]', '', member)),
            'time': int(0)
        }
        member_list.append(member_)
        return member_list

    @classmethod
    def counter_for_group(cls, group, member_set):
        if group in member_set:
            member_set[group] += 1
        else:
            member_set[group] = 1

        return member_set

    @classmethod
    def get_person_info(cls, this_week):
        jira = JIRA(server=Jira_.domain, basic_auth=(Jira_.account, Jira_.password))
        info_list = dict()

        start, end = TimeTool.new_parse_week(this_week=this_week)
        # 下條件式, 利用JQL
        time_values = list()
        issues = jira.search_issues(f'updated >= {start} AND updated <= {end}', maxResults=0)
        # 取得資料 解析
        group_ = cls.get_group(group_list=True)
        totally_time = dict()

        for issue in tqdm(issues):
            worklogs = jira.worklogs(issue)
            time_list = Jira_.get_worklog_info(worklogs=worklogs, this_week=this_week)
            if time_list == []:
                continue
            user_list = Jira_.get_worklog_info(time=False, worklogs=worklogs, this_week=this_week)

            # status = issue.fields.status.name
            # link = issue.permalink()
            #
            summary = issue.fields.summary
            project_list = issue.fields.project.name
            result = {
                'project': project_list,
                'summary': summary,
                'time': time_list,
                'user': user_list,
                # 'status': status,
                # 'link': link
            }
            user_values = result['user']
            time_values = result['time']
            for user, time in zip(user_values, time_values):
                for group in group_:
                    if user == group['name']:
                        dictionary = {
                            # 'project': result['project'],
                            # 'summary': result['summary'],
                            'user': user,
                            'group': group['group'],
                            'time': round(eval(CountTool.compute_cost(sp_time=time)), 2),
                            # 'status': result['status'],
                            # 'link': result['link']
                        }
                        group_name = dictionary['group']
                        group_time = float(dictionary['time'])
                        if group_name in totally_time:
                            totally_time[group_name] += group_time
                        else:
                            totally_time[group_name] = 0
        print(totally_time)

    @classmethod
    def get_time(cls, info_list):
        totally_time = dict()
        for group in range(len(info_list)):
            group_name = info_list[group]['group']
            group_time = float(info_list[group]['time'])
            if group_name in totally_time:
                totally_time[group_name] += group_time
            else:
                totally_time[group_name] = 0

        return totally_time

    @classmethod
    def sum_info(cls, totally_time, group_list):
        sum_info = {}
        for key in group_list.keys():
            if key in totally_time:
                value = totally_time[key] / group_list[key]
            else:
                value = 0
            sum_info[key] = round(value, 2)
        return sum_info

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
                    info_ += [f'{round(eval(CountTool.compute_cost(sp_time=work.timeSpent)), 2)}']
                else:
                    info_ += [f'{work.author.name}']
        return info_


if __name__ == '__main__':
    Jira_.get_person_info(this_week=Jira_.is_this_week)
