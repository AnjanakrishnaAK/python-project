from rest_framework.exceptions import APIException

class BusinessLogicError(APIException):
    status_code = 400
    default_detail = "Business rule violation"
    default_code = "business_error"
    