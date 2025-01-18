import time
from json import loads
import structlog

from dm_api_account.apis.account_api import AccountApi
from dm_api_account.apis.login_api import LoginApi
from mailhog_api.apis.mailhog_api import MailhogApi
from restclient.configuration import Configuration as MailhogConfiguration
from restclient.configuration import Configuration as DmApiConfiguration

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(indent=4, ensure_ascii=True, sort_keys=True)
    ]

)


def test_put_v1_account_token():
    # Регистрация пользователя
    mailhog_configuration = MailhogConfiguration(host='http://5.63.153.31:5025')
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)

    account_api = AccountApi(configuration=dm_api_configuration)
    login_api = LoginApi(configuration=dm_api_configuration)
    mailhog_api =MailhogApi(mailhog_configuration)

    login = 'ivan_39'
    email = f'{login}@mail.ru'
    password = '123456789'

    json_data = {
        'login': login,
        'email': email,
        'password': password,
    }

    response = account_api.post_v1_account(json_data=json_data)
    assert response.status_code == 201, f"Пользователь не был создан, {response.json()}"

    # Получение писем из почтового ящика
    time.sleep(0.5)  # Введение задержки, тк иногда возникает ситуация, когда в response еще нет письма с нужным логином
    response = mailhog_api.get_api_v2_messages()
    assert response.status_code == 200, "Письма не получены"

    # Получение активационного токена
    time.sleep(0.5)  # Введение задержки, тк иногда возникает ситуация, когда в response еще нет письма с нужным логином
    token = get_activation_token_by_login(login, response)
    assert token is not None, f'токен для пользователя {login} не был получен'

    # Активация пользователя
    response = account_api.put_v1_account_token(token=token)
    assert response.status_code == 200, "Пользователь не был активирован"


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
