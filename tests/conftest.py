import os
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import pytest
import structlog
import platform
from swagger_coverage_py.reporter import CoverageReporter

from vyper import v
from helpers.account_helper import AccountHelper
from packages.restclient.configuration import Configuration as MailhogConfiguration
from packages.restclient.configuration import Configuration as DmApiConfiguration
from services.dm_api_account import DmApiAccount
from services.api_mailhog import MailHogApi

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(indent=4, ensure_ascii=True, sort_keys=True)
    ]

)

options = (
    'service.dm_api_accout',
    'service.mailhog',
    'user.login',
    'user.password',
    'telegram.chat_id',
    'telegram.token'
)

@pytest.fixture(scope="session", autouse=True)
def setup_swagger_coverage():
    reporter = CoverageReporter(api_name="dm-api-account", host="http://5.63.153.31:5051")
    reporter.setup("/swagger/Account/swagger.json")
    yield
    reporter.generate_report()
    # reporter.cleanup_input_files()



@pytest.fixture(scope='session', autouse=True)
def set_config(request):
    config = Path(__file__).joinpath('../../').joinpath('config')
    config_name = request.config.getoption('--env')
    v.set_config_name(config_name)
    v.add_config_path(config)
    v.read_in_config()
    for option in options:
        v.set(f'{option}', request.config.getoption(f'--{option}'))
    request.config.stash['telegram-notifier-addfields']['environment'] = config_name
    request.config.stash['telegram-notifier-addfields']['report'] = 'https://ichobotov.github.io/dm_api_tests/'


    if platform.system() == "Windows":
        pass
    else:
        os.environ["TELEGRAM_BOT_CHAT_ID"] = v.get('telegram.chat_id')
        os.environ["TELEGRAM_BOT_ACCESS_TOKEN"] = v.get('telegram.token')



def pytest_addoption(parser):
    parser.addoption("--env", action='store', default='stg', help='run stg')
    for option in options:
        parser.addoption(f"--{option}", action='store', default=None)


class User(NamedTuple):
    login: str
    password: str
    email: str


@pytest.fixture(scope='session')
def mailhog_api():
    mailhog_configuration = MailhogConfiguration(host=v.get('service.mailhog'),disable_log=True)
    mailhog_api = MailHogApi(configuration=mailhog_configuration)
    return mailhog_api

@pytest.fixture(scope='session')
def account_api():
    dm_api_configuration = DmApiConfiguration(host=v.get('service.dm_api_account'), disable_log=False)
    account_api = DmApiAccount(configuration=dm_api_configuration)
    return account_api

@pytest.fixture(scope='session')
def account_helper(account_api, mailhog_api):
    account_helper = AccountHelper(dm_api_account=account_api, mailhog=mailhog_api)
    return account_helper

@pytest.fixture()
def auth_account_helper(mailhog_api):
    dm_api_configuration = DmApiConfiguration(host=v.get('service.dm_api_account'))
    account = DmApiAccount(configuration=dm_api_configuration)
    account_helper = AccountHelper(dm_api_account=account, mailhog=mailhog_api)
    account_helper.auth_client(
        login=v.get('user.login')+'_50',
        password=v.get('user.password')
    )
    return account_helper

@pytest.fixture()
def prepare_user():
    now = datetime.now()
    data = now.strftime('%d%m%y_%H%M%S.%f')[:-3]
    login = v.get('user.login')+data
    email = f'{login}@mail.ru'
    password = '1234567'
    return User(login=login, password=password, email=email)