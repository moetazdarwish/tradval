from rest_framework.throttling import UserRateThrottle
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):  # check that a Throttled exception is raised
        custom_response_data = {  # prepare custom response data
            'message': 'You limit exceeded search per hour , try again after 60 minutes',

        }
        response.data = custom_response_data  # set the custom response data on response object

    return response


class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'


class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'
