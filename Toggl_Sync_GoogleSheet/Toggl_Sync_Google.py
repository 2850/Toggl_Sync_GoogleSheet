import os
from utility.toggl.Togglpy import togglpy
from utility.GoogleSheet.googlesheet import GoogleSheet
import pendulum
import pandas as pd
import sys
from datetime import datetime, date, timedelta
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as st
from tkcalendar import DateEntry
import time


def toggl_sync_google_sheet():
    """主要程式進入點
    """
    __clearwindows()
    # 執行主程式
    btnsync['state'] = 'disabled'  # 進度條開始時，不能點擊按鈕
    __sync(s_date.get_date(), e_date.get_date())
    btnsync['state'] = 'normal'


def __clearwindows():
    """刪除Log畫面與進度條
    """
    text_area.delete('1.0', "end")
    bar['value'] = 0


# Inserting Text which is read only
def insert_log(msg):
    print(msg)
    text_area.insert(tk.INSERT, str(msg))
    text_area.insert(tk.INSERT, '\n')  # 換行
    tkframe.update()  # 更新視窗內容
    text_area.see("end")  # 滾輪顯示最新資料


def __sync(s_date: datetime.date, e_date: datetime.date):
    """同步資料

    Args:
        s_date (str): 2023-01-01
        e_date (str): 2023-01-02
    """

    try:

        if (s_date.year > 0 & e_date.year > 0):
            insert_log('【App】輸入格式錯誤。 ex:yyyy-mmdd-yyyy-mmdd')
            sys.exit(1)

        # print("當前工作目錄是：", current_dir,'Toggl_sync_Google\\','Toggl.ini')  
 
        # 讀取設定檔案
        togglpyhelper = togglpy()
        insert_log('【App】讀取設定檔資料中...')

        # togglpyhelper._LoadingSetting()
        togglpyhelper._syncprofile()
        insert_log('【App】讀取設定檔完畢')
        insert_log("【App】月份範圍：{s_date} - {e_date}".format(s_date=str(s_date),
                                                          e_date=str(e_date)))

        # 取得範圍內的資訊
        startdate = pendulum.datetime(s_date.year, s_date.month, s_date.day)
        enddate = pendulum.datetime(e_date.year, e_date.month, e_date.day)

        #[{'id': 2291477950, 'guid': '2c3db05ea091e94b0374f4914a34c2ea', 'wid': 5333167, 'pid': 169590148, 'billable': False, 'start': '2021-12-14T01:48:26+00:00', 'stop': '2021-12-14T03:55:08+00:00', 'duration': 7602, 'description': 'EINK 檔案上傳', 'duronly': False, 'at': '2021-12-14T04:07:00+00:00', 'uid': 6826362}]
        insert_log('【Toggl】呼叫Toggl API 中.....')

        df_entries = togglpyhelper.merge_toggl_data(str(startdate),
                                                    str(enddate))
        df_entries = df_entries[[
            'client_name', 'project_name', 'description', 'tags', 'duration',
            'start', 'stop'
        ]]

        df = togglpyhelper.proc_toggl(df_entries)

        insert_log('【Toggl】Toggl 取得完畢')

        if (len(df) > 0):

            # 產生 google sheet 物件
            sheet = GoogleSheet(togglpyhelper.AUTH_JSON_PATH,
                                togglpyhelper.GSS_SCOPES,
                                togglpyhelper.SHEETKEY,
                                togglpyhelper.GOOGLE_SHEET_NAME)

            # 目前Append Google Sheet 進度
            current_count = 0
            total_count = len(df)

            # 更新進度條最高數字
            bar['maximum'] = int(total_count)

            insert_log('【Toggl】讀取Toggl資料 【{username}】 ：共{count}筆。'.format(
                username=togglpyhelper.TOGGL_USERNAME, count=total_count))
            insert_log(df[[
                'description', 'hours', 'tags', 'client_name', 'project_name'
            ]])

            for index, row in df.iterrows():
                stdate = str(row['start'][:10]).replace("-", "/")
                eddate = str(row['stop'][:10]).replace("-", "/")
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
                sheet.AppendtRow([
                    togglpyhelper.TOGGL_USERNAME,
                    stdate,
                    row['description'],
                    float(row['hours']),
                    str(tags),
                    "",
                    str(row['project_name']),
                    str(row['client_name']),
                ], 2)
                current_count = current_count + 1
                insert_log(
                    '【Sync Google Sheet】目前進度 {current_count} / {total_count}筆。'
                    .format(current_count=current_count,
                            total_count=total_count))

                # 更改進度條
                __updateprogress()

        insert_log('【Sync Google Sheet】打完收工!!!')

    except Exception as e:
        insert_log('【Exception】：{msg}'.format(msg=str(e)))
        # os._exit(1)


def __updateprogress():
    if bar['value'] < bar['maximum']:
        bar['value'] += 1
    tkframe.update()  # 更新視窗內容
    time.sleep(0.01)


# root window
root = tk.Tk()
root.geometry("350x380")
# root.resizable(False, False)
root.title('Toggl小工具')

# Sign in frame
tkframe = ttk.Frame(root)
tkframe.pack(padx=0, pady=0, fill='x')

# start_date
start_date_label = ttk.Label(tkframe, text="日期範圍：")
start_date_label.grid(column=0, row=0, padx=10, pady=10)

# create dateentry
ttk.Label(tkframe, text="選擇開始日期", background='gray61', foreground="white")
s_date = DateEntry(tkframe,
                   date_pattern='y/mm/dd',
                   expand=True,
                   foreground="white")
s_date.grid(column=1, row=0, padx=4, pady=10)
s_date.set_date(date.today() + timedelta(days=-7))

ttk.Label(tkframe, text="選擇結束日期", background='gray61', foreground="white")
e_date = DateEntry(tkframe,
                   date_pattern='y/mm/dd',
                   fill='x',
                   expand=True,
                   foreground="white")
e_date.grid(column=3, row=0, padx=4, pady=10)

# Add Button and Label
btnsync = ttk.Button(root, text="同步", command=toggl_sync_google_sheet)
btnsync.pack(fill='x', expand=1, padx=10, pady=0)

text_area = st.ScrolledText(root,
                            width=60,
                            height=10,
                            font=("Times New Roman", 10))
text_area.pack(fill='both', expand=1, padx=10, pady=10)

# 進度條
bar = ttk.Progressbar(root,
                      mode='determinate',
                      orient='horizontal',
                      length=100)
bar.pack(fill='x', expand=1, padx=10, pady=10)

root.mainloop()
