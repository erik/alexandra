import json


class Session:
    """Provides easier access to session objects sent along with requests"""

    def __init__(self, session_obj):
        self.obj = session_obj

    def __repr__(self):
        return '<Session %s>' % json.dumps(self.obj)

    @property
    def is_new(self):
        """Is this a new session or a previously open one?"""
        return self.obj['new']

    @property
    def session_id(self):
        return self.obj['sessionId']

    @property
    def application_id(self):
        return self.obj['application']['applicationId']

    @property
    def user_id(self):
        return self.obj['user'].get('userId')

    @property
    def user_access_token(self):
        return self.obj['user'].get('accessToken')

    def get(self, attr, default=None):
        """Get an attribute defined by this session"""

        attrs = self.obj.get('attributes') or {}
        return attrs.get(attr, default)
