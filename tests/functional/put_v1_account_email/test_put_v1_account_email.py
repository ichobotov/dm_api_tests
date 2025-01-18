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


def test_post_v1_account_email():
    # Регистрация пользователя
    mailhog_configuration = MailhogConfiguration(host='http://5.63.153.31:5025')
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)

    account_api = AccountApi(configuration=dm_api_configuration)
    login_api = LoginApi(configuration=dm_api_configuration)
    mailhog_api = MailhogApi(mailhog_configuration)

    login = 'ivan_40'
    email = f'{login}@mail.ru'
    new_email = f'{login}_new@mail.ru'
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
    token = get_activation_token_by_login(login, response)
    assert token is not None, f'токен для пользователя {login} не был получен'

    # Активация пользователя
    response = account_api.put_v1_account_token(token=token)
    assert response.status_code == 200, "Пользователь не был активирован"

    # Авторизация
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True,
    }

    response = login_api.post_v1_account_login(json_data=json_data)
    assert response.status_code == 200, "Пользователь не был авторизован"

    # Смена email
    json_data = {
        'login': login,
        'password': password,
        'email': new_email,
    }

    response = account_api.put_v1_account_email(json_data)
    assert response.status_code == 200, "Email не был изменен"

    # Попытка войти после смены почты
    response = login_api.post_v1_account_login(json_data=json_data)
    assert response.status_code == 403, "Вход пользователя не был запрещен"

    # Получение писем из почтового ящика
    time.sleep(0.5)  # Введение задержки, тк иногда возникает ситуация, когда в response еще нет письма с нужным логином
    response = mailhog_api.get_api_v2_messages()
    assert response.status_code == 200, "Письма не получены"

    # Поиск токена для смены email
    token = get_activation_token_by_email(email=new_email, response=response)
    assert token is not None, f'токен для новой почты {new_email} пользователя {login} не был получен'

    # Активация пользователя с новым email
    response = account_api.put_v1_account_token(token=token)
    assert response.status_code == 200, "Пользователь не был активирован"

    # Повторная авторизация
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True,
    }

    response = login_api.post_v1_account_login(json_data=json_data)
    assert response.status_code == 200, "Пользователь не был авторизован"


def get_activation_token_by_login(login, response):
    token = None
    for item in response.json()['items']:

        user_data = loads(item['Content']['Body'])
        user_login = user_data['Login']
        if user_login == login:
            token = user_data['ConfirmationLinkUrl'].split('/')[-1]
            break
    return token


def get_activation_token_by_email(email, response):
    token = None
    for item in response.json()['items']:
        user_email = item['Content']['Headers']['To'][0]
        if user_email == email:
            user_data = loads(item['Content']['Body'])
            token = user_data['ConfirmationLinkUrl'].split('/')[-1]
            break
    return token






