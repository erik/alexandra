try:
    from cStringIO import StringIO
except:
    from io import StringIO

import datetime as dt
import logging

import pytest

from alexandra import util


class TestRespond:
    '''alexandra.util.respond'''

    def test_sanity(self):
        resp = util.respond()

        assert resp == {
            'version': '1.0',
            'response': {
                'outputSpeech': {'type': 'PlainText', 'text': ''},
                'shouldEndSession': True
            },
            'sessionAttributes': {}
        }

    def test_output_format(self):
        resp = util.respond(text='foobar')
        assert resp['response'] == {
            'outputSpeech': {'type': 'PlainText', 'text': 'foobar'},
            'shouldEndSession': True
        }

        resp = util.respond(ssml='foobar')
        assert resp['response'] == {
            'outputSpeech': {'type': 'SSML', 'ssml': 'foobar'},
            'shouldEndSession': True
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
            'response': {
                'outputSpeech': {'type': 'PlainText', 'text': 'foo'},
                'shouldEndSession': False,
                'reprompt': {
                    'outputSpeech': {'type': 'SSML', 'ssml': 'bar'}
                }
            },
            'sessionAttributes': {'a': 'b'}
        }


class TestReprompt:
    '''alexandra.util.reprompt'''

    def test_reprompt_sanity(self):
        assert util.reprompt(text='foo') == util.respond(reprompt_text='foo', end_session=False)  # noqa
        assert util.reprompt(ssml='foo') == util.respond(reprompt_ssml='foo', end_session=False)  # noqa


class TestValidateTimestamp:
    '''alexandra.util.validate_request_timestamp'''

    def setup_class(self):
        self.log = StringIO()
        self.logger = logging.StreamHandler(stream=self.log)

        logging.getLogger('alexandra').addHandler(self.logger)

    def teardown_class(self):
        logging.getLogger('alexandra').removeHandler(self.logger)

    def last_log(self):
        value = self.log.getvalue()
        self.log.truncate(0)
        self.log.seek(0)

        return value

    def test_missing_timestamp(self):
        assert util.validate_request_timestamp({}) is False
        assert self.last_log() == 'timestamp not present {}\n'

    def test_expired_timestamp(self):
        future = dt.datetime.utcnow() + dt.timedelta(hours=3)
        past = dt.datetime.utcnow() - dt.timedelta(hours=3)

        assert util.validate_request_timestamp({
            'request': {'timestamp': future.strftime('%Y-%m-%dT%H:%M:%SZ')}
        }) is False

        assert 'timestamp difference too high' in self.last_log()

        assert util.validate_request_timestamp({
            'request': {'timestamp': past.strftime('%Y-%m-%dT%H:%M:%SZ')}
        }) is False

        assert 'timestamp difference too high' in self.last_log()

    def test_good_timestamp(self):
        now = dt.datetime.utcnow()

        assert util.validate_request_timestamp({
            'request': {'timestamp': now.strftime('%Y-%m-%dT%H:%M:%SZ')}
        }) is True


