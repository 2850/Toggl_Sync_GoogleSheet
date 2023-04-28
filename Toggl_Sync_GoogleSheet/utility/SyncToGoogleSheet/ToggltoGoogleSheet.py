import os
from utility.toggl.Togglpy import togglpy
from utility.GoogleSheet.googlesheet import GoogleSheet
import pendulum
import pandas as pd
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

class synctogooglesheet:
    def sync(self,s_date:datetime.date,e_date:datetime.date):
        """同步資料

        Args:
            s_date (str): 2023-01-01
            e_date (str): 2023-01-02
        """
        try:
            
            # 讀取設定檔案
            togglpyhelper = togglpy()

            print("【App】月份範圍：{s_date} - {e_date}".format(s_date=str(s_date),e_date=str(e_date)))

            if (s_date.year > 0 & e_date.year > 0):
                print('【App】輸入格式錯誤。 ex:yyyy-mmdd-yyyy-mmdd')
                sys.exit(1)

            # 取得範圍內的資訊
            startdate = pendulum.datetime(s_date.year, s_date.month,s_date.day )
            enddate = pendulum.datetime(e_date.year, e_date.month,e_date.day  )

            #[{'id': 2291477950, 'guid': '2c3db05ea091e94b0374f4914a34c2ea', 'wid': 5333167, 'pid': 169590148, 'billable': False, 'start': '2021-12-14T01:48:26+00:00', 'stop': '2021-12-14T03:55:08+00:00', 'duration': 7602, 'description': 'EINK 檔案上傳', 'duronly': False, 'at': '2021-12-14T04:07:00+00:00', 'uid': 6826362}]
            print('【Toggl】呼叫Toggl API 中.....')
            
            df_entries = togglpyhelper.merge_toggl_data(str(startdate),str(enddate))
            df_entries = df_entries[['client_name','project_name','description','tags','duration','start','stop']]
            
            df = togglpyhelper.proc_toggl(df_entries)
            
            print('【Toggl】Toggl 取得完畢')

            if (len(df) > 0):

                # 取得Track 資料
                # df_entries = togglpyhelper.gettrack(df_entries)

                # 產生 google sheet 物件
                sheet = GoogleSheet(togglpyhelper.AUTH_JSON_PATH,togglpyhelper.GSS_SCOPES,togglpyhelper.SHEETKEY,togglpyhelper.GOOGLE_SHEET_NAME)

                # 目前Append Google Sheet 進度
                current_count = 0
                total_count = len(df)

                print('【Toggl】讀取Toggl資料 【{username}】 ：共{count}筆。'.format(username=togglpyhelper.TOGGL_USERNAME,count=total_count))
                print(df[['description','hours','tags','client_name','project_name']])

                for index, row in df.iterrows():
                    stdate = str(row['start'][:10]).replace("-","/")
                    eddate = str(row['stop'][:10]).replace("-","/")
                    tags = ""

                    # 這邊只取一個
                    if (pd.isna(row['tags']) == False):
                        tags = row['tags'][0]

                    # AD名稱	TOGGL_USERNAME
                    # 執行日期	Stdate
                    # 執行項目	Description
                    # 耗時	    hours
                    # 分類	    tags
                    # 備註	    沒有
                    # 標籤	    Project
                    # 網站/系統 Client
                    
                    # 資料 Append Google Sheet
                    sheet.AppendtRow([togglpyhelper.TOGGL_USERNAME,
                    stdate,
                    row['description'],
                    float(row['hours']),
                    str(tags),
                    "",
                    str(row['project_name']),
                    str(row['client_name']),
                    ],2)
                    current_count = current_count + 1
                    print('【Sync Google Sheet】目前進度 {current_count} / {total_count}筆。'.format(current_count=current_count,total_count=total_count))

            print('打完收工!!!')

        except Exception as e:
            print("Exception Error:", e)
            os._exit(1)
            