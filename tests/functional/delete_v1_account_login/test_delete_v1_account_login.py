import allure



@allure.suite("Тест на проверку метода DELETE v1/account/login")
class TestDeleteV1AccountLogin:
    @allure.sub_suite("Позитивные тесты")
    @allure.title("Проверка выхода из личного каюинета")
    def test_delete_v1_account_login(
            self,
            auth_account_helper
            ):
        response = auth_account_helper.dm_api_account.login_api.delete_v1_account_login()
        assert response.status_code == 204, "Пользователь не был разлогирован"
