from jira import JIRA
import xlwt
import re
from tqdm import tqdm
from collections import Counter
import pandas as pd
from Tool.week_tool import TimeTool


class JiraByAll:
    # 基本設定
    domain = 'http://jira.trevi.cc/'
    account = 'Vicky.C'
    password = 'Pocky0822'
    is_this_week = False
    file = '/Users/user/Desktop/jira_spider/JIRA_'
    mapping_file_name = '.xlsx'

    # 排除不需要顯示的狀態列表
    skip_ = ['Planning', 'Pending']

    @classmethod
    def get_person_info(cls, this_week):
        """
        Main content
        取得相關所需資料
        """
        jira = JIRA(server=JiraByAll.domain, basic_auth=(JiraByAll.account, JiraByAll.password))
        summary = list()
        str_creatd = list()
        link = list()
        priority = list()
        project = list()
        status_list = list()
        user_list = list()
        timespent = list()
        due_date = list()
        estimated_time = list()
        test_time = list()
        timespents = list()
        a = list()
        t_worklog_ = None
        start, end = TimeTool.new_parse_week(this_week=this_week)

        # 下條件式, 利用JQL
        issues = jira.search_issues(f'updated >= {start} AND updated <= now()', maxResults=0)
        # 取得資料 解析
        for issue in tqdm(issues):
            status = issue.fields.status.name
            if status not in JiraByAll.skip_:
                status_list.append(status)
            else:
                continue
            worklogs = jira.worklogs(issue)
            link += [issue.permalink()]
            a += [JiraByAll.test_by_vicky(worklogs=worklogs, this_week=this_week, jira=jira)]
            timespent += [JiraByAll.get_worklog_info(worklogs=worklogs, this_week=this_week)]
            timespents += [JiraByAll.get_worklog_info(time=False, worklogs=worklogs, this_week=this_week)]
            t_worklog_ = JiraByAll.count_timespant(timespent=timespent, is_count=True)
            summary += [issue.fields.summary]

            estimated = issue.fields.timeestimate
            timeorigina = issue.fields.timeoriginalestimate
            # 剩下時間
            estimated_time += [JiraByAll.parse_estimated_time(time_type=estimated)]
            # 起始預判工時
            test_time += [JiraByAll.parse_estimated_time(time_type=timeorigina)]

            # test = issue.fields.timeoriginalestimate
            # print(issue.fields.timeoriginalestimate)

            due_date += [str(issue.fields.duedate)[0:19].replace('None', '-')]
            project += [issue.fields.project.name]
            created = issue.fields.created
            created = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", created)
            str_creatd += ["".join(created)]
            priority += [issue.fields.priority.name]
            user_list += [JiraByAll.get_worklog_info(worklogs=worklogs, this_week=this_week, time=False)]
            user = JiraByAll.get_worklog_info(worklogs=worklogs, this_week=this_week, time=False)
            # q = Jira.test_pockys(user=user, issue=issue, timespent=timespent)

        worklog_ = JiraByAll.test_pocky(name_list=user_list, timespent=timespent)
        # worklog_name, worklog_time += [Jira.vicky_parse_info(worklog_=worklog_, workId=workId)]
        # test = Jira.get_for_test(worklog_code=worklog_code, summary=summary)

        return worklogs, summary, project, priority, str_creatd, status_list, t_worklog_, link, worklog_, due_date, estimated_time, test_time

    @classmethod
    def test_pockys(cls, user, issue, timespent):
        summary = list()
        user_list = list()
        time_list = list()
        project = list()

        for test in user:
            user_list.append(test.split(','))
        for time in timespent:
            b = time.split(',')
            user_list.append(time.split(','))
            for i in range(len(b)):
                summary.append(issue.fields.summary)
                project += [issue.fields.project.name]

    @classmethod
    def parse_estimated_time(cls, time_type):
        if type(time_type) is int:
            estimated_time = float(time_type / 60 / 60)
            estimated_time = (round(estimated_time, 2))

        else:
            estimated_time = '-'

        return estimated_time

    @classmethod
    def get_worklog_info(cls, worklogs, this_week, time=True, workId=None):
        """
            取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        week = TimeTool.parse_week_(this_week=this_week, rule=True)
        print(week)
        info_ = list()

        for work in worklogs:
            parse = work.started[:10]
            if parse in week:
                # test_list += {f'{work.author.name}:{work.timeSpent}'}
                if time is True:
                    info_ += [f'{work.timeSpent}']
                else:
                    info_ += [f'{work.author.name}']
                if workId is True:
                    info_ += [work.issueId]
        return info_

    @classmethod
    def test_by_vicky(cls, worklogs, this_week, jira):
        """
            取得 worklog 資料, 記載員工針對該工單所花費的時間
        """
        week = TimeTool.parse_week_(this_week=this_week, rule=True)
        name = list()
        time = list()
        for work in worklogs:
            parse = work.started[:10]
            if parse in week:
                name += [work.author.name]
                my_count = JiraByAll.compute_cost(sp_time=work.timeSpent)
                my_count = eval(my_count)
                count = "{:.2f}".format(my_count)
                time += [count]
                dict_ = dict(zip(name, time))
                return dict_

    @classmethod
    def export_excel_test(cls, this_week):
        """
        匯出 且 存入 excel
        """
        _, summary, project, priority, str_creatd, status_list, t_worklog_, link, worklog_, due_date, estimated_time, \
            test_time = JiraByAll.get_person_info(this_week=this_week)
        file = xlwt.Workbook('encoding = utf-8')
        sheet = file.add_sheet(f'jira_', cell_overwrite_ok=True)
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'project')
        sheet.write(0, 2, 'summary')
        sheet.write(0, 3, 'priority')
        sheet.write(0, 4, 'created')
        # sheet.write(0, 5, 'due_date')
        sheet.write(0, 5, 'worklog')
        sheet.write(0, 6, 'total_worklog')
        sheet.write(0, 7, 'status')
        sheet.write(0, 8, 'estimated_time')
        # sheet.write(0, 10, '預估時間')
        sheet.write(0, 9, 'link')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, project[i])
            sheet.write(i + 1, 2, summary[i])
            sheet.write(i + 1, 3, priority[i])
            sheet.write(i + 1, 4, str_creatd[i])
            # sheet.write(i + 1, 5, due_date[i])
            sheet.write(i + 1, 5, worklog_[i])
            sheet.write(i + 1, 6, t_worklog_[i])
            sheet.write(i + 1, 7, status_list[i])
            sheet.write(i + 1, 8, estimated_time[i])
            # sheet.write(i + 1, 10, test_time[i])
            sheet.write(i + 1, 9, link[i])
        # excel 檔案名稱
        start, end = TimeTool.new_parse_week(this_week=this_week)
        file.save(f'JIRA_{end}{JiraByAll.is_this_week}.xlsx')
        JiraByAll.to_excel(this_week=this_week)

    @classmethod
    def compute_cost(cls, sp_time):
        cost = sp_time.replace('d', '*8').replace('h', '*1').replace('m', '/60').replace(' ', '+'). \
            replace('w', '*40').replace('s', '/3600')
        return cost

    @classmethod
    def count_timespant(cls, timespent, is_count=None):
        temp = list()
        a_list = list()
        for time in timespent:
            time_list = list()
            for t in time:
                cost = eval(cls.compute_cost(sp_time=t))
                cost = (round(cost, 2))
                time_list.append(cost)
            temp.append(time_list)
        if is_count is None:
            return temp

        if is_count is True:
            for i in temp:
                a_list.append(str(sum(i)))
        return a_list

    @classmethod
    def test_pocky(cls, timespent, name_list):
        temp = cls.count_timespant(timespent=timespent)
        B = list()
        for a, b in zip(name_list, temp):
            name_value_pairs = [f'{x}:{y}' for x, y in zip(a, b)]
            name_sum = Counter()
            # Counter 統計可迭代序列中，每個元素出現的次數
            names = list()
            for item in name_value_pairs:
                name, value = item.split(":")
                names.append(name)
                name_sum[name] += float(value)

            combined = [f"{name}:{name_sum[name]}" for name in names]
            B.append(combined)
        ans = [str(set(i)).replace('set()', '') for i in B]
        return ans

    @classmethod
    def to_excel(cls, this_week):
        start, end = TimeTool.new_parse_week(this_week=this_week)
        file_name = f'{JiraByAll.file}{end}{JiraByAll.is_this_week}{JiraByAll.mapping_file_name}'
        df = pd.read_excel(f'{file_name}')
        df.dropna(axis=0, how='any', inplace=True)
        df.to_excel(f'{file_name}', index=False)


if __name__ == '__main__':
    JiraByAll.export_excel_test(this_week=JiraByAll.is_this_week)


# 優化現在工時一個多人的狀況
# 匯出檔案 依人名分sheet 參考 (sort_info.py )
