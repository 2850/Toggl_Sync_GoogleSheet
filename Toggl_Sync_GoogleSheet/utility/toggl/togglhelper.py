

# class togglhelper:
#     def __init__(self):
#         self.SEARCHYEAR = ""
#         self.USERNAME =""
#         self.TOGGL_TOKEN = ""
#         self.AUTH_JSON_PATH = ""
#         self.GSS_SCOPES = ""
#         self.SHEETKEY = ""

#     def LoadingSetting(self,projectname,inifilename):
#         """讀取Ini設定檔案

#         Args:
#             projectname (string): 固定寫死Toggl2GoogleSheet
#             inifilename (string): 設定檔案名稱
#         """
#         print('【App】讀取資料中...')

#         f = FileProc()
#         config = f.readconfig('{0}/{1}'.format(projectname,inifilename), "Section_A")

#         self.SEARCHYEAR = config["YEAR"]
#         self.USERNAME = config["USERNAME"]
#         self.TOGGL_TOKEN = config["TOGGL_TOKEN"] # "89e5b0e543ccd739c94ebbfb730447db"
#         self.AUTH_JSON_PATH = projectname + '/' + config["AUTH_JSON_PATH"] # 'n8n-willis-da99ff5fb91d.json'
#         self.GSS_SCOPES = [config["GSS_SCOPES"]]
#         self.SHEETKEY = config["SHEETKEY"] # '1sV1IH0lxNTUkMLDLwwcQ1oIiQtJ8VY-ruXyw6vdf-hI'   # 2023

#         print("【App】日期年份{yy}".format(yy=int(self.SEARCHYEAR)))
#         print('【App】讀取完畢')

#     def SyncTogglData(self):
#         """同步Toggl Project、Client 名稱

#         Returns:
#             bool: 正常執行(true)
#         """
#         return False

