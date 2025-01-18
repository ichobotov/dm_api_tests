from restclient.configuration import Configuration
from mailhog_api.apis.mailhog_api import MailhogApi



class MailHogApi():
    def __init__(
            self,
            configuration: Configuration
            ):
        self.configuration = configuration
        self.mailhog_api = MailhogApi(configuration=self.configuration)
