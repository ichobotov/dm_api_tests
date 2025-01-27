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


class GetV1Account:
    @classmethod
    def check_response_values_for_auth_user(
            cls,
            response
    ):
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

    @classmethod
    def check_response_values_for_not_auth_user(
            cls,
            response
            ):
        assert_that(response, has_property('resource', equal_to(None)))
