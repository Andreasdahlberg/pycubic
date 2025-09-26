"""
Pycubic - A Python wrapper for the LK Systems CubicSecure API.

This package provides an async Python interface to interact with LK Systems
CubicSecure API for controlling water valves and accessing device information.
"""

__version__ = '0.1.0'
__author__ = 'Andreas Dahlberg'
__email__ = 'andreas.dahlberg90@gmail.com'

from .auth import AuthClient
from .user import UserClient
from .cubic_access import CubicAccessClient
from .cubic import CubicClient

__all__ = ['AuthClient', 'UserClient', 'CubicAccessClient', 'CubicClient']