class TestValidateCertificate:
    '''alexandra.util.validate_request_certificate'''

    def setup_class(self):
        self.log = StringIO()
        self.logger = logging.StreamHandler(stream=self.log)

        logging.getLogger('alexandra').addHandler(self.logger)

    def teardown_class(self):
        self.log.close()
        logging.getLogger('alexandra').removeHandler(self.logger)

    def last_log(self):
        value = self.log.getvalue()
        self.log.truncate(0)
        self.log.seek(0)

        return value

    def test_bogus_urls(self):
        '''explicitly given by amazon docs as failure cases'''

        cases = [
            'http://s3.amazonaws.com/echo.api/echo-api-cert.pem',
            'https://notamazon.com/echo.api/echo-api-cert.pem',
            'https://s3.amazonaws.com/EcHo.aPi/echo-api-cert.pem',
            'https://s3.amazonaws.com/invalid.path/echo-api-cert.pem',
            'https://s3.amazonaws.com:563/echo.api/echo-api-cert.pem',
            'https://s3.amazonaws.com:443/echo.api/../echo-api-cert.pem',
        ]

        for case in cases:
            assert util._get_certificate(case) is None
            assert self.last_log() == 'invalid cert location %s\n' % case

    def test_good_url_expired_cert(self):
        '''correctly formatted url, but certificate expired'''

        cases = [
            'https://s3.amazonaws.com/echo.api/echo-api-cert.pem',
            'https://s3.amazonaws.com:443/echo.api/echo-api-cert.pem',
        ]

        for case in cases:
            assert util._get_certificate(case) is None
            assert self.last_log() == 'certificate expired or invalid\n'

    @pytest.mark.skip
    def test_request_validation(self):
        '''This test is disabled due to echo-api-cert-4 having expired.'''
        cert_url = 'https://s3.amazonaws.com/echo.api/echo-api-cert-4.pem'
        sig = 'biCfiVPY/AfFHPLz3s6msyoSWewJzQo0jZxsrSelEvVw1RlZ9ehxoREB/iUK+PD2rzO+z1SdP3RlOabMf6eHCvkG1G3SJY13Q00lVbmabJVOcNGObvxuWHD0oUtdfPKSzcUok2cEiAiMtI+OkXNoCkji4kxHPx1+nvfPhNhoakALCLqEYNYTm3ifNt5WbfYe8TC+5U86+U8Bv/Xl5jaUDT9CzCjR0KEqI1Sw1tWrTGZt857Zzx0ZkF3jdD8Ljdet2d64pzkyX+Ig/91PQQt4VEvfbGcjDc32Ic3RjMTCW5amd22Bs0uWLdzn8luOh6wg2WvVbE2ME8FsvUVCEtCCSQ=='
        headers = {'SignatureCertChainUrl': cert_url, 'Signature': sig}

        # Valid data
        data =  b'{"version":"1.0","session":{"new":true,"sessionId":"SessionId.a5a7c87a-4274-45bc-ac16-fb1bc02b93e4","application":{"applicationId":"amzn1.ask.skill.d4ed8492-e5ca-47f7-86d2-103d6a918c00"},"attributes":{},"user":{"userId":"amzn1.ask.account.AHVZCEBJIIIE32N24P522JWAJBM4W2CWOZVP5R74WC6LBMHQG4NPDV4CXCHV5FONOGH3WMOUYN7QWB5BIEYR26RT3VBZIRWF77ZEQZT2E23CSAYHCFWYH4NUSD7R522J2C6TCWOEFSHXTHTN3J77Z5KNEC4IHNXBJZGZELWKI5YR4KIDEXQZDOTLTK4WDREGVGVAQK73734BCYA"}},"request":{"type":"LaunchRequest","requestId":"EdwRequestId.5399ce92-0424-4dd4-b434-40213b4cd2c9","timestamp":"2016-12-28T05:59:13Z","locale":"en-US"}}'
        assert util.validate_request_certificate(headers, data) is True

        # Invalid data (timestamp altered by 1 second)
        data =  b'{"version":"1.0","session":{"new":true,"sessionId":"SessionId.a5a7c87a-4274-45bc-ac16-fb1bc02b93e4","application":{"applicationId":"amzn1.ask.skill.d4ed8492-e5ca-47f7-86d2-103d6a918c00"},"attributes":{},"user":{"userId":"amzn1.ask.account.AHVZCEBJIIIE32N24P522JWAJBM4W2CWOZVP5R74WC6LBMHQG4NPDV4CXCHV5FONOGH3WMOUYN7QWB5BIEYR26RT3VBZIRWF77ZEQZT2E23CSAYHCFWYH4NUSD7R522J2C6TCWOEFSHXTHTN3J77Z5KNEC4IHNXBJZGZELWKI5YR4KIDEXQZDOTLTK4WDREGVGVAQK73734BCYA"}},"request":{"type":"LaunchRequest","requestId":"EdwRequestId.5399ce92-0424-4dd4-b434-40213b4cd2c9","timestamp":"2016-12-28T05:59:14Z","locale":"en-US"}}'
        assert util.validate_request_certificate(headers, data) is False
        assert self.last_log() == 'invalid request signature\n'
