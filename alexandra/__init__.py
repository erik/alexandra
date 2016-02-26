# flake8: noqa
"""
Python support for Alexa applications.

Because like everything Amazon it involves a ton of tedious boilerplate.
"""

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())


from alexandra.app import Application
from alexandra.session import Session
from alexandra.util import respond, reprompt
