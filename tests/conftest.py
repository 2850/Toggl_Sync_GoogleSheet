import json
import pandas as pd
import pytest
from utility.toggl.Togglpy import togglpy

@pytest.fixture()
def test_togglpyhelper():
    """檢查同步資訊是否正常執行
    """
    # 讀取設定檔案
    togglpyhelper = togglpy()

    # assert togglpyhelper.SEARCHYEAR == "2023"
    # assert togglpyhelper.AUTH_JSON_PATH == "n8n-willis-da99ff5fb91d.json"
    # assert togglpyhelper.GSS_SCOPES[0] == "https://spreadsheets.google.com/feeds"
    # assert togglpyhelper.SHEETKEY == "1sV1IH0lxNTUkMLDLwwcQ1oIiQtJ8VY-ruXyw6vdf-hI"
    # assert togglpyhelper.TOGGL_TOKEN == "89e5b0e543ccd739c94ebbfb730447db"
    # assert togglpyhelper.ORG_ID == "5305487"
   
    return togglpyhelper

@pytest.fixture()
def mock_org_id():
    return "5305487"

@pytest.fixture()
def mock_workspace_id():
    return "5333167"

@pytest.fixture()
def mock_username():
    return "willis.ko"

@pytest.fixture()
def mock_projects_id():
    f = open('tests/resource/projects_v9.json',encoding='utf8')
    data = json.load(f)
    return data

@pytest.fixture()
def mock_clients_data():
    f = open('tests/resource/clients_v9.json',encoding='utf8')
    data = json.load(f)
    return data

@pytest.fixture()
def mock_entries_data():
    f = open('tests/resource/time_entries_v9.json',encoding='utf8')
    data = json.load(f)
    return data

@pytest.fixture()
def mock_toggl_merge_data():
    f = open('tests/resource/toggl_merge_data.json',encoding='utf8')
    data = json.load(f)
    df = pd.json_normalize(data)    
    return df[['client_name','project_name','description','tags','duration','start','stop']]