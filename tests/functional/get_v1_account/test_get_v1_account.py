import allure

from checkers.get_v1_account import GetV1Account
from checkers.http_checkers import check_status_code_http


@allure.suite("Тест на проверку метода GET v1/account")
class TestGetV1Account:
    @allure.sub_suite("Позитивные тесты")
    @allure.title("Проверка получения данных об авторизованном пользователе")
    def test_get_v1_account_auth(
            self,
            auth_account_helper
    ):
        with check_status_code_http():
            response = auth_account_helper.dm_api_account.account_api.get_v1_account()
            GetV1Account.check_response_values_for_auth_user(response, login="ivan_50")

    @allure.sub_suite("Негативные тесты")
    @allure.title("Проверка получения данных об неавторизованном пользователе")
    def test_get_v1_account_no_auth(
            self,
            account_helper
            ):
        with check_status_code_http(401, "User must be authenticated"):
            response = account_helper.dm_api_account.account_api.get_v1_account()
            GetV1Account.check_response_values_for_not_auth_user(response)
