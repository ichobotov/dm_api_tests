import structlog

from restclient.configuration import Configuration as MailhogConfiguration
from restclient.configuration import Configuration as DmApiConfiguration
from services.dm_api_account import DmApiAccount
from services.api_mailhog import MailHogApi
from helpers.account_helper import AccountHelper
from tests.functional import logins

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(indent=4, ensure_ascii=True, sort_keys=True)
    ]

)

def test_post_v1_account():
    mailhog_configuration = MailhogConfiguration(host='http://5.63.153.31:5025')
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)

    account = DmApiAccount(configuration=dm_api_configuration)
    mailhog = MailHogApi(configuration=mailhog_configuration)
    account_helper = AccountHelper(account, mailhog)

    login = f'{logins.post_v1_login_account}'
    email = f'{login}@mail.ru'
    password = '123456789'
    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.user_login(login=login, password=password)








