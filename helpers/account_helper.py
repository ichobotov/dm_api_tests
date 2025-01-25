import time
from json import loads

from retrying import retry
from services.dm_api_account import DmApiAccount
from services.api_mailhog import MailHogApi


def retry_if_result_none(
        result
):
    """Return True if we should retry (in this case when result is None), False otherwise"""
    return result is None


class AccountHelper:
    def __init__(
            self,
            dm_api_account: DmApiAccount,
            mailhog: MailHogApi
    ):
        self.dm_api_account = dm_api_account
        self.mailhog = mailhog

    def auth_client(
            self,
            login,
            password
    ):
        response = self.user_login(
            login=login,
            password=password
        )
        token = {
            'x-dm-auth-token': response.headers['x-dm-auth-token']
        }
        self.dm_api_account.account_api.set_headers(token)
        self.dm_api_account.login_api.set_headers(token)

    def change_password(
            self,
            login,
            oldPassword,
            newPassword,
            email
            ):
        response = self.user_login(
            login=login,
            password=oldPassword
        )
        token = {
            'x-dm-auth-token': response.headers['x-dm-auth-token']
        }
        json_data = {
            'login': login,
            'email': email
         }
        self.dm_api_account.account_api.post_v1_account_password(json_data=json_data)
        assert response.status_code == 200, "Пароль не был сброшен"
        pass_token = self.get_activation_token_by_login(login=login, key='ConfirmationLinkUri')
        json_data = {
            'login': login,
            'token': pass_token,
            'oldPassword': oldPassword,
            'newPassword': newPassword
        }
        self.dm_api_account.account_api.put_v1_account_password(json_data=json_data, headers=token)
        assert response.status_code == 200, "Пароль не был изменен"


    def register_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        json_data = {
            'login': login,
            'email': email,
            'password': password,
        }

        response = self.dm_api_account.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f"Пользователь не был создан, {response.json()}"
        start_time = time.time()
        token = self.get_activation_token_by_login(login=login, key='ConfirmationLinkUrl')
        end_time = time.time()
        assert end_time - start_time < 3, "Время получения токена превышено"
        assert token is not None, f'Токен для пользователя {login} не был получен'
        response = self.dm_api_account.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, "Пользователь не был активирован"

        return response

    def user_login(
            self,
            login: str,
            password: str,
            rememberMe: bool = True
    ):
        # Авторизация
        json_data = {
            'login': login,
            'password': password,
            'rememberMe': rememberMe,
        }

        response = self.dm_api_account.login_api.post_v1_account_login(json_data=json_data)
        assert response.headers['x-dm-auth-token'], "Токен для пользоватля не был получен"
        assert response.status_code == 200, "Пользователь не был авторизован"
        return response

    def change_email(
            self,
            login: str,
            password: str,
            new_email: str
    ):
        # Смена email
        json_data = {
            'login': login,
            'password': password,
            'email': new_email,
        }
        response = self.dm_api_account.account_api.put_v1_account_email(json_data)
        assert response.status_code == 200, "Email не был изменен"
        # Попытка войти после смены почты
        response = self.dm_api_account.login_api.post_v1_account_login(json_data=json_data)
        assert response.status_code == 403, "Вход пользователя не был запрещен"
        # Поиск токена для смены email
        token = self.get_activation_token_by_email(email=new_email)
        assert token is not None, f'токен для новой почты {new_email} пользователя {login} не был получен'
        # Активация пользователя с новым email
        response = self.dm_api_account.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, "Пользователь не был активирован"


    @retry(stop_max_attempt_number=5, stop_max_delay=1000, retry_on_result=retry_if_result_none)
    def get_activation_token_by_login(
            self,
            login,
            key
    ):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()['items']:

            user_data = loads(item['Content']['Body'])
            user_login = user_data['Login']
            if user_login == login:
                token = user_data[f'{key}'].split('/')[-1]
                break
        return token

    @retry(stop_max_attempt_number=5, stop_max_delay=1000, retry_on_result=retry_if_result_none)
    def get_activation_token_by_email(
            self,
            email
    ):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()['items']:
            user_email = item['Content']['Headers']['To'][0]
            if user_email == email:
                user_data = loads(item['Content']['Body'])
                token = user_data['ConfirmationLinkUrl'].split('/')[-1]
                break
        return token
