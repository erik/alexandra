# coding: utf-8

from alexandra import Session


SESSION_BODY = {
    'new': False,
    'sessionId': 'session_id',
    'attributes': {
        'fizz': 'buzz',
        'foo': 'bar'
    },
    'application': {
        'applicationId': 'application_id'
    },

    'user': {
        'userId': 'user_id',
        'accessToken': 'access_token'
    }
}


class TestSession:
    '''alexandra.session.Session.

    stupid simple class, stupid simple tests.'''

    def setup_class(self):
        self.session = Session(SESSION_BODY)

    def test_sanity(self):
        assert self.session.is_new is False
        assert self.session.session_id == 'session_id'
        assert self.session.application_id == 'application_id'
        assert self.session.user_id == 'user_id'
        assert self.session.user_access_token == 'access_token'
        assert self.session.get('foo') == 'bar'
        assert self.session.get('not present', 'default') == 'default'

        assert self.session.body is SESSION_BODY
