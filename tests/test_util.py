from alexandra import util


class TestRespond:
    '''alexandra.util.respond'''

    def test_sanity(self):
        resp = util.respond()

        assert resp == {
            'version': '1.0',
            'shouldEndSession': True,
            'response': {
                'outputSpeech': {'type': 'PlainText', 'text': ''}
            },
            'sessionAttributes': {}
        }

    def test_output_format(self):
        resp = util.respond(text='foobar')
        assert resp['response'] == {
            'outputSpeech': {'type': 'PlainText', 'text': 'foobar'}
        }

        resp = util.respond(ssml='foobar')
        assert resp['response'] == {
            'outputSpeech': {'type': 'SSML', 'ssml': 'foobar'}
        }

    def test_reprompt(self):
        resp = util.respond(reprompt_text='foobar')
        assert resp['response']['reprompt'] == {
            'outputSpeech': {'type': 'PlainText', 'text': 'foobar'}
        }

        resp = util.respond(reprompt_ssml='foobar')
        assert resp['response']['reprompt'] == {
            'outputSpeech': {'type': 'SSML', 'ssml': 'foobar'}
        }

    def test_argument_mashup(self):
        resp = util.respond(text='foo', reprompt_ssml='bar',
                            attributes={'a': 'b'}, end_session=False)

        assert resp == {
            'version': '1.0',
            'shouldEndSession': False,
            'response': {
                'outputSpeech': {'type': 'PlainText', 'text': 'foo'},
                'reprompt': {
                    'outputSpeech': {'type': 'SSML', 'ssml': 'bar'}
                }
            },
            'sessionAttributes': {'a': 'b'}
        }


class TestReprompt:
    '''alexandra.util.reprompt'''

    def test_reprompt_sanity(self):
        assert util.reprompt(text='foo') == util.respond(reprompt_text='foo', end_session=False)
        assert util.reprompt(ssml='foo') == util.respond(reprompt_ssml='foo', end_session=False)


class TestValidateTimestamp:
    '''alexandra.util.validate_request_timestamp'''
    pass


class TestValidateCertificate:
    '''alexandra.util.validate_request_certificate'''
    pass
