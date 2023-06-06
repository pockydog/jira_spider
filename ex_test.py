import pandas as pd
import xlwt
from collections import defaultdict



class WeeklyTo:
    INFOLIST = 'A', 'C', 'E'
    PROJECTLIST = ['官網(菲)', 'G03', 'G08', 'G09', '電投', '其他', '官網(台)', 'slot', '官網(菲) ', 'G03 ', 'G08 ', 'G09 ', '電投 ', '其他 ', '官網(台) ', 'slot ']
    test = ['G03', 'G03 ']

    @classmethod
    def get_info(cls):
        key_list = list()
        value_list = list()
        get_info = pd.read_excel(
            'trevi 2023 0502-0505 週報表.xlsx',
            sheet_name='vicky',
        )
        test1 = get_info['type'].values.tolist()
        # test = get_info['plan'].values.tolist()
        test2 = get_info['time'].values.tolist()
        d = defaultdict(list)
        for key, value in zip(test1, test2):
            d[key].append(value)
        a = dict(d)
        print(dict(d))

        print(type(a))
        # print(dict(d))

        return key_list, value_list
        # return test1, test2

    # @classmethod
    # def parse_info(cls):
    #     test1, test2 = WeeklyTo.get_info()
    #     for u in test1:
    #         if u in WeeklyTo.PROJECTLIST:
    #             print(u)
    #     # print(test1)

    @classmethod
    def export_excel(cls):
        test1, test2 = WeeklyTo.get_info()
        file = xlwt.Workbook('encoding = utf-8')
        sheet = file.add_sheet(f'jira_', cell_overwrite_ok=True)
        sheet.write(0, 0, '')
        sheet.write(0, 1, 'project')
        sheet.write(0, 2, 'time')
        for i in range(len(test1)):
            sheet.write(i + 1, 0, i)
            sheet.write(i + 1, 1, test1)
            sheet.write(i + 1, 2, test2)

        file.save(f'test_pp.xls')


if __name__ == '__main__':
    WeeklyTo.get_info()
