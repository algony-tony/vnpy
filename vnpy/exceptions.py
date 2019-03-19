# -*- coding: utf-8 -*-

class VnpyException(Exception):
    """
    Base class for all vnpy's errors.
    Each custom exception should be derived from this class
    """
    status_code = 500


class VnpyBadRequest(VnpyException):
    """Raise when the application or server cannot handle the request"""
    status_code = 400


class VnpyNotFoundException(VnpyException):
    """Raise when the requested object/resource is not available in the system"""
    status_code = 404

