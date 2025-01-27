from datetime import datetime

from hamcrest import (
    assert_that,
    has_property,
    starts_with,
    all_of,
    instance_of,
    has_properties,
    equal_to,
    only_contains
)


class PostV1Account:

    @classmethod
    def check_response_values(
            cls,
            response,
            login
    ):
        today = datetime.now().strftime("%Y-%m-%d")
        assert_that(str(response.resource.registration), starts_with(today))
        # noinspection PyTypeChecker
        assert_that(
            response, all_of
                (
                    has_property('resource', has_property('login', starts_with(login))),
                    has_property('resource', has_property('registration', instance_of(datetime))),
                    has_property(
                        'resource', has_property(
                            'rating', has_properties(
                                'enabled', equal_to(True),
                                "quality", equal_to(0),
                                "quantity", equal_to(0)
                            )
                        )
                    )
                )
        )
