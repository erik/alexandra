"""Utility functionality for Alexandra"""

import base64
import logging
import os.path

try:
    from urlparse import urlparse
    from urllib2 import urlopen
except:
    from urllib.parse import urlparse
    from urllib.request import urlopen

from datetime import datetime

from OpenSSL import crypto


# We don't want to check the certificate every single time. Store for
# as long as they are valid.
_cache = {}
log = logging.getLogger(__name__)


def respond(text=None, ssml=None, attributes=None, reprompt_text=None,
            reprompt_ssml=None, end_session=True):
    """ Build a dict containing a valid response to an Alexa request.

    If speech output is desired, either of `text` or `ssml` should
    be specified.

    :param text: Plain text speech output to be said by Alexa device.
    :param ssml: Speech output in SSML form.
    :param attributes: Dictionary of attributes to store in the session.
    :param end_session: Should the session be terminated after this response?
    :param reprompt_text, reprompt_ssml: Works the same as
        `text`/`ssml`, but instead sets the reprompting speech output.
    """

    obj = {
        'version': '1.0',
        'response': {
            'outputSpeech': {'type': 'PlainText', 'text': ''},
            'shouldEndSession': end_session
        },
        'sessionAttributes': attributes or {}
    }

    if text:
        obj['response']['outputSpeech'] = {'type': 'PlainText', 'text': text}
    elif ssml:
        obj['response']['outputSpeech'] = {'type': 'SSML', 'ssml': ssml}

    reprompt_output = None
    if reprompt_text:
        reprompt_output = {'type': 'PlainText', 'text': reprompt_text}
    elif reprompt_ssml:
        reprompt_output = {'type': 'SSML', 'ssml': reprompt_ssml}

    if reprompt_output:
        obj['response']['reprompt'] = {'outputSpeech': reprompt_output}

    return obj


def reprompt(text=None, ssml=None, attributes=None):
    """Convenience method to save a little bit of typing for the common case of
    reprompting the user. Simply calls :py:func:`alexandra.util.respond` with
    the given arguments and holds the session open.

    One of either the `text` or `ssml` should be provided if any
    speech output is desired.

    :param text: Plain text speech output
    :param ssml: Speech output in SSML format
    :param attributes: Dictionary of attributes to store in the current session
    """

    return respond(
        reprompt_text=text,
        reprompt_ssml=ssml,
        attributes=attributes,
        end_session=False
    )


def validate_request_timestamp(req_body, max_diff=150):
    """Ensure the request's timestamp doesn't fall outside of the
    app's specified tolerance.

    Returns True if this request is valid, False otherwise.

    :param req_body: JSON object parsed out of the raw POST data of a request.
    :param max_diff: Maximum allowable difference in seconds between request
        timestamp and system clock. Amazon requires <= 150 seconds for
        published skills.
    """

    time_str = req_body.get('request', {}).get('timestamp')

    if not time_str:
        log.error('timestamp not present %s', req_body)
        return False

    req_ts = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
    diff = (datetime.utcnow() - req_ts).total_seconds()

    if abs(diff) > max_diff:
        log.error('timestamp difference too high: %d sec', diff)
        return False

    return True


def validate_request_certificate(headers, data):
    """Ensure that the certificate and signature specified in the
    request headers are truely from Amazon and correctly verify.

    Returns True if certificate verification succeeds, False otherwise.

    :param headers: Dictionary (or sufficiently dictionary-like) map of request
        headers.
    :param data: Raw POST data attached to this request.
    """

    # Make sure we have the appropriate headers.
    if 'SignatureCertChainUrl' not in headers or \
       'Signature' not in headers:
        log.error('invalid request headers')
        return False

    cert_url = headers['SignatureCertChainUrl']
    sig = base64.b64decode(headers['Signature'])

    cert = _get_certificate(cert_url)

    if not cert:
        return False

    try:
        # ... wtf kind of API decision is this
        crypto.verify(cert, sig, data, 'sha1')
        return True
    except:
        log.error('invalid request signature')
        return False


def _get_certificate(cert_url):
    """Download and validate a specified Amazon PEM file."""
    global _cache

    if cert_url in _cache:
        cert = _cache[cert_url]
        if cert.has_expired():
            _cache = {}
        else:
            return cert

    url = urlparse(cert_url)
    host = url.netloc.lower()
    path = os.path.normpath(url.path)

    # Sanity check location so we don't get some random person's cert.
    if url.scheme != 'https' or \
       host not in ['s3.amazonaws.com', 's3.amazonaws.com:443'] or \
       not path.startswith('/echo.api/'):
        log.error('invalid cert location %s', cert_url)
        return

    resp = urlopen(cert_url)
    if resp.getcode() != 200:
        log.error('failed to download certificate')
        return

    cert = crypto.load_certificate(crypto.FILETYPE_PEM, resp.read())

    if cert.has_expired() or cert.get_subject().CN != 'echo-api.amazon.com':
        log.error('certificate expired or invalid')
        return

    _cache[cert_url] = cert
    return cert
