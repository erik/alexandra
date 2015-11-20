import json
import logging

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, abort

import alexandra.util as util


log = logging.getLogger(__name__)


class WsgiApp:
    """This class is compatible with Werkzeug's WSGI implementation and
    handles all the gory details of parsing Alexa requests and validating that
    they were actually sent by Amazon.
    """

    def __init__(self, alexa, validate_requests=True):
        """
        :param alexa: alexandra.app.App to wrap
        :param validate_requests: Whether or not to do timestamp and
            certificate validation.
        """

        self.alexa = alexa
        self.validate = validate_requests

    @Request.application
    def __call__(self, request):
        return self.wsgi_app(request)

    def wsgi_app(self, request):
        """Validates and routes WSGI requests."""

        try:
            if request.method != 'POST':
                abort(400)

            try:
                body = json.loads(request.data)
            except ValueError:
                abort(400)

            if self.validate:
                valid_cert = util.validate_request_certificate(request)
                valid_ts = util.validate_request_timestamp(body)

                if not valid_cert or not valid_ts:
                    log.error('failed to validate request')
                    abort(403)

            resp_obj = self.alexa.dispatch_request(body)
            return Response(response=json.dumps(resp_obj, indent=4),
                            status=200,
                            mimetype='application/json')

        except HTTPException, exc:
            return exc
