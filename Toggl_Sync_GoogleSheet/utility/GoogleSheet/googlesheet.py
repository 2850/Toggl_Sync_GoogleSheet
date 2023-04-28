import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheet:

    def __init__(self,jsonpath:str,scopes:list,sheetkey:str,sheetname:str):
        try:
            self.jsonpath = jsonpath
            self.scopes = scopes
            #連線
            credentials = ServiceAccountCredentials.from_json_keyfile_name(jsonpath,scopes)
            gss_client = gspread.authorize(credentials)
            self._sheet = gss_client.open_by_key(sheetkey).worksheet(sheetname)
        except Exception as e:
            raise Exception('Google Sheet Error',e) 

    def InsertRow(self,data:list,rownumber = 0):
        return self._sheet.insert_row(data,rownumber,value_input_option='USER_ENTERED')

    def AppendtRow(self,data:list,rownumber = 0):
        return self._sheet.append_row(data,value_input_option='USER_ENTERED')

    def GetAll(self):
        return self._sheet.get_all_values()
    

    # auth_json_path = 'n8n-willis-da99ff5fb91d.json'
    # gss_scopes = ['https://spreadsheets.google.com/feeds']


    #開啟 Google Sheet 資料表
    # spreadsheet_key = '1G-YmITGLGteOmZwt3McWSZ4i3f4jSFLgb5Bui1Uo-8w'

    #建立工作表1
    # sheet = gss_client.open_by_key(spreadsheet_key).sheet1
    #自定義工作表名稱

    # sheet = gss_client.open_by_key(spreadsheet_key).worksheet('工作表2')

#Google Sheet 資料表操作(舊版)
# sheet.clear() # 清除 Google Sheet 資料表內容
# listtitle=["姓名","電話"]
# sheet.append_row(listtitle)  # 標題
# listdata=["Liu","0912-345678"]
# sheet.append_row(listdata)  # 資料內容

# #Google Sheet 資料表操作(20191224新版)
# sheet.update_acell('D2', 'ABC')  #D2加入ABC
# sheet.update_cell(2, 4, 'ABC')   #D2加入ABC(第2列第4行即D62)
# #寫入一整列(list型態的資料)
# values = ['A','B','C','D']
# sheet.insert_row(values) #插入values到第1列
# #讀取儲存格
# sheet.acell('B1').value
# sheet.cell(1, 2).value
# #讀取整欄或整列
# sheet.row_values(1) #讀取第1列的一整列
# sheet.col_values(1) #讀取第1欄的一整欄
# #讀取整個表
# sheet.get_all_values()