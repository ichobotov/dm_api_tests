import allure
import requests

from dm_api_account.models.change_email import ChangeEmail

from dm_api_account.models.change_password import ChangePassword
from dm_api_account.models.registration import Registration
from dm_api_account.models.reset_password import ResetPassword
from dm_api_account.models.user_details_envelope import UserDetailsEnvelope
from dm_api_account.models.user_envelope import UserEnvelope
from restclient.client import RestClient


class AccountApi(RestClient):

    @allure.step("Регистрация пользователя")
    def post_v1_account(
            self,
            registration: Registration
    ):
        """
        Register user
        :param registration:
        :return:
        """
        response = self.post(
            path=f'/v1/account',
            json=registration.model_dump(exclude_none=True, by_alias=True)
        )
        return response

    @allure.step("Получение текущего пользователя")
    def get_v1_account(
            self,
            return_model: bool = True,
            **kwargs
    ):
        """
        Get current user
        :param json_data:
        :return:
        """
        response = self.get(
            path=f'/v1/account',
            **kwargs
        )
        user_details_envelope_model = UserDetailsEnvelope(**response.json())
        if return_model:
            return user_details_envelope_model
        return response

    @allure.step("Активация пользователя")
    def put_v1_account_token(
            self,
            token,
            return_model: bool = True,
    ):
        """
        Activate registered user
        :param token:
        :return:
        """
        headers = {
            'accept': 'text/plain',
        }
        response = self.put(
            path=f'/v1/account/{token}',
            headers=headers
        )
        user_envelope_model = UserEnvelope(**response.json())
        if return_model:
            return user_envelope_model
        return response

    @allure.step("Изменение пароля")
    def put_v1_account_password(
            self,
            change_password: ChangePassword,
            headers,
            return_model: bool = True,
    ):
        """
        Change registered user password
        :param change_password:
        :param headers:
        :return:
        """

        response = self.put(
            path=f'/v1/account/password',
            json=change_password.model_dump(exclude_none=True, by_alias=True),
            headers=headers
        )
        user_envelope_model = UserEnvelope(**response.json())
        if return_model:
            return user_envelope_model
        return response

    @allure.step("Сброс пароля")
    def post_v1_account_password(
            self,
            reset_password: ResetPassword
    ):
        """
        Reset user password
        :param reset_password:
        :return:
        """

        response = self.post(
            path=f'/v1/account/password',
            json=reset_password.model_dump(exclude_none=True, by_alias=True)
        )
        return response

    @allure.step("Изменение адреса электронной почты")
    def put_v1_account_email(
            self,
            change_email: ChangeEmail,
            return_model: bool = True,
    ):
        """
        Change registered user email
        :param change_email:
        :return:
        """
        response = self.put(
            path='/v1/account/email',
            json=change_email.model_dump(exclude_none=True, by_alias=True)
        )
        user_envelope_model = UserEnvelope(**response.json())
        if return_model:
            return user_envelope_model
        return response
