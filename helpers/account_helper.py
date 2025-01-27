import time
from json import loads

from retrying import retry

from dm_api_account.models.change_email import ChangeEmail
from dm_api_account.models.change_password import ChangePassword
from dm_api_account.models.login_credentials import LoginCredentials
from dm_api_account.models.registration import Registration
from dm_api_account.models.reset_password import ResetPassword
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
            password=password,
            return_model=False
        )
        token = {
            'x-dm-auth-token': response.headers['x-dm-auth-token']
        }
        self.dm_api_account.account_api.set_headers(token)
        self.dm_api_account.login_api.set_headers(token)

    def change_password(
            self,
            login,
            old_password,
            new_password,
            email
            ):
        response = self.user_login(
            login=login,
            password=old_password,
            incorrect_login=True,
            return_model=False
        )
        token = {
            'x-dm-auth-token': response.headers['x-dm-auth-token']
        }
        reset_password = ResetPassword(
            login=login,
            email=email
        )
        self.dm_api_account.account_api.post_v1_account_password(reset_password=reset_password)
        assert response.status_code == 200, "Пароль не был сброшен"
        pass_token = self.get_activation_token_by_login(login=login, key='ConfirmationLinkUri')
        change_password = ChangePassword(
            login=login,
            token=pass_token,
            oldPassword=old_password,
            newPassword=new_password
        )
        self.dm_api_account.account_api.put_v1_account_password(change_password=change_password, headers=token)
        assert response.status_code == 200, "Пароль не был изменен"


    def register_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        registration = Registration(
            login=login,
            email=email,
            password=password
        )
        response = self.dm_api_account.account_api.post_v1_account(registration=registration)
        assert response.status_code == 201, f"Пользователь не был создан, {response.json()}"
        start_time = time.time()
        token = self.get_activation_token_by_login(login=login, key='ConfirmationLinkUrl')
        end_time = time.time()
        assert end_time - start_time < 3, "Время получения токена превышено"
        assert token is not None, f'Токен для пользователя {login} не был получен'
        response = self.dm_api_account.account_api.put_v1_account_token(token=token)

        return response

    def user_login(
            self,
            login: str,
            password: str,
            remember_me: bool = True,
            return_model:bool = True,
            incorrect_login:bool = False
    ):
        # Авторизация
        login_credentials = LoginCredentials(
            login=login,
            password=password,
            rememberMe=remember_me

        )
        response = self.dm_api_account.login_api.post_v1_account_login(login_credentials=login_credentials, return_model=return_model)
        if incorrect_login:
            return response
        assert response.headers['x-dm-auth-token'], "Токен для пользоватля не был получен"
        assert response.status_code == 200, "Пользователь не был авторизован"
        return response

    def change_email(
            self,
            login: str,
            password: str,
            new_email: str
    ):
        change_email = ChangeEmail(
            login=login,
            password=password,
            email=new_email
        )
        response = self.dm_api_account.account_api.put_v1_account_email(change_email=change_email)
        # Попытка войти после смены почты
        response = self.user_login(login=login, password=password, incorrect_login=True, return_model=False)
        assert response.status_code == 403, "Вход пользователя не был запрещен"
        # Поиск токена для смены email
        token = self.get_activation_token_by_email(email=new_email)
        assert token is not None, f'токен для новой почты {new_email} пользователя {login} не был получен'
        # Активация пользователя с новым email
        response = self.dm_api_account.account_api.put_v1_account_token(token=token)


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
