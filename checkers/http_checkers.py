import requests
from requests.exceptions import HTTPError
from contextlib import contextmanager


@contextmanager
def check_status_code_http(
        expexted_code: requests.codes = requests.codes.OK,
        expected_message: str = "",
        errors_details: dict = None
        ):
    try:
        yield
        if expexted_code != requests.codes.OK:
            raise AssertionError(f'Ожидаемый статус должен быть равен {expexted_code}')
        if expected_message:
            raise AssertionError(f'Ожидалось сообщение "{expected_message}", но тест завершился без ошибок')
    except HTTPError as e:
        assert e.response.status_code == expexted_code
        assert e.response.json()['title'] == expected_message
        if errors_details:
            for key, value in errors_details.items():
                assert e.response.json()['errors'][key] == value
