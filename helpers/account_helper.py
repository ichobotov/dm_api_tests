import time
from json import loads

from services.dm_api_account import DmApiAccount
from services.api_mailhog import MailHogApi


class AccountHelper:
    def __init__(
            self,
            dm_api_account: DmApiAccount,
            mailhog: MailHogApi
            ):
        self.dm_api_account = dm_api_account
        self.mailhog = mailhog

    def register_new_user(self, login:str, password:str, email:str):
        json_data = {
            'login': login,
            'email': email,
            'password': password,
        }

        response = self.dm_api_account.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f"Пользователь не был создан, {response.json()}"
        time.sleep(0.5)  # Введение задержки, тк иногда возникает ситуация, когда в response еще нет письма с нужным логином
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        assert response.status_code == 200, "Письма не получены"
        token = self.get_activation_token_by_login(login=login, response=response)
        response = self.dm_api_account.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, "Пользователь не был активирован"

        return response

    def user_login(self, login:str, password:str, rememberMe:bool=True):
        # Авторизация
        json_data = {
            'login': login,
            'password': password,
            'rememberMe': rememberMe,
        }

        response = self.dm_api_account.login_api.post_v1_account_login(json_data=json_data)
        assert response.status_code == 200, "Пользователь не был авторизован"

    def change_email(self, login:str, password:str, new_email:str):
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
        # Получение писем из почтового ящика
        time.sleep(0.5)  # Введение задержки, тк иногда возникает ситуация, когда в response еще нет письма с нужным логином
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        assert response.status_code == 200, "Письма не получены"
        # Поиск токена для смены email
        token = self.get_activation_token_by_email(email=new_email, response=response)
        assert token is not None, f'токен для новой почты {new_email} пользователя {login} не был получен'
        # Активация пользователя с новым email
        response = self.dm_api_account.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, "Пользователь не был активирован"


    @staticmethod
    def get_activation_token_by_login(
            login,
            response
            ):
        token = None
        for item in response.json()['items']:

            user_data = loads(item['Content']['Body'])
            user_login = user_data['Login']
            if user_login == login:
                token = user_data['ConfirmationLinkUrl'].split('/')[-1]
                break
        return token

    @staticmethod
    def get_activation_token_by_email(email, response):
        token = None
        for item in response.json()['items']:
            user_email = item['Content']['Headers']['To'][0]
            if user_email == email:
                user_data = loads(item['Content']['Body'])
                token = user_data['ConfirmationLinkUrl'].split('/')[-1]
                break
        return token
