import pygsheets
import Const


class ExcelSpidreTool:

    @staticmethod
    def get_excel_data(sheet_name, url):
        """
        取得Excel 資料，回傳Json格式
        """
        get_json = pygsheets.authorize(service_file=Const.setting_file)
        open_by_url = get_json.open_by_url(url)
        worksheet = open_by_url.worksheet_by_title(sheet_name)
        data = worksheet.get_all_records()
        return data