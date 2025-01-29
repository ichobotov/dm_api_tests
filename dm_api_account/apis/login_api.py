import allure
import requests

from dm_api_account.models.login_credentials import LoginCredentials
from dm_api_account.models.user_envelope import UserEnvelope
from restclient.client import RestClient


class LoginApi(RestClient):

    @allure.step("Аутентификация пользователя")
    def post_v1_account_login(
            self,
            login_credentials: LoginCredentials,
            return_model: bool = True,
    ):
        """
        Authenticate via credentials
        :param login_credentials:
        :return:
        """
        response = self.post(
            path=f'/v1/account/login',
            json=login_credentials.model_dump(exclude_none=True, by_alias=True)
        )
        user_envelope_model = UserEnvelope(**response.json())
        if return_model:
            return user_envelope_model
        return response

    @allure.step("Выход из системы")
    def delete_v1_account_login(
            self,
            **kwargs
    ):
        """
        Logout as current user
        :param kwargs:
        :return:
        """

        response = self.delete(
            path='/v1/account/login',
            **kwargs
        )
        return response

    @allure.step("Выходиз системы на всех устройствах")
    def delete_v1_account_login_all(
            self,
            **kwargs
    ):
        """
        Logout as current user from all devices
        :param kwargs:
        :return:
        """

        response = self.delete(
            path='/v1/account/login/all',
            **kwargs
        )
        return response
