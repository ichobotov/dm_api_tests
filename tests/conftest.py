from datetime import datetime
from typing import NamedTuple
import pytest
import structlog

from helpers.account_helper import AccountHelper
from restclient.configuration import Configuration as MailhogConfiguration
from restclient.configuration import Configuration as DmApiConfiguration
from services.dm_api_account import DmApiAccount
from services.api_mailhog import MailHogApi

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(indent=4, ensure_ascii=True, sort_keys=True)
    ]

)

class User(NamedTuple):
    login: str
    password: str
    email: str


@pytest.fixture(scope='session')
def mailhog_api():
    mailhog_configuration = MailhogConfiguration(host='http://5.63.153.31:5025')
    mailhog_api = MailHogApi(configuration=mailhog_configuration)
    return mailhog_api

@pytest.fixture(scope='session')
def account_api():
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)
    account_api = DmApiAccount(configuration=dm_api_configuration)
    return account_api

@pytest.fixture(scope='session')
def account_helper(account_api, mailhog_api):
    account_helper = AccountHelper(dm_api_account=account_api, mailhog=mailhog_api)
    return account_helper

@pytest.fixture()
def auth_account_helper(mailhog_api):
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)
    account = DmApiAccount(configuration=dm_api_configuration)
    account_helper = AccountHelper(dm_api_account=account, mailhog=mailhog_api)
    account_helper.auth_client(
        login='ivan_65',
        password='123456789'
    )
    return account_helper


@pytest.fixture()
def prepare_user():
    now = datetime.now()
    data = now.strftime('%d%m%y_%H%M%S.%f')[:-3]
    login = f'ivan_{data}'
    email = f'{login}@mail.ru'
    password = '1234567'
    return User(login=login, password=password, email=email)