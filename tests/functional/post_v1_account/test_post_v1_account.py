import pytest

from checkers.http_checkers import check_status_code_http
from checkers.post_v1_account import PostV1Account


def test_post_v1_account(
        account_helper,
        prepare_user,
):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)
    response = account_helper.user_login(login=login, password=password, return_model=True)
    PostV1Account.check_response_values(response)


@pytest.mark.parametrize(
    "login, email, password, expected_code, expected_message, errors_details",
    [
        ('A', 'test@mail.ru', '1234567', 400, "Validation failed", {'Login': ['Short']}),
        ('ivan', 'test_mail.ru', '1234567', 400, "Validation failed", {'Email': ['Invalid']}),
        ('ivan', 'test@mail.ru', '123', 400, "Validation failed", {'Password': ['Short']}),
    ]
)
def test_post_v1_account_bad_parameters(
        account_helper,
        login,
        email,
        password,
        expected_code,
        expected_message,
        errors_details,

):
    with check_status_code_http(expexted_code=expected_code, expected_message=expected_message, errors_details=errors_details):
        login = login
        password = password
        email = email
        account_helper.register_new_user(login=login, password=password, email=email)
        account_helper.user_login(login=login, password=password, return_model=True)
