from datetime import datetime
from typing import NamedTuple
import pytest
import structlog

from helpers.account_helper import AccountHelper
from restclient.configuration import Configuration as MailhogConfiguration
from restclient.configuration import Configuration as DmApiConfiguration
from services.dm_api_account import DmApiAccount
from services.api_mailhog import MailHogApi
from tests.functional import logins

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(indent=4, ensure_ascii=True, sort_keys=True)
    ]

)

class User(NamedTuple):
    login: str
    password: str
    email: str

@pytest.fixture
def mailhog_api():
    mailhog_configuration = MailhogConfiguration(host='http://5.63.153.31:5025')
    mailhog_api = MailHogApi(configuration=mailhog_configuration)
    return mailhog_api

@pytest.fixture()
def account_api():
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)
    account_api = DmApiAccount(configuration=dm_api_configuration)
    return account_api

@pytest.fixture()
def account_helper(account_api, mailhog_api):
    account_helper = AccountHelper(dm_api_account=account_api, mailhog=mailhog_api)
    return  account_helper

@pytest.fixture()
def prepare_user():
    now = datetime.now()
    data = now.strftime('%d_%m_%y_%H_%M_%S.%f')[:-3]
    login = f'ivan_{data}'
    email = f'{login}@mail.ru'
    password = '123456789'
    return User(login=login, password=password, email=email)

def test_put_v1_account_token(account_helper, prepare_user):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)





