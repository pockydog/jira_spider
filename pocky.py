from Tool.excel_tool import ExcelSpidreTool
import Const
import re


class Monly:
    project_name = 'vicky_test'

    @classmethod
    def test_one(cls):
        project_list = list()
        google_sheet = ExcelSpidreTool.get_excel_data(url=Const.survey_urls, sheet_name=f'vicky')
        for row in google_sheet:
            if row['項目'] in project_list:
                continue
            else:
                project_list.append(row['項目'])
            for project in project_list:
                if row['項目'] in project:
                    data = {
                        'Project': row['項目'],
                        '產品': int(row['產品'].replace('%', '')),
                        # '美術': row['設計'].replace('%', ''),
                        # '後台': row['後台'].replace('%', ''),
                        # '前端': row['前端'].replace('%', ''),
                        # '服務器': row['服務器'].replace('%', ''),
                        # '測試': row['測試'].replace('%', ''),
                    }
                    print(data)


#
# if __name__ == '__main__':
#     print(Monly.test_one())

a = 30

for i in range(a+1):
    print(i)
