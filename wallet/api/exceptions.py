from rest_framework.exceptions import APIException
from rest_framework import status


class WrongAmountError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Wrong amount'


class WrongDateFormatError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Wrong date format'
