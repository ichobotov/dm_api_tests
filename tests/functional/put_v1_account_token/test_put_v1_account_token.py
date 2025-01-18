import time
from json import loads
import structlog

from restclient.configuration import Configuration as MailhogConfiguration
from restclient.configuration import Configuration as DmApiConfiguration
from services.dm_api_account import DmApiAccount
from services.api_mailhog import MailHogApi

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(indent=4, ensure_ascii=True, sort_keys=True)
    ]

)

def test_put_v1_account_token():
    # Регистрация пользователя
    mailhog_configuration = MailhogConfiguration(host='http://5.63.153.31:5025')
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)

    account = DmApiAccount(configuration=dm_api_configuration)
    mailhog =MailHogApi(configuration=mailhog_configuration)

    login = 'ivan_45'
    email = f'{login}@mail.ru'
    password = '123456789'

    json_data = {
        'login': login,
        'email': email,
        'password': password,
    }

    response = account.account_api.post_v1_account(json_data=json_data)
    assert response.status_code == 201, f"Пользователь не был создан, {response.json()}"

    # Получение писем из почтового ящика
    time.sleep(0.5)  # Введение задержки, тк иногда возникает ситуация, когда в response еще нет письма с нужным логином
    response = mailhog.mailhog_api.get_api_v2_messages()
    assert response.status_code == 200, "Письма не получены"

    # Получение активационного токена
    time.sleep(0.5)  # Введение задержки, тк иногда возникает ситуация, когда в response еще нет письма с нужным логином
    token = get_activation_token_by_login(login, response)
    assert token is not None, f'токен для пользователя {login} не был получен'

    # Активация пользователя
    response = account.account_api.put_v1_account_token(token=token)
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
