import json
import logging

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, abort

import alexandra.util as util


log = logging.getLogger(__name__)


class WsgiApp:
    """This class is wraps :py:obj:`alexandra.app.Application` object and
    handles all the gory details of parsing Alexa requests and validating that
    they were actually sent by Amazon.

    This class implements the WSGI interface, so an instance of can be passed
    to standard WSGI servers (uWSGI, gunicorn, ...)
    """

    def __init__(self, alexa, validate_requests=True):
        """
        :param alexa: alexandra.app.App to wrap
        :param validate_requests: Whether or not to do timestamp and
            certificate validation.
        """

        self.alexa = alexa
        self.validate = validate_requests

    # The Request.application decorator handles some boring parts of making
    # this work with WSGI
    @Request.application
    def __call__(self, request):
        return self.wsgi_app(request)

    def wsgi_app(self, request):
        """Incoming request handler.

        :param request: Werkzeug request object
        """

        try:
            if request.method != 'POST':
                abort(400)

            try:
                # Python 2.7 compatibility
                data = request.data
                if isinstance(data, str):
                    body = json.loads(data)
                else:
                    body = json.loads(data.decode('utf-8'))
            except ValueError:
                abort(400)

            if self.validate:
                valid_cert = util.validate_request_certificate(
                    request.headers, request.data)

                valid_ts = util.validate_request_timestamp(body)

                if not valid_cert or not valid_ts:
                    log.error('failed to validate request')
                    abort(403)

            resp_obj = self.alexa.dispatch_request(body)
            return Response(response=json.dumps(resp_obj, indent=4),
                            status=200,
                            mimetype='application/json')

        except HTTPException as exc:
            log.exception('Failed to handle request')
            return exc
