from clients.http.mailhog_api.apis.mailhog_api import MailhogApi
from packages.restclient.configuration import Configuration




class MailHogApi():
    def __init__(
            self,
            configuration: Configuration
            ):
        self.configuration = configuration
        self.mailhog_api = MailhogApi(configuration=self.configuration)
