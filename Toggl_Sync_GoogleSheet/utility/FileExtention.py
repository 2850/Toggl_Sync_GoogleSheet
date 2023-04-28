import pandas as pd
import os
import time
from os import listdir
from os import walk
import subprocess
from configparser import ConfigParser


class FileProc:
    def readconfig(self, filepath: str):
        """讀取設定檔案

        Args:
            filepath (str): 檔案路徑
            section (str): 讀取的區域

        Returns:
            [type]: [description]
        """
        if not filepath:
            filepath = "Config.ini"

        myconfig = ConfigParser()
        myconfig.read(filepath)
        return myconfig

    def readfiletodic(self, filepath: str) -> dict:
        """讀取檔案資料到 Dictionary

        Example:
        --------
        檔案範例:

        >>> 五月花,https://www.facebook.com/tw.mayflower
        ... 得意,https://www.facebook.com/delightPK2016
        ... 小綠蛙,https://www.facebook.com/froschtw
        ... 橘子工坊,https://www.facebook.com/orangehouse.tw



        Args:
            filepath (str): 檔案路徑

        Returns:
            dict: 資料集合
        """
        d = {}
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                (key, val) = line.split(',')
                d[key] = val
        return d

    def readfiletodataframe(self, filepath: str):
        """讀取檔案到DataFrame

        Args:
            filepath (str): 檔案路徑

        Returns:
            [type]: [description]
        """
        df = pd.read_csv(filepath, index_col=0, encoding='utf-8')
        return df

    def removefilelastmodify(self, folder: str, day: int, extension: str):
        """刪除第X天前的資料

        Args:
            folder (str): 檢查的檔案路徑
            day (int): 天數(正數=前X天)
            extension (str): 附檔名(txt或py)
        """
        now = time.time()
        files = [
            os.path.join(folder, filename) for filename in os.listdir(folder)
            if filename.endswith('.' + extension)
        ]

        for filename in files:
            if (os.stat(filename).st_mtime) < now - (day * 86400):
                command = "rm {0}".format(filename)
                subprocess.call(command, shell=True)

    def getfiles(self, directory, extension):
        """取得該資料夾的所有檔案

        Args:
            directory (str): 資料夾路徑
            extension (str): 附檔名

        Returns:
            [type]: [description]
        """
        return (f for f in listdir(directory) if f.endswith('.' + extension))

    def getmenuidbycategory(self, categoryno):
        mapping = self.readfiletodataframe('MenuCategoryMapping.csv')
        MenuID = mapping.loc[mapping['CategoryNo'] == categoryno].values[0][2]
        return MenuID
