from datetime import datetime

from hamcrest import (
    assert_that,
    has_property,
    all_of,
    instance_of,
    has_properties,
    equal_to,
    contains_inanyorder,
)


def test_get_v1_account_auth(
        auth_account_helper
    ):
    response = auth_account_helper.dm_api_account.account_api.get_v1_account()
    assert_that(
        response, all_of(
            has_property(
                'resource', has_properties(
                    'login', equal_to("ivan_65"),
                    'online', instance_of(datetime),
                    'rating', has_properties(
                        'enabled', equal_to(True),
                        'quality', equal_to(0),
                        'quantity', equal_to(0)
                    ),
                    'registration', instance_of(datetime),
                    'roles', contains_inanyorder("Guest", "Player"),
                )

            )

        )
    )



def test_get_v1_account_no_auth(
        account_helper
    ):
    response = account_helper.dm_api_account.account_api.get_v1_account()
    assert_that(response,has_property('resource', equal_to(None)))

