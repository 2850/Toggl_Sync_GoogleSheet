from requests.auth import HTTPBasicAuth
import pandas as pd
import dateutil.parser
import time
import os
import json
import math
import urllib
import requests
from utility.FileExtention import FileProc


class togglpy:

    def __init__(self):
        """建構式
        Args:
            token (sting): Token
        """

        self.__headers = {'content-type': 'application/json'}
        self.__entries_api = {
            # "Range":["GET","https://api.track.toggl.com/api/v8/time_entries"],
            "Range":
            ["GET", "https://api.track.toggl.com/api/v9/me/time_entries"],
            "Projects": [
                "GET",
                "https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects"
            ],
            "Clients": [
                "GET",
                "https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients"
            ],
            "Workspace": [
                "GET",
                "https://api.track.toggl.com/api/v9/organizations/{organization_id}/users"
            ],
            "organizations":
            ["GET", "https://api.track.toggl.com/api/v9/me/organizations"],
        }
        self.__auth_api = {
            "API": [
                "Get",
                "https://api.track.toggl.com/api/v8/me?with_related_data=true"
            ]
        }
        self.AUTH_JSON_PATH = ""
        self.GSS_SCOPES = ""
        self.SHEETKEY = ""
        self.iniconfig = ""

        self.__inifile_section_name = ""
        self.__inifile_path = ""
        self.__W_ID = ""
        self.__USER_ID = ""
        self.ORG_ID = ""
        self.TOGGL_USERNAME = ""
        self.TOGGL_TOKEN = ""
        self.__auth = ""
        self.PROJECTNAME = 'Toggl_Sync_GoogleSheet'

        # '.\Toggl_Sync_GoogleSheet\Toggl.ini'
        inifilepath=(".\{}\{}".format(self.PROJECTNAME,'Toggl.ini'))  
        self._LoadingSetting(inifilepath=inifilepath)
        # self.__auth = HTTPBasicAuth(self.TOGGL_TOKEN, 'api_token')
        self._syncprofile()

    def get_clients_data(self):
        self.goodseeyou("mytest")
        return '[{"id": 61683580, "wid": 5333167, "archived": false, "name": "CPG", "at": "2022-12-15T10:59:03+00:00"}, {"id": 61693022, "wid": 5333167, "archived": false, "name": "YFS", "at": "2022-12-19T09:06:34+00:00"}, {"id": 61791221, "wid": 5333167, "archived": false, "name": "\u5168\u806f", "at": "2023-01-16T06:42:04+00:00"}, {"id": 61791219, "wid": 5333167, "archived": false, "name": "\u8a02\u55ae\u7cfb\u7d71", "at": "2023-01-16T06:41:56+00:00"}, {"id": 61791220, "wid": 5333167, "archived": false, "name": "BPM", "at": "2023-01-16T06:41:59+00:00"}]'

    def goodseeyou(self, msg: str):
        print(msg)

    def _LoadingSetting(self,
                        inifilepath: str = "Toggl.ini",
                        configsection: str = "Section_A"):
        """讀取Ini設定檔案

        Args:
            projectname (string): 固定寫死Toggl2GoogleSheet
            inifilename (string): 設定檔案名稱
        """
        print('【App】讀取{inifilepath}資料中...'.format(inifilepath=inifilepath))

        f = FileProc()
        self.__inifile_path = inifilepath
        self.__inifile_section_name = configsection

        config = f.readconfig(inifilepath)
        self.iniconfig = config

        # 取得基本設定檔案
        configA = config[configsection]

        # self.__USERNAME = configA["USERNAME"]
        # "89e5b0e543ccd739c94ebbfb730447db"
        self.TOGGL_TOKEN = configA["TOGGL_TOKEN"]
        # self.ORG_ID = configA["organization_id"]
        self.GOOGLE_SHEET_NAME = configA["googlesheetname"]

        # 'n8n-willis-da99ff5fb91d.json'
        self.AUTH_JSON_PATH = ".\{}\{}".format(self.PROJECTNAME,configA["AUTH_JSON_PATH"])
        self.GSS_SCOPES = [configA["GSS_SCOPES"]]
        # '1sV1IH0lxNTUkMLDLwwcQ1oIiQtJ8VY-ruXyw6vdf-hI'   # 2023
        self.SHEETKEY = configA["SHEETKEY"]

        # 設定token
        self.__auth = HTTPBasicAuth(self.TOGGL_TOKEN, 'api_token')
        print('【App】讀取{inifilepath}完畢'.format(inifilepath=inifilepath))

    def _syncprofile(self):
        """同步Toggl資料 workspace、userId、Name

        Args:
            org_id (str): 組織ID

        Returns:
            Bool: 回傳成功或是失敗
        """

        try:
            # 同步基本資訊
            configA = self.iniconfig[self.__inifile_section_name]

            # 同步 organization.id
            ro = self._sync_organizations()

            # 同步 username、workspace_id、user_id
            rw = self._sync_workspace_by_orgid(self.ORG_ID)

            self.TOGGL_USERNAME = configA["toggl_username"]
            self.__USER_ID = configA["toggl_user_id"]
            self.__W_ID = configA["toggl_workspace_id"]

            return rw.status_code == 200 & ro.status_code == 200
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise RuntimeError("unable to handle error")

    # 取得專案名稱
    def get_user_projects(self):
        """取得專案名稱

        Returns:
            DataFrame: 取得專案名稱
        """
        info = self.__get_base_info()
        res = info.json()
        ids = [x["id"] for x in res["data"]["projects"]]
        names = [x["name"] for x in res["data"]["projects"]]
        df = pd.DataFrame(list(zip(ids, names)), columns=['pid', 'pname'])
        # 另一種寫法(比較慢)
        # pd.json_normalize(res["data"], record_path= "projects")[['id','name']]
        return df

    # 取得使用者基本資訊，參考 auth.json
    def __get_base_info(self):
        url = self.__auth_api["API"][1]
        r = requests.get(url, headers=self.__headers, auth=self.__auth)
        return r

    # 取得記錄狀況 by 日期
    def _get_entries_range(self, startdate: str, enddate: str):
        params = {'start_date': startdate, 'end_date': enddate}
        return self.__callapi("Range", params)

    def __callapi(self, urlname: str, param):
        full = self.__entries_api[urlname][1]
        if (param):
            encodeparam = urllib.parse.urlencode(param)
            url = self.__entries_api[urlname][1]
            full = "{}?{}".format(url, encodeparam)

        result = requests.get(full, headers=self.__headers, auth=self.__auth)
        # print("function:{urlname}，Reulst：{result}".format(urlname=urlname,result = result))
        return result

    # 使用workspaceId取得專案名稱
    def _sync_projects_by_wid(self, w_id: str):
        print('【Toggl】Project同步中...')
        # 每次執行都直接覆蓋專案列表
        filepath = "{username}-prjects.json".format(
            username=self.TOGGL_USERNAME)
        url = self.__entries_api["Projects"][1]
        r = requests.get(url.format(workspace_id=w_id),
                         headers={'content-type': 'application/json'},
                         auth=self.__auth)

        json_object = json.dumps(r.json(), ensure_ascii=False)
        with open(filepath, "w", encoding='utf8') as outfile:
            outfile.write(json_object)

        print('【Toggl】Project完畢')
        return r

    # 使用workspaceId取得專案名稱
    def _sync_clients_by_wid(self, w_id: str):
        """同步Clients

        Args:
            w_id (str): workspace_id

        Returns:
            result : api result
        """
        print('【Toggl】clients同步中...')
        try:
            # 每次執行都直接覆蓋專案列表
            filepath = "{username}-clients.json".format(
                username=self.TOGGL_USERNAME)
            url = self.__entries_api["Clients"][1]
            apirul = url.format(workspace_id=w_id)
            # print(apirul)
            r = requests.get(apirul,
                             headers={'content-type': 'application/json'},
                             auth=self.__auth)

            json_object = json.dumps(r.json(), ensure_ascii=False)
            with open(filepath, "w", encoding='utf8') as outfile:
                outfile.write(json_object)

            print('【Toggl】clients完畢')
            return r
        except:
            print('【Toggl】clients An exception occurred')
            return None

    # 使用組織Id取得workspace_id
    def _sync_workspace_by_orgid(self, org_id: str):
        """使用組織Id取得workspace_id

        Args:
            org_id (str): 組織Id

        Returns:
            result : api result
        """
        print('【Toggl】workspace同步中...')
        try:
            url = self.__entries_api["Workspace"][1]
            r = requests.get(url.format(organization_id=org_id),
                             headers={'content-type': 'application/json'},
                             auth=self.__auth)
            data = r.json()
            # print(r.json())

            workspace_id = data[0]['workspaces'][0]['workspace_id']
            user_id = data[0]['user_id']
            name = data[0]['workspaces'][0]['name']

            # 儲存需要的欄位資訊
            self.iniconfig[self.__inifile_section_name][
                'toggl_workspace_id'] = str(workspace_id)
            self.iniconfig[self.__inifile_section_name]['toggl_user_id'] = str(
                user_id)
            self.iniconfig[
                self.__inifile_section_name]['toggl_username'] = str(name)

            with open(self.__inifile_path, 'w', encoding='utf8') as f:
                self.iniconfig.write(f)

            print('【Toggl】workspace完畢')

            return r
        except:
            print('【Toggl】workspace An exception occurred')
            return None

    # 秒數轉小時(以0.5為一個單位)
    def __transhours(self, secend: int):
        total = round(secend / 3600, 2)  # 總時數
        mod = total % 1  # 取餘數
        hours = math.floor(total)  # 小時

        if (mod > 0.8 and mod < 1):
            return hours + 1
        elif (mod < 0.8 and mod > 0.3):
            return hours + 0.5
        else:
            return hours

    # 取得Track資料
    def gettrack(self, df_entries):
        # 取得 Toggl的所有專案
        df_pid = self.get_user_projects()

        # Merge Project & Toggl Data
        df_merge = pd.merge(df_entries, df_pid, on=['pid'])
        df_final = df_merge[[
            'id', 'pid', 'pname', 'description', 'duration', 'start', 'stop',
            'tags'
        ]]
        # 日期

        df_final["CreateDate"] = df_final.apply(
            lambda x: dateutil.parser.parse(x['start']).strftime("%Y-%m-%d"),
            axis=1)
        # 計算總時數
        # df_final["Total"] = df_final.apply(lambda x : time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(int(x['duration']))),axis=1)
        # 開始
        df_final["start"] = df_final.apply(lambda x: dateutil.parser.parse(x[
            'start']).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                           axis=1)
        # 結束
        df_final["stop"] = df_final.apply(lambda x: dateutil.parser.parse(x[
            'stop']).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                          axis=1)
        # 總耗時(單位 = 0.5小時)
        df_final["hours"] = df_final.apply(
            lambda x: self.__transhours(int(x["duration"])), axis=1)
        # print(df_final)

        # print(df_final.to_json())

        # Group By 專案，讓相同的專案時間總和成一筆，同一天，相同描述者。
        dd = df_final.groupby(
            by=['description', 'CreateDate'])['duration'].sum().reset_index(
                name='Second')

        dd["Total"] = dd.apply(
            lambda x: time.strftime('%H:%M:%S', time.gmtime(int(x['Second']))),
            axis=1)
        # print(dd)

        return df_final

    def merge_toggl_data(self, s_date: str, e_date: str):        
        """Client、Project、BaseInfo 合併

        Args:
            s_date (str): 2023-01-01
            e_date (str): 2023-01-03

        Returns:
            dataframe: 要匯入Google的結果
        """
        
        try:
            projests = self._sync_projects_by_wid(self.__W_ID)
            clients = self._sync_clients_by_wid(self.__W_ID)
            entries = self._get_entries_range(s_date, e_date)

            if clients == None:
                raise Exception("""必須填寫Toggl Track 的Client。
                                每個執行項目必須有相對應的Client
                                Client對應日報【網站/系統】""")

            if projests == None:
                raise Exception("""必須填寫Toggl Track的Project。
                                每個執行項目必須有相對應的Project
                                Project對應日報【標籤】""")

            if entries == None:
                raise Exception("取不到資料，請重新選擇日期範圍。")

            # ./test/projects_v9.json
            df_projects = pd.json_normalize(projests.json())
            df_projects = df_projects[['id', 'name', 'wid', 'cid']]
            df_projects.rename(columns={
                'id': 'pid',
                'name': 'project_name'
            },
                            inplace=True)
            df_projects = df_projects.set_index(['wid', 'cid'])

            # ./test/clients_v9.json
            df_clients = pd.json_normalize(clients.json())
            df_clients = df_clients[['id', 'wid', 'name']]
            df_clients.rename(columns={
                'id': 'cid',
                'name': 'client_name'
            },
                            inplace=True)
            # df_clients = df_clients.set_index(['cid','wid'])

            # ./test/entries_v9.json
            df_entries = pd.json_normalize(entries.json())
            df_entries = df_entries[[
                'id', 'start', 'stop', 'duration', 'description', 'tags', 'wid',
                'pid'
            ]]
            df_entries = df_entries.set_index(['pid', 'wid'])

            df = df_projects.merge(df_clients, how='left', on=['cid'])
            df.set_index(['wid', 'pid'])
            df_toggl_data = df_entries.merge(df, how='left', on=['wid', 'pid'])
            # df_toggl_data = df_entries.merge(df_projects,how='left',on=['pid']).merge(df_clients,how='left',on=['wid','pid'])
            # df_toggl_data = pd.merge(df_entries,df_projects,df_clients,on=['pid'])
        except Exception as err:
            raise Exception(f"merge_toggl_data exception occurred {err=}, {type(err)=}")
        

        # df_toggl_data output Demo
        # client_name project_name description  tags     duration       start                       stop
        # YFS         OGSM          OGSM分類    [專案]      1386        2023-01-09T09:13:12+00:00  2023-01-09T09:36:18Z
        # YFS         OGSM          OGSM分類    [專案]      1500        2023-01-09T08:48:09+00:00  2023-01-09T09:13:09Z
        # YFS         OGSM          OGSM分類    [專案]      1009        2023-01-09T08:26:19+00:00  2023-01-09T08:43:08Z
        # YFS         預期外        尾牙抽獎     [突發]      4233        2023-01-09T07:12:00+00:00  2023-01-09T08:22:33Z
        return df_toggl_data

    def proc_toggl(self, df: pd.DataFrame):
        df["CreateDate"] = df.apply(
            lambda x: dateutil.parser.parse(x['start']).strftime("%Y-%m-%d"),
            axis=1)
        # 計算總時數
        # df_final["Total"] = df_final.apply(lambda x : time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(int(x['duration']))),axis=1)
        # 開始
        df["start"] = df.apply(lambda x: dateutil.parser.parse(x['start']).
                               strftime("%Y-%m-%dT%H:%M:%SZ"),
                               axis=1)
        # 結束
        df["stop"] = df.apply(lambda x: dateutil.parser.parse(x['stop']).
                              strftime("%Y-%m-%dT%H:%M:%SZ"),
                              axis=1)
        # 總耗時(單位 = 0.5小時)
        df["hours"] = df.apply(lambda x: self.__transhours(int(x["duration"])),
                               axis=1)
        # print(df_final)

        # print(df_final.to_json())

        # Group By 專案，讓相同的專案時間總和成一筆，同一天，相同描述者。
        dd = df.groupby(
            by=['description', 'CreateDate'])['duration'].sum().reset_index(
                name='Second')

        dd["Total"] = dd.apply(
            lambda x: time.strftime('%H:%M:%S', time.gmtime(int(x['Second']))),
            axis=1)
        # print(dd)

        return df

    def _sync_organizations(self):
        """取得第一個組織ID

        Returns:
            json: organizations 回傳json檔案。參考test/organizations
        """
        data = self.__callapi("organizations", None)

        if (data.status_code == 200):
            organization_id = data.json()[0]['id']
            # 儲存需要的欄位資訊
            self.iniconfig[self.__inifile_section_name][
                'organization_id'] = str(organization_id)

            self.ORG_ID = str(organization_id)
        return data

    def Processing(self):
        """處理資料
        """
        GGG = "TEST"
        print(GGG)
        self.__get_a_value()

    def __get_a_value(self):
        """取得A值
        """
        a = "TEST"
        if (len(a) > 0):
            print("OK")
