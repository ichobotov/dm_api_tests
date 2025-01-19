def test_delete_v1_account_login(auth_account_helper):
    response = auth_account_helper.dm_api_account.login_api.delete_v1_account_login_all()
    assert response.status_code == 204, "Пользователь не был разлогирован cо всех устройств"