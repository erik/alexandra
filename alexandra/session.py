import json


class Session:
    """Provides easier access to session objects sent along with requests.

    The object parsed from the request can be accessed directly
    through the :py:attr:`body` member.
    """

    def __init__(self, session_body):
        self.body = session_body

    def __repr__(self):
        return '<Session %s>' % json.dumps(self.body)

    @property
    def is_new(self):
        """Is this a new session or a previously open one?"""
        return self.body['new']

    @property
    def session_id(self):
        return self.body['sessionId']

    @property
    def application_id(self):
        return self.body['application']['applicationId']

    @property
    def user_id(self):
        return self.body['user'].get('userId')

    @property
    def user_access_token(self):
        return self.body['user'].get('accessToken')

    def get(self, attr, default=None):
        """Get an attribute defined by this session"""

        attrs = self.body.get('attributes') or {}
        return attrs.get(attr, default)
