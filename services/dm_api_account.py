from restclient.configuration import Configuration
from dm_api_account.apis.login_api import LoginApi
from dm_api_account.apis.account_api import AccountApi


class DmApiAccount:
    def __init__(
            self,
            configuration: Configuration
            ):
        self.configuration = configuration
        self.login_api = LoginApi(configuration=self.configuration)
        self.account_api = AccountApi(configuration=self.configuration)
