from rest_framework import status
from rest_framework.exceptions import APIException


class WrongAmountError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Wrong amount'


class WrongDateFormatError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Wrong date format'
