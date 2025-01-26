from checkers.get_v1_account import GetV1Account
from checkers.http_checkers import check_status_code_http


def test_get_v1_account_auth(
        auth_account_helper
    ):
    with check_status_code_http():
        response = auth_account_helper.dm_api_account.account_api.get_v1_account()
        GetV1Account.check_response_values_for_auth_user(response)


def test_get_v1_account_no_auth(
        account_helper
    ):
    with check_status_code_http(401, "User must be authenticated"):
        response = account_helper.dm_api_account.account_api.get_v1_account()
        GetV1Account.check_response_values_for_not_auth_user(response)
