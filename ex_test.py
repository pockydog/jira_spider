import pandas as pd


class WeeklyTo:

    @classmethod
    def get_info(cls):
        info = pd.read_excel(
            "trevi 2023 0502-0505 週報表.xlsx",
            sheet_name='本週報表(人力）',
            usecols='B, D, F')

        return info.head()


if __name__ == '__main__':
    print(WeeklyTo.get_info())
