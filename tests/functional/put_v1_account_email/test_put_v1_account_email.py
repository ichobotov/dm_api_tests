import allure


@allure.suite("Тесты на проверку метода PUT v1/account/email")
class TestsPutV1AccountEmail:
    @allure.sub_suite("Позитивные тесты")
    @allure.title("Проверка смены адреса электронной почты")
    def test_put_v1_account_email(
            self,
            account_helper,
            prepare_user
            ):
        login = prepare_user.login
        email = prepare_user.email
        new_email = f'{login}_new@mail.ru'
        password = prepare_user.password
        account_helper.register_new_user(login=login, password=password, email=email)
        account_helper.user_login(login=login, password=password, return_model=False)
        account_helper.change_email(login=login, password=password, new_email=new_email)
        account_helper.user_login(login=login, password=password, return_model=False)
