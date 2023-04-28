from datetime import date
import logging
import pytest
from utility.FileExtention import FileProc
from utility.toggl.Togglpy import togglpy
import pytest_mock

def test__sync_workspacebyorgid(test_togglpyhelper,mock_org_id):    
    r = test_togglpyhelper._sync_workspace_by_orgid(mock_org_id)
    data = r.json()
    workspace_id = data[0]['workspaces'][0]['workspace_id']
    user_id = data[0]['user_id']
    name = data[0]['workspaces'][0]['name']

    # 驗證API回傳正確
    assert r.status_code == 200
    assert len(r.json()) > 0

    # 驗證資料正確性
    assert workspace_id == 5333167
    assert user_id == 6826362
    assert name == 'willis.ko'

def test_syncprofile(mock_org_id,mocker:pytest_mock.MockFixture):
    """檢查初始化設定，更新基本資料、Projects

    Args:
        test_togglpyhelper (class): toggl module
        test_org_id (str): 組織Id
    """
    
    wk = mocker.patch('utility.toggl.Togglpy.togglpy._sync_workspace_by_orgid',autospec=True)
    # project = mocker.patch('utility.toggl.Togglpy.togglpy._sync_projects_by_wid',autospec=True)
    # client = mocker.patch('utility.toggl.Togglpy.togglpy._sync_clients_by_wid',autospec=True)
    
    test_togglpyhelper = togglpy()
    
    # 檢查執行是否正常
    wk.assert_called_once_with(test_togglpyhelper,mock_org_id)
    # project.assert_called_once_with(test_togglpyhelper,mock_projects_id)
    # client.assert_called_once_with(test_togglpyhelper,mock_clients_data)
        
# def test_stub(test_togglpyhelper:togglpy,mock_clients_data,mocker:pytest_mock.MockFixture):
#     # 以下程式只要使用 get_clients_data 就會把mock_clients_data傳給他
#     mocker.patch('utility.toggl.Togglpy.togglpy.get_clients_data',autospec=True,return_value=mock_clients_data)
    
#     r = test_togglpyhelper.get_clients_data()
#     assert '[{"id": 61683580, "wid": 5333167}]' == r
#     # print(r)

# def test_mock(test_togglpyhelper:togglpy,mocker:pytest_mock.MockFixture):
#     """Mock練習
#     """
#     # mock_log本身就是goodseeyou
#     mock_log = mocker.patch('utility.toggl.Togglpy.togglpy.goodseeyou',autospec=True)
#     test_togglpyhelper.get_clients_data()

#     # 確認goodseeyou有被執行一次，並且有給參數
#     # goodseeyou有self 就要加入 togglheler
#     mock_log.assert_called_once_with(test_togglpyhelper,'mytest')
    
#     # Spy 
#     mock_py = mocker.spy(test_togglpyhelper,'goodseeyou')    
#     mock_py.assert_called_once_with(test_togglpyhelper,'mytest')
    
#     # Spy 與 Stub差異在於Spy會【實際執行】Goodseeyou並記錄傳入參數
    
def test__sync_projectsbywid(test_togglpyhelper:togglpy,mock_workspace_id:str):
    r = test_togglpyhelper._sync_projects_by_wid(mock_workspace_id)
    assert r.status_code == 200
    assert len(r.json()) > 0
    
def test_sync_clientsbywid(test_togglpyhelper,mock_workspace_id:str):
    r = test_togglpyhelper._sync_clients_by_wid(mock_workspace_id)
    assert r.status_code == 200
    assert len(r.json()) > 0

def test_togglinit():
    togglpyhelper = togglpy()
    
    # assert togglpyhelper.SEARCHYEAR == "2023"
    assert togglpyhelper.AUTH_JSON_PATH == "n8n-willis-da99ff5fb91d.json"
    assert togglpyhelper.GSS_SCOPES[0] == "https://spreadsheets.google.com/feeds"
    assert togglpyhelper.SHEETKEY == "1sV1IH0lxNTUkMLDLwwcQ1oIiQtJ8VY-ruXyw6vdf-hI"
    assert togglpyhelper.TOGGL_TOKEN == "89e5b0e543ccd739c94ebbfb730447db"
    assert togglpyhelper.ORG_ID == "5305487"

def test_entries(test_togglpyhelper):
        start_date = str('2023-01-11T00:00:00+00:00')
        end_date = str('2023-02-08T00:00:00+00:00')
        result = test_togglpyhelper._get_entries_range(start_date,end_date)
        print(result.json())
        assert result.status_code == 200
        
def test_merge_toggl_data(test_togglpyhelper:togglpy,mock_clients_data,mock_entries_data,mock_projects_id,mocker:pytest_mock.MockFixture):
    # 以下程式只要使用 get_clients_data 就會把mock_clients_data傳給他
    mocker.patch('utility.toggl.Togglpy.togglpy._sync_projects_by_wid',autospec=True,return_value=mock_projects_id)
    mocker.patch('utility.toggl.Togglpy.togglpy._sync_clients_by_wid',autospec=True,return_value=mock_clients_data)
    mocker.patch('utility.toggl.Togglpy.togglpy._get_entries_range',autospec=True,return_value=mock_entries_data)
    
    s_date = '0206'
    e_date = '0208'
    df = test_togglpyhelper.merge_toggl_data(s_date,e_date)
    assert len(df) > 0
    # print(r)

def test_organizations(test_togglpyhelper):
    r = test_togglpyhelper._sync_organizations()
    print(r.json())
    logging.info(str(r.json()))
    assert r.status_code == 200
    assert len(r.json()) > 0
    
def test_proc_toggl(test_togglpyhelper,mock_toggl_merge_data):
    df = test_togglpyhelper.proc_toggl(mock_toggl_merge_data)
    assert len(df) > 0
    