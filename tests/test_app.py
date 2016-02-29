import pytest

from alexandra import util
from alexandra.app import Application


def _request(req_type, session=None):
    return {
        'request': {
            'type': req_type,
        },
        'session': session
    }


def _intent(name, slots=None, session=None):
    req = _request('IntentRequest', session)

    req['request']['intent'] = {
        'name': name,
        'slots': {
            k: {'name': k, 'value': v}
            for k, v in (slots or {}).items()
        }
    }

    return req


def test_sanity():
    '''If this fails the sky is falling.'''
    app = Application()

    assert app.dispatch_request(_request('LaunchRequest')) == app.launch_fn(None)
    assert app.dispatch_request(_intent('Foo')) == app.unknown_intent_fn(None, None)
    assert app.dispatch_request(_request('SessionEndedRequest')) == app.session_end_fn()


def test_launch_request():
    app = Application()

    @app.launch
    def launch(sesh):
        assert sesh.get('fizz') == 'buzz'
        return 123

    sesh = {'attributes': {'fizz': 'buzz'}}
    assert app.dispatch_request(_request('LaunchRequest', sesh)) == 123

    @app.launch
    def launch_no_session(sesh):
        assert sesh is None
        return 456

    assert app.dispatch_request(_request('LaunchRequest')) == 456


def test_intent_noargs():
    app = Application()

    slots = {'fizz': 'buzz', 'ab': 'cd'}
    session = {'attributes': {'foo': 'bar'}}

    @app.intent('Foo')
    def foo():
        return 'foo'

    @app.intent('Bar')
    def bar():
        return 'bar'

    assert app.dispatch_request(_intent('Foo')) == 'foo'
    assert app.dispatch_request(_intent('Foo', slots, session)) == 'foo'
    assert app.dispatch_request(_intent('Bar')) == 'bar'


def test_intent_withargs():
    app = Application()

    @app.intent('Foo')
    def foo(slots, session):
        assert slots.get('fizz') == 'buzz'
        assert session.get('foo') == 'bar'

        return 'foo'

    slots = {'fizz': 'buzz', 'ab': 'cd'}
    session = {'attributes': {'foo': 'bar'}}

    assert app.dispatch_request(_intent('Foo', slots, session)) == 'foo'


def test_intent_badargs():
    app = Application()

    with pytest.raises(ValueError):
        @app.intent('Foo')
        def bad_intent_handler(a, b, c, d, e, f):
            pass


def test_unknown_request_type():
    with pytest.raises(ValueError):
        Application().dispatch_request(_request(req_type='something bad'))


def test_unknown_intent_handler():
    app = Application()

    @app.unknown_intent
    def unknown_handler_no_args():
        return 'foo'

    assert app.dispatch_request(_intent('What?')) == 'foo'

    @app.unknown_intent
    def unknown_handler_with_args(slots, session):
        assert slots.get('fizz') == 'buzz'
        assert session.get('foo') == 'bar'

        return 'bar'

    slots = {'fizz': 'buzz', 'ab': 'cd'}
    session = {'attributes': {'foo': 'bar'}}

    assert app.dispatch_request(_intent('What?', slots, session)) == 'bar'
