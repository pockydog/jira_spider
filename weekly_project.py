import pandas as pd
from weekly_report import Jira


class Test:

    @classmethod
    def get_info(cls):
        name_list = list()

        summary, project, priority, str_creatd, status_list, t_worklog_, link, worklog_, due_date, estimated_time, \
            test_time = Jira.get_person_info(
            this_week=False)
        for i in range(len(summary)):
            result = {
                'project': project[i],
                't_worklog_': t_worklog_[i],
                'result': f'=SUMIF(A:A,"{project}",B:B)'
            }
            name_list.append(result)
        df = pd.DataFrame(name_list)
        # df.to_excel(f'12345678.xlsx', 'test', index=False)
        # df = pd.read_excel(f'12345678.xlsx')
        df.dropna(axis=0, how='any', inplace=True)
        df.to_excel(f'12345678.xlsx', index=False)
        print('1234')


if __name__ == '__main__':
    Test.get_info()
