import re
import pandas as pd
import xlwt

from weekly_report import Jira


class CheckinfoHandler:

    @classmethod
    def get_spendtime(cls):
        info = {'name': '', 'time': '='}
        name_list = list()
        _, summary, project, priority, str_creatd, status_list, t_worklog_, link, worklog_, due_date, estimated_time, test_time = Jira.get_person_info(
            this_week=False)
        test = list()
        for i in str(worklog_).split(','):
            name = str(re.sub(r'[^a-zA-Z,]', '', i))
            name_list += [str(re.sub(r'[^a-zA-Z,]', '', i))]

            time = str(re.sub(r'[^0-9/.]', '', i)).lstrip('.')
            result = {
                'name': name,
                'time': f'={time}',
            }
            if result == info:
                continue
            else:
                test.append(result)
        name_list = set(name_list)
        for name in name_list:
            results = {
                'name_list': name,
                'result': f'=SUMIF(A:A,"{name}",B:B)'
            }
            test.append(results)

        df = pd.DataFrame(test)
        df.to_excel(f'testrrr.xlsx', 'counter1', index=False)

    #  新增項目總時長, + 部門花費總時長
    @classmethod
    def get_info(cls):
        name_list = set()
        worklogs, summary, project, priority, str_creatd, status_list, t_worklog_, link, worklog_, due_date, estimated_time, test_time = Jira.get_person_info(
            this_week=False)

        name = Jira.get_worklog_info(worklogs=worklogs, this_week=True, time=False)
        file = xlwt.Workbook('encoding = utf-8')
        sheet = file.add_sheet(f'jira_', cell_overwrite_ok=True)
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'project')
        sheet.write(0, 2, 'summary')
        sheet.write(0, 3, 'worklog')
        sheet.write(0, 4, 'total_worklog')
        sheet.write(0, 5, 'status')

        for i in range(len(summary)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, project[i])
            sheet.write(i + 1, 2, summary[i])
            sheet.write(i + 1, 3, worklog_[i])
            sheet.write(i + 1, 4, t_worklog_[i])
            sheet.write(i + 1, 5, status_list[i])
        # excel 檔案名稱
        file.save(f'JIRA_today{Jira.is_this_week}.xlsx')


if __name__ == '__main__':
    CheckinfoHandler.get_spendtime()
