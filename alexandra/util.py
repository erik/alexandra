"""Utility functionality for Alexandra"""

import base64
import os.path
import urlparse
import urllib2

from datetime import datetime

from OpenSSL import crypto


# We don't want to check the certificate every single time. Store for
# as long as they are valid.
_cache = {}


def respond(text=None, ssml=None, session_attrs=None, reprompt_text=None,
            reprompt_ssml=None, end_session=True):
    """ Build a dict containing a valid response to an Alexa request.

    If speech output is desired, either of `text` or `ssml` should
    be specified.

    :param text: Plain text speech output to be said by Alexa device.
    :param ssml: Speech output in SSML form.
    :param session: Dict containing key, value pairs to attach to
        user's session.
    :param end_session: Should the session be terminated after this response?
    :param reprompt_text, reprompt_ssml: Works the same as
        `text`/`ssml`, but instead sets the reprompting speech output.
    """

    obj = {
        'version': '1.0',
        'shouldEndSession': end_session,
        'response': {}
    }

    output = {}
    if text:
        output = {'type': 'PlainText', 'text': text}
    elif ssml:
        output = {'type': 'SSML', 'ssml': ssml}

    obj['response']['outputSpeech'] = output

    reprompt_output = None
    if reprompt_text:
        reprompt_output = {'type': 'PlainText', 'text': reprompt_text}
    elif reprompt_ssml:
        reprompt_output = {'type': 'SSML', 'ssml': reprompt_ssml}

    if reprompt_output:
        obj['response']['reprompt'] = {'outputSpeech': reprompt_output}

    if session_attrs is not None:
        obj['sessionAttributes'] = session_attrs

    return obj


def validate_request_timestamp(body):
    """Ensure the request's timestamp doesn't fall outside of the
    app's specified tolerance.
    """

    time_str = body.get('request', {}).get('timestamp')

    if not time_str:
        return False

    req_ts = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
    diff = (datetime.utcnow() - req_ts).total_seconds()

    if abs(diff) > 150:
        return False

    return True


def validate_request_certificate(request):
    """Ensure that the certificate and signature specified in the
    request headers are truely from Amazon and correctly verify.
    """

    # Make sure we have the appropriate headers.
    if 'SignatureCertChainUrl' not in request.headers or \
       'Signature' not in request.headers:
        return False

    cert_url = request.headers['SignatureCertChainUrl']
    sig = base64.b64decode(request.headers['Signature'])

    cert = _get_certificate(cert_url)

    if not cert:
        return False

    try:
        # ... wtf kind of API decision is this
        crypto.verify(cert, sig, request.data, 'sha1')
        return True
    except:
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

    url = urlparse.urlparse(cert_url)
    host = url.netloc.lower()
    path = os.path.normpath(url.path)

    # Sanity check location so we don't get some random person's cert.
    if url.scheme != 'https' or \
       host not in ['s3.amazonaws.com', 's3.amazonaws.com:443'] or \
       not path.startswith('/echo.api/'):
        return

    resp = urllib2.urlopen(cert_url)
    if resp.getcode() != 200:
        return

    cert = crypto.load_certificate(crypto.FILETYPE_PEM, resp.read())

    if cert.has_expired() or cert.get_subject().CN != 'echo-api.amazon.com':
        return

    _cache[cert_url] = cert
    return cert
