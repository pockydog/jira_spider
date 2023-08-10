import re
import pandas as pd
from weekly_report import Jira


class CheckinfoHandler:

    @classmethod
    def get_info(cls):
        info = {'name': '', 'time': '='}
        name_list = list()
        summary, project, priority, str_creatd, status_list, t_worklog_, link, worklog_, due_date, estimated_time, test_time = Jira.get_person_info(
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
        df.to_excel(f'test.xlsx', 'counter1', index=False)
#  新增項目總時長, + 部門花費總時長


if __name__ == '__main__':
    CheckinfoHandler.get_info()








